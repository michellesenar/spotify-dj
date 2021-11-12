from typing import Any, Dict, List

from dj.wrapper.connection import spotify
from dj.wrapper.artist import build_artist
from dj.wrapper.track import build_track, build_track_analysis
from dj.data import TrackAnalysis, Artist


def recommend(artist_ids: List[str], genres: List[str], track_ids: List[str], limit: int = 20):
    return spotify.recommendations(
        seed_artists=artist_ids,
        seed_genres=genres,
        seed_tracks=track_ids,
        limit=limit,
    )


def build_recommended_tracklist(recs: Dict[str, Any]) -> tuple[List[TrackAnalysis], List[Artist]]:
    artists = []
    track_analyses = []

    for rec in recs["tracks"]:
        artist = build_artist(rec["artists"][0]["uri"])
        artists.append(artist)

        track = build_track(rec)
        track_analysis = build_track_analysis(track)
        track_analyses.append(track_analysis)

    return track_analyses, artists