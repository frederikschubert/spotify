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
    album_name: Optional[str] = None
    album_uri: Optional[str] = None
    artist_name: Optional[str] = None
    artist_uri: Optional[str] = None
    duration_ms: Optional[str] = None
    pos: Optional[str] = None

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Track):
            return (
                o.track_uri == self.track_uri
                and o.album_uri == self.album_uri
                and o.artist_uri == self.artist_uri
            )
        return False

    def __hash__(self) -> int:
        return hash(self.track_uri)

    def __str__(self):
        return self.track_name


@dataclass
class Playlist(DataClassJsonMixin):
    pid: int
    tracks: List[Track]
    name: str = ""
    collaborative: bool = False
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
    playlists: List[Playlist]
    info: Optional[SliceInfo] = None