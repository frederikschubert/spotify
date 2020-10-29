import os
from pathlib import Path
from typing import Optional

import orjson
from tap.tap import Tap
from common.mpd_model import MPDSlice, Playlist
from common.utils import imap_progress
from loguru import logger
from torch.utils.data import random_split


class Args(Tap):
    mpd_dir: str = str(Path("./data/nobackup/dataset/data"))
    start_slice: int = 0
    end_slice: int = 1000
    output_dir: str = str(Path("./output/nobackup"))


def slice_start_from_filename(filename):
    return int(str(filename).split("-")[0].split(".")[-1])


def playlist2text(playlist: Playlist):
    line = "<BOS>"
    line += ' "' + playlist.name + '":'
    for track in playlist.tracks:
        line += ' "' + "".join(track.track_name.split(" ")) + '"'
    line += "<EOS>\n"
    return line


def read_lines(file):
    lines = []
    with open(file, "r") as f:
        file_content = orjson.loads(f.read())
        s = MPDSlice.from_dict(file_content)

        for playlist in s.playlists:
            line = playlist2text(playlist)
            lines.append(line)
    return lines


def read_slice_files(mpd_dir: str, start_slice: int, end_slice: int = 1000):
    return [
        file
        for file in Path(mpd_dir).glob("mpd.slice.*.json")
        if start_slice * 1000 <= slice_start_from_filename(file) <= end_slice * 1000
    ]


def main():
    args = Args().parse_args()
    slice_files = read_slice_files(args.mpd_dir, args.start_slice, args.end_slice)
    logger.trace(slice_files)
    os.makedirs(args.output_dir, exist_ok=True)

    results = imap_progress(read_lines, slice_files)
    lines = [l for slice_lines in results for l in slice_lines]

    with open(Path(args.output_dir) / "mpd.txt", "w") as f:
        f.writelines(lines)


if __name__ == "__main__":
    main()
