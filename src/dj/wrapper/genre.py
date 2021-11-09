from typing import List

from .connection import spotify
from dj.log_setup import get_logger
from dj.logging import log_track_characteristics
from .track import build_track, build_track_analysis
from .artist import build_artist, search_artist_id_by_name

logger = get_logger(__name__)


def list_genres():
    official_genres = spotify.recommendation_genre_seeds()["genres"]
    for g in official_genres:
        logger.info("%s", g)
    return official_genres


def recommender(artist_uris: List[str], genres: List[str], limit: int = 20):
    return spotify.recommendations(
        seed_artists=artist_uris,
        seed_genres=genres,
        limit=limit,
    )


def recommend_from_official_genres(artists: List[str], genres: List[str]):
    if artists:
        artist_ids = [search_artist_id_by_name(x) for x in artists]
    else:
        artist_ids = []
    recs = recommender(artist_ids, genres)
    track_analyses = []
    for rec in recs["tracks"]:
        artist = build_artist(rec["artists"][0]["uri"])
        track = build_track(rec)
        track_analysis = build_track_analysis(track)
        track_analyses.append(track_analysis)
        log_track_characteristics(artist, track_analysis)

    return track_analyses
