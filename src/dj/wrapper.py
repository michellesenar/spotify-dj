import csv
import os
from typing import Any, Dict, List

import spotipy
from dotenv import load_dotenv

import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

from .data import Artist, Album, AudioFeatures, Track, TrackAnalysis
from .logging import get_logger

load_dotenv()

scope = 'user-library-read playlist-modify-public playlist-modify-private'
spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

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


def add_to_playlist_from_csv(username: str, playlist_id: str, csv_name: str):

    def _track_name(x):
        return f"{x['name']}__{x['artists'][0]['name']}"

    user_id = os.getenv(username)
    playlist_name = spotify.playlist(playlist_id)['name']
    existing_track_uris = [x['track']['uri'] for x in spotify.playlist_tracks(playlist_id)['items']]
    existing_track_names = [_track_name(x['track']) for x in spotify.playlist_tracks(playlist_id)['items']]
    new_track_uris = []
    logger.debug("Adding to %s's playlist '%s' from '%s'", username, playlist_name, csv_name)

    def _batch(seq, size):
        return [
            seq[i:i + size]
            for i in range(0, len(seq), size)
        ]

    with open(csv_name, "r") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            new_track_uri = row["track_uri"]
            new_track_name = f"{row['track_name']}__{row['artist_name']}"
            new_track_uris.append((new_track_uri, new_track_name))

    for batch in _batch(new_track_uris, 10):
        actual_new_uris = set([x[0] for x in batch]).difference(set(existing_track_uris))
        actual_new_names = set([x[1] for x in batch]).difference(set(existing_track_names))
        if actual_new_uris and actual_new_names and (len(actual_new_uris) == len(actual_new_names)):
            spotify.user_playlist_add_tracks(user_id, playlist_id, actual_new_uris)

    logger.debug("Finished adding from %s", csv_name)
