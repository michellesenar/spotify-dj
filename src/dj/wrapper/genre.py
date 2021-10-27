from typing import List

from .connection import spotify
from dj.log_setup import get_logger
from dj.logging import log_track_characteristics
from dj.old_wrapper import get_artist_id, build_artist, build_track, build_track_analysis

logger = get_logger(__name__)


def list_genres():
    official_genres = spotify.recommendation_genre_seeds()["genres"]
    for g in official_genres:
        logger.debug("%s", g)
    return official_genres


def recommender(artist_uris: List[str], genres: List[str], limit : int = 20):
    return spotify.recommendations(
        seed_artists=artist_uris,
        seed_genres=genres,
        limit=limit,
    )


def recommend_from_official_genres(artists: List[str], genres: List[str]):
    if artists:
        artist_ids = [get_artist_id(x) for x in artists]
    else:
        artist_ids = []
    recs = recommender(artist_ids, genres)
    for rec in recs["tracks"]:
        artist = build_artist(rec['artists'][0]['uri'])
        track = build_track(rec)
        track_analysis = build_track_analysis(track)
        log_track_characteristics(artist, track_analysis)