from .log_setup import get_logger
from .data import Artist, TrackAnalysis

KEY_INTEGER_TO_NAME_MAP = {
    0: "C",
    1: "C♯/D♭",
    2: "D",
    3: "D♯/E♭",
    4: "E",
    5: "F",
    6: "F♯/G♭",
    7: "G",
    8: "G♯/A♭",
    9: "A",
    10: "A♯/B♭",
    11: "B",
}

MODE_MAP = {
    0: "minor",
    1: "major"
}

logger = get_logger(__name__)


def log_track_characteristics(artist: Artist, track_analysis: TrackAnalysis):
    track = track_analysis.track
    analysis = track_analysis.analysis

    minutes, seconds = divmod(analysis.duration_ms / 1000, 60)
    logger.debug("")
    logger.debug("'%s' by %s. Explicit = %s", track.name, artist.name, track.explicit)
    logger.debug("--Duration: %d min %d sec", minutes, seconds)
    logger.debug("--Valence: %s", analysis.valence)
    logger.debug("--Energy: %s", analysis.energy)
    logger.debug("--Speechiness: %s", analysis.speechiness)
    logger.debug("--Tempo: %s BPM; %s %s", analysis.tempo, KEY_INTEGER_TO_NAME_MAP[analysis.key], MODE_MAP[analysis.mode])
    logger.debug("--Instrumentalness: %s", analysis.instrumentalness)
