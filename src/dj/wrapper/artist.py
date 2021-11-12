from typing import List

from dj.data import Artist
from dj.log_setup import get_logger
from .connection import spotify
from .track import build_preliminary_tracklist
from .util import find, search

logger = get_logger(__name__)


def search_artist_id_by_name(query: str):
    s = search(query, "artist")
    return s["id"]


def find_an_artist_by_name(query: str):
    f = find(query, "artist")
    return f

def build_artist(uri: str) -> Artist:
    artist = spotify.artist(uri)
    logger.info("===== Current Artist: %s", artist["name"])
    return Artist(name=artist["name"], id=artist["id"], genres=artist["genres"])


def get_top_tracks_per_artist(artist_uri: str, allow_explicit=False):
    artist = spotify.artist(artist_uri)
    top_tracks = spotify.artist_top_tracks(artist["id"])["tracks"]
    return build_preliminary_tracklist(top_tracks, allow_explicit)


def get_related_artists(artist_id: str) -> List[Artist]:
    related = []
    for a in spotify.artist_related_artists(artist_id)["artists"]:
        relative = Artist(name=a["name"], id=a["id"], genres=a["genres"])
        logger.info("Related Arist: %s", relative.name)
        logger.debug("--- Genres: %s", relative.genres)
        related.append(a)
    return related
