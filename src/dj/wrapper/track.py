from typing import Any, Dict, List

from dj.data import Artist, Album, Track, TrackAnalysis, AudioFeatures
from dj.logging import log_track_characteristics
from dj.log_setup import get_logger
from dj.wrapper.connection import spotify


logger = get_logger(__name__)


def allowable_track(allow_explicit, track):
    return allow_explicit or not track.explicit


def get_track_by_uri(uri: str):
    return spotify.track(uri)


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


def build_preliminary_tracklist(
    spotify_tracks: List[Dict[str, Any]], allow_explicit=False
) -> List[TrackAnalysis]:
    analyses = []

    for t in spotify_tracks:
        track = build_track(t)
        track_analysis = build_track_analysis(track)
        logger.debug("'%s'", track.name)
        logger.debug("---- URI: %s", track.uri)
        analyses.append(track_analysis)

    return analyses
