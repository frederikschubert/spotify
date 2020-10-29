# Submission for the Spotify Million Dataset Challenge

https://www.aicrowd.com/challenges/spotify-million-playlist-dataset-challenge

## Task

Given a seed playlist title and/or initial set of tracks in a playlist, predict the subsequent tracks in that playlist.

## Usage

```bash
# split tracks file into parts to speed up reading
cd output/nobackup
split -l 5000 -d --additional-suffix=.json tracks.json tracks
```
