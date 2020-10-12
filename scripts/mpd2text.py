import os
from pathlib import Path
from typing import Optional

import orjson
from argtyped import Arguments
from common.mpd_model import MPDSlice, Playlist
from common.utils import imap_progress
from loguru import logger
from torch.utils.data import random_split


class Args(Arguments):
    mpd_dir: str = str(Path("./data/nobackup/dataset/data"))
    start_slice: int = 0
    end_slice: Optional[int] = 1000
    output_dir: str = str(Path("./output/nobackup"))


def slice_start_from_filename(filename):
    return int(str(filename).split("-")[0].split(".")[-1])


def playlist2text(playlist: Playlist):
    line = "<BOS>"
    line += ' "' + playlist.name + '":'
    for track in playlist.tracks:
        line += ' "' + track.track_name + '"'
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


def main():
    args = Args()
    logger.debug(args.to_string())
    slice_files = [
        file
        for file in Path(args.mpd_dir).glob("mpd.slice.*.json")
        if args.start_slice * 1000
        <= slice_start_from_filename(file)
        < args.end_slice * 1000
    ]
    logger.debug(slice_files)
    os.makedirs(args.output_dir, exist_ok=True)

    results = imap_progress(read_lines, slice_files)
    lines = [l for slice_lines in results for l in slice_lines]

    with open(Path(args.output_dir) / "mpd.txt", "w") as f:
        f.writelines(lines)


if __name__ == "__main__":
    main()
