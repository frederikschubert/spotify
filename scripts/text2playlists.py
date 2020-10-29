from copy import deepcopy
from functools import partial
from itertools import zip_longest
from pathlib import Path
from typing import List
import os
import numpy as np
import orjson
from tqdm import tqdm
from common.mpd_model import MPDSlice, Playlist, Track
from common.utils import imap_progress
from loguru import logger
from tap.tap import Tap
from Levenshtein import distance
import multiprocessing as mp
from ctypes import c_wchar_p
from scripts.generate import generate


class Args(Tap):
    challenge_file: str = str(Path("./data/nobackup/challenge/challenge_set.json"))
    tracks_file: str = str(Path("./output/nobackup/"))
    output_file: str = str(Path("./output/nobackup/submission.csv"))
    checkpoint: str
    k: int = 50
    temperature: float = 2.0
    num_tracks: int = 50
    debug: bool = False


def read_challenge(file):
    with open(file, "r") as f:
        file_content = orjson.loads(f.read())
        s = MPDSlice.from_dict(file_content)
    return s.playlists


def write_submission(output_file: str, playlists: List[Playlist]):
    logger.info("Writing submission")
    with open(output_file, "w") as f:
        f.write("team_info, Frederik Schubert, info@frederik-schubert.de\n")
        for playlist in playlists:
            f.write(f"{playlist.pid}, ")
            f.write(", ".join([track.track_uri for track in playlist.tracks]))
            f.write("\n")


def find_real_tracks(generated_tracks: List[Track]) -> List[Track]:
    real_tracks = set()
    for g_track in generated_tracks:
        if not g_track or not g_track.track_name:
            continue
        min_distance = np.inf
        best_track_uri = None
        best_track_name = None
        for track_name, track_uri in zip(track_names, track_uris):
            dist = distance(g_track.track_name, track_name)
            if dist < min_distance:
                best_track_uri = track_uri
                best_track_name = track_name
                min_distance = dist
        if best_track_name and best_track_uri:
            real_tracks.add(Track(track_name=best_track_name, track_uri=best_track_uri))
    return list(real_tracks)


def read_tracks(track_file):
    tracks = []
    with open(track_file, "rb") as f:
        lines = f.readlines()
        for line in lines:
            tracks.append(Track.from_json(line))
            tracks[-1].track_name = "".join(tracks[-1].track_name.split(" "))
    return tracks


def grouper(n, iterable, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)


def init(names, uris):
    global track_names, track_uris
    track_names = names
    track_uris = uris


def imap_progress_args(f, iterable, args):
    with mp.Pool(processes=os.cpu_count(), initializer=init, initargs=args) as pool:
        results = []
        for result in tqdm(pool.imap_unordered(f, iterable), total=len(iterable)):
            results.append(result)
    return results


def main():
    args = Args().parse_args()
    slice_files = [args.challenge_file]
    logger.info("Reading Challenge playlists...")
    challenge_playlists_list: List[List[Playlist]] = imap_progress(
        read_challenge, slice_files
    )
    challenge_playlists = [
        playlist
        for playlist_list in challenge_playlists_list
        for playlist in playlist_list
    ]
    if not args.debug:
        logger.info("Reading tracks...")
        tracks_files = list(Path(args.tracks_file).glob("tracks*.json"))
        tracks_result: List[List[Track]] = imap_progress(read_tracks, tracks_files)
        tracks = [track for track_list in tracks_result for track in track_list]
        track_names = mp.Array(c_wchar_p, len(tracks), lock=False)
        track_uris = mp.Array(c_wchar_p, len(tracks), lock=False)
        for i, track in enumerate(tracks):
            track_names[i] = track.track_name
            track_uris[i] = track.track_uri
    else:
        tracks = []
        track_names = []
        track_uris = []
    playlist_name_length_probs = [0.4, 0.3, 0.2, 0.1]
    submission_playlists = []
    for playlist in challenge_playlists:
        logger.trace(playlist)
        submission_playlist = deepcopy(playlist)
        submission_playlist.tracks = []
        while len(submission_playlist.tracks) < 500:
            logger.info("Generating track candidates")
            generated_tracks = generate(
                playlist,
                checkpoint=args.checkpoint,
                k=args.k,
                temperature=args.temperature,
                num_tracks=args.num_tracks,
                playlist_name_length_probs=playlist_name_length_probs,
            )
            logger.trace(generated_tracks)
            logger.info("Matching tracks...")
            generated_tracks_groups = list(grouper(os.cpu_count() * 2, generated_tracks))
            matched_real_tracks = imap_progress_args(
                find_real_tracks,
                generated_tracks_groups,
                args=(
                    track_names,
                    track_uris,
                ),
            )
            submission_playlist.tracks.extend(
                list(
                    set(
                        [
                            track
                            for track_list in matched_real_tracks
                            for track in track_list
                            if track not in playlist.tracks
                        ]
                    )
                )
            )
            submission_playlist.tracks = submission_playlist.tracks[:500]
            logger.info(
                "Submission Playlist with {} tracks", len(submission_playlist.tracks)
            )
        submission_playlists.append(submission_playlist)

    write_submission(args.output_file, submission_playlists)


if __name__ == "__main__":
    main()
