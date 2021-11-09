import csv
import os

from dj.log_setup import get_logger
from dj.wrapper.connection import spotify


logger = get_logger(__name__)


def get_official_spotify_playlist(playlist_id: str):
    for item in spotify.playlist(playlist_id)['tracks']['items']:
        track = item['track']
        main_artist = track['artists'][0]['name']
        main_id = track['artists'][0]['id']
        track_name = track['name']
        track_uri = track['uri']

        logger.debug("'%s' -- %s", track_name, main_artist)


def create_new_playlist(playlist_name: str):
    spotify.user_playlist_create(create_new_playlist)


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
        return [seq[i: i + size] for i in range(0, len(seq), size)]

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
