import csv
import os
from typing import Any, Dict, List

import spotipy
from dotenv import load_dotenv

import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

from .data import Artist, Album, AudioFeatures, Track, TrackAnalysis
from .log_setup import get_logger

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


def build_artist(uri: str) -> Artist:
    artist = spotify.artist(uri)
    logger.debug("===== Current Artist: %s", artist["name"])
    return Artist(name=artist["name"], id=artist["id"], genres=artist["genres"])



def analysis_matches_criteria(analysis):
    return (
        #0.7 <= analysis.valence < 0.8 # previously 0.6; >0.8 is meditative
        analysis.valence >= 0.67
        and analysis.speechiness < 0.4
        and analysis.duration_ms > 40000 # swtiched from >= 120000
        #and analysis.mode == 1  # major key 1; minor key 0; not useful
        #and analysis.tempo >= 100 # bpm is all over the map
        #and analysis.instrumentalness >= 0.9 #makes almost no difference
    )


def get_all_tracks(artist: Artist, limit=None):
    track_infos = []
    albums = [
        Album(id=a["id"], name=a["name"], uri=a["uri"]) 
        for a in spotify.artist_albums(artist.id)["items"]
    ]

    if limit:
        album_list = albums[0:limit]
    else:
        album_list = albums

    for album in album_list:
        logger.debug("Collecting tracks from %s", album.name)
        for track_ in spotify.album_tracks(album.uri)["items"]:
            track = build_track(track_)
            track_analysis = build_track_analysis(track)
            if track_analysis:  # Deal with returned Nonetypes from Spotify
                track_infos.append(track_analysis)

    
    return track_infos


def get_related_artists(artist_id: str) -> List[Artist]:
    related = []
    for a in spotify.artist_related_artists(artist_id)["artists"]:
        relative = Artist(name=a["name"], id=a["id"], genres=a["genres"])
        logger.debug("Related Arist: %s", relative.name) 
        logger.debug("--- Genres: %s", relative.genres)
        related.append(a)
    return related


def build_track(raw_track_info: Dict[str, Any]) -> Track:
    return Track(
        name=raw_track_info["name"],
        uri=raw_track_info["uri"],
        explicit=raw_track_info["explicit"],
    )


def build_track_analysis(track: Track) -> TrackAnalysis:
    if features := spotify.audio_features(track.uri):
        if features[0]:  # sometimes Spotify returns None
            analysis = AudioFeatures(**features[0])
            return TrackAnalysis(track=track, analysis=analysis)


# def log_track_info(artist_name, track_analysis):
#     track = track_analysis.track
#     analysis = track_analysis.analysis
#     logger.debug("'%s' by %s", track.name, artist_name)

#     logger.debug("p: %s", str(analysis))
#     minutes, seconds = divmod(analysis.duration_ms / 1000, 60)
#     logger.debug("")
#     logger.debug("'%s' by %s. Explicit = %s", track.name, artist_name, track.explicit)
#     logger.debug("--Track Duration: %d min %d sec", minutes, seconds)
#     logger.debug("---- %s BPM", analysis.tempo)



def build_preliminary_tracklist(
    spotify_tracks: List[Dict[str, Any]], allow_explicit=False
) -> List[TrackAnalysis]:
    analyses = []

    for t in spotify_tracks:
        track = build_track(t)
        track_analysis = build_track_analysis(track)
        logger.debug("---- Track Name: %s", track.name)
        analyses.append(track_analysis)

    return analyses


def genres():
    for g in spotify.recommendation_genre_seeds()["genres"]:
        logger.debug("%s", g)
    return genres


def recommender(artist_uris: List[str], genres: List[str], limit : int = 20):
    return spotify.recommendations(
        seed_artists=artist_uris,
        seed_genres=genres,
        limit=limit,
    )


def recommendations_from_genres(artists: List[str], genres: List[str]):
    from .matcher import log_track_characteristics
    if artists:
        artist_ids = [get_artist_id(x) for x in artists]
    else:
        artist_ids = []
    recs = recommender(artist_ids, genres)
    for rec in recs["tracks"]:
        artist = build_artist(rec['artists'][0]['uri'])
        track = build_track(rec)
        analysis = build_track_analysis(track).analysis
        log_track_characteristics(artist, track, analysis)


###### User PLAYLIST STUFF; doesn't really work
# def create_new_playlist(playlist_name: str):
#     spotify.user_playlist_create(create_new_playlist)


# def get_user_playlists(username: str):
#     user_id = os.getenv(username)
#     playlists = spotify.current_user_saved_tracks()
#     logger.debug("Playlist Count: %s", playlists["total"])
#     return playlists



# def get_user_playlist_id_from_playlist_name(playlist_name: str):
#     playlists = get_user_playlists(user)
#     for playlist in playlists["items"]:
#         if playlist["name"] == playlist_name:
#             breakpoint()


def get_artist_id(query: str):
    s = spotify.search(query, type="artist", limit=1)
    return s["artists"]["items"][0]["id"]


def search(query: str, type_: str):
    # query_string = f"q=name:{query}&type={type_}"
    s = spotify.search(query, type=type_, limit=1)

    for item in s[f"{type_}s"]["items"]:
        # logger.debug("Found %s '%s': %s", type_, item["name"], item["id"])
        return item
