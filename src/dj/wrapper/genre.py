from typing import List

from .connection import spotify
from dj.log_setup import get_logger
from dj.logging import log_track_characteristics
from .recommender import build_recommended_tracklist, recommend
from .track import build_track, build_track_analysis
from .artist import build_artist, search_artist_id_by_name

logger = get_logger(__name__)


def list_genres():
    official_genres = spotify.recommendation_genre_seeds()["genres"]
    for g in official_genres:
        logger.info("%s", g)
    return official_genres


def recommend_from_official_genres(artists: List[str], genres: List[str]):
    if artists:
        artist_ids = [search_artist_id_by_name(x) for x in artists]
    else:
        artist_ids = []
    recs = recommend(artist_ids, genres, track_ids=None)
    track_analyses, _ = build_recommended_tracklist(recs)
    return track_analyses
