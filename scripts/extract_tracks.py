from pathlib import Path
from scripts.mpd2text import read_slice_files
from typing import List, Optional, Set
import os
import orjson
from tap import Tap
from common.mpd_model import MPDSlice, Playlist, Track
from common.utils import imap_progress
from loguru import logger


class Args(Tap):
    mpd_dir: str = str(Path("./data/nobackup/dataset/data"))
    output_file: str = str(Path("./output/nobackup/tracks.json"))
    start_slice: int = 0
    end_slice: int = 1000


def read_tracks(file):
    tracks = set()
    with open(file, "r") as f:
        file_content = orjson.loads(f.read())
        s = MPDSlice.from_dict(file_content)

        for playlist in s.playlists:
            for track in playlist.tracks:
                track.album_name = None
                track.album_uri = None
                track.artist_name = None
                track.artist_uri = None
                track.duration_ms = None
                track.pos = None
                tracks.add(track)
    return tracks


def main():
    args = Args().parse_args()
    slice_files = read_slice_files(args.mpd_dir, args.start_slice, args.end_slice)
    results: List[Set[Track]] = imap_progress(read_tracks, slice_files)
    unique_tracks = set()
    for track_list in results:
        for track in track_list:
            unique_tracks.add(track)
    logger.info("Found {} unique tracks", len(unique_tracks))
    if os.path.exists(args.output_file):
        os.remove(args.output_file)
    with open(str(args.output_file), "wb") as f:
        for track in unique_tracks:
            f.write(orjson.dumps(track))
            f.write(b"\n")


if __name__ == "__main__":
    main()
