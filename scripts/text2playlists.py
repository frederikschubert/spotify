from common.mpd_model import MPDSlice, Playlist
import orjson
from common.utils import imap_progress
from pathlib import Path

from argtyped import Arguments
from loguru import logger


class Args(Arguments):
    mpd_dir: str = str(Path("./data/nobackup/dataset/data"))
    text_dir: str


def read_tracks(file):
    tracks = set()
    with open(file, "r") as f:
        file_content = orjson.loads(f.read())
        s = MPDSlice.from_dict(file_content)

        for playlist in s.playlists:
            for track in playlist.tracks:
                tracks.add(track)
    return tracks


def main():
    args = Args()
    logger.debug(args.to_string())
    slice_files = [file for file in Path(args.mpd_dir).glob("mpd.slice.*.json")]
    results = imap_progress(read_tracks, slice_files)
    # TODO(frederik): combine all track sets
    # TODO(frederik): read text_dir files
    # TODO(frederik): look for nearest neighbors in the track set
    # TODO(frederik): write submission file


if __name__ == "__main__":
    main()
