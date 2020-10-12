from typing import Optional, List
from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin


@dataclass
class SliceInfo(DataClassJsonMixin):
    slice: str
    version: str
    generated_on: str
    description: Optional[str] = None
    license: Optional[str] = None


@dataclass
class Track(DataClassJsonMixin):
    track_name: str
    track_uri: str
    album_name: str
    album_uri: str
    artist_name: str
    artist_uri: str
    duration_ms: int
    pos: int


@dataclass
class Playlist(DataClassJsonMixin):
    pid: int
    name: str
    collaborative: bool
    tracks: List[Track]
    description: Optional[str] = None
    modified_at: Optional[int] = None
    num_artists: Optional[int] = None
    num_albums: Optional[int] = None
    num_tracks: Optional[int] = None
    num_followers: Optional[int] = None
    num_edits: Optional[int] = None
    duration_ms: Optional[int] = None


@dataclass
class MPDSlice(DataClassJsonMixin):
    info: SliceInfo
    playlists: List[Playlist]