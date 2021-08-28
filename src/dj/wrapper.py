import os
from typing import Any, Dict, List

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

from .data import Artist, AudioFeatures, Track, TrackAnalysis
from .logging import get_logger

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

client_credentials_manager = SpotifyClientCredentials(
    client_id=CLIENT_ID, client_secret=CLIENT_SECRET
)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

logger = get_logger(__name__)


def allowable_track(allow_explicit, track):
    return allow_explicit or not track.explicit


def get_top_tracks_per_artist(artist_uri: str, allow_explicit=False):
    artist = spotify.artist(artist_uri)
    top_tracks = spotify.artist_top_tracks(artist["id"])["tracks"]
    return build_preliminary_tracklist(top_tracks, allow_explicit)


def get_artist(uri: str) -> Artist:
    artist = spotify.artist(uri)
    logger.debug("===== Current Artist: %s", artist["name"])
    return Artist(name=artist["name"], id=artist["id"])


def get_related_artists(artist_id: str) -> List[Artist]:
    related = []
    for a in spotify.artist_related_artists(artist_id)["artists"]:
        relative = Artist(name=a["name"], id=a["id"])
        logger.debug("Related Arist: %s", relative.name)
        related.append(a)
    return related


def build_track(raw_track_info: Dict[str, Any]) -> Track:
    return Track(
        name=raw_track_info["name"],
        uri=raw_track_info["uri"],
        explicit=raw_track_info["explicit"],
    )


def build_track_analysis(track: Track) -> TrackAnalysis:
    analysis = AudioFeatures(**spotify.audio_features(track.uri)[0])
    return TrackAnalysis(track=track, analysis=analysis)


def build_preliminary_tracklist(
    spotify_tracks: List[Dict[str, Any]], allow_explicit=False
) -> List[TrackAnalysis]:
    analyses = []

    for t in spotify_tracks:
        track = build_track(t)
        if allowable_track(allow_explicit, track):
            track_analysis = build_track_analysis(track)
            logger.debug("---- Track Name: %s", track.name)
            logger.debug(
                "Explicit: %s. Tempo=%s", track.explicit, track_analysis.analysis.tempo
            )
            analyses.append(track_analysis)

    return analyses
