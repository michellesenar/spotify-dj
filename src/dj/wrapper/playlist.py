import csv
import os

from dj.log_setup import get_logger
from dj.wrapper.connection import spotify
from dj.wrapper.genre import recommend_from_official_genres


logger = get_logger(__name__)


def get_official_spotify_playlist(playlist_id: str):
    breakpoint()
    for item in spotify.playlist(playlist_id)["tracks"]["items"]:
        track = item["track"]
        main_artist = track["artists"][0]["name"]
        main_id = track["artists"][0]["id"]
        track_name = track["name"]
        track_uri = track["uri"]

        logger.debug("'%s' -- %s", track_name, main_artist)


def add_recommended_tracks_to_playlist(user_id, artist_names, genres, playlist_id):
    logger.info("Playlist ID: %s", playlist_id)
    new_tracks = recommend_from_official_genres(artist_names, genres)
    track_uris = [t.track.uri for t in new_tracks]
    spotify.user_playlist_add_tracks(user_id, playlist_id, track_uris)


def add_track_uris_to_existing_playlist_name(username: str, playlist_name: str, track_uris):
    if len(track_uris):
        logger.info("Adding %d songs to playlist", len(track_uris))
        user_id = os.getenv(username)
        playlist_id = [
            p["id"]
            for p in spotify.user_playlists(user_id)["items"]
            if p["name"] == playlist_name
        ][0]
        spotify.user_playlist_add_tracks(user_id, playlist_id, track_uris)


def create_new_playlist(
    username: str, playlist_name: str, description: str, artist_names, genres
):
    user_id = os.getenv(username)
    new_playlist = spotify.user_playlist_create(
        user_id, playlist_name, description=description
    )
    add_recommended_tracks_to_playlist(
        user_id, artist_names, genres, new_playlist["id"]
    )

    logger.info("Finished creating playlist '%s'", playlist_name)


def add_to_existing_playlist(username: str, playlist_name: str, artist_names, genres):
    user_id = os.getenv(username)
    playlist_id = [
        p["id"]
        for p in spotify.user_playlists(user_id)["items"]
        if p["name"] == playlist_name
    ][0]
    add_recommended_tracks_to_playlist(user_id, artist_names, genres, playlist_id)

    logger.info("Added new songs to playlist '%s'", playlist_name)


def get_user_playlists(username: str):
    playlists = spotify.current_user_saved_tracks()
    logger.debug("Playlist Count: %s", playlists["total"])
    return playlists


def get_user_playlist_id_from_playlist_name(playlist_name: str):
    # playlists = get_user_playlists(user)
    # for playlist in playlists["items"]:
    #     if playlist["name"] == playlist_name:
    #         breakpoint()
    pass


def add_to_playlist_from_csv(username: str, playlist_id: str, csv_name: str):
    def _track_name(x):
        return f"{x['name']}__{x['artists'][0]['name']}"

    user_id = os.getenv(username)
    playlist_name = spotify.playlist(playlist_id)["name"]
    existing_track_uris = [
        x["track"]["uri"] for x in spotify.playlist_tracks(playlist_id)["items"]
    ]
    existing_track_names = [
        _track_name(x["track"]) for x in spotify.playlist_tracks(playlist_id)["items"]
    ]
    new_track_uris = []
    logger.debug(
        "Adding to %s's playlist '%s' from '%s'", username, playlist_name, csv_name
    )

    def _batch(seq, size):
        return [seq[i : i + size] for i in range(0, len(seq), size)]

    with open(csv_name, "r") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            new_track_uri = row["track_uri"]
            new_track_name = f"{row['track_name']}__{row['artist_name']}"
            new_track_uris.append((new_track_uri, new_track_name))

    for batch in _batch(new_track_uris, 10):
        actual_new_uris = set([x[0] for x in batch]).difference(
            set(existing_track_uris)
        )
        actual_new_names = set([x[1] for x in batch]).difference(
            set(existing_track_names)
        )
        if (
            actual_new_uris
            and actual_new_names
            and (len(actual_new_uris) == len(actual_new_names))
        ):
            spotify.user_playlist_add_tracks(user_id, playlist_id, actual_new_uris)

    logger.debug("Finished adding from %s", csv_name)
