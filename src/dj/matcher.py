import toml
from typing import Any, Dict, List

from . import wrapper
from .data import Artist, AudioFeatures, Track
from .logging import get_logger

logger = get_logger(__name__)


def allowable_track(track, allow_explicit=False):
    return allow_explicit or not track.explicit


def compare_values(section: Dict[str, Any], keyname: str, actual_value: float) -> bool:
    if criteria_value := section.get(keyname):
        if keyname.startswith("min"):
            return actual_value >= criteria_value
        elif keyname.startswith("max"):
            return actual_value <= criteria_value
        else:
            return actual_value == criteria_value
    else:
        return True


def valence_energy_relationship(
    section: Dict[str, Any], analysis: AudioFeatures
) -> bool:
    valence_energy = analysis.valence * analysis.energy
    if product_value := section.get("product"):
        return valence_energy > product_value
    else:
        return True


def acceptable_track(track: Track, analysis: AudioFeatures, criteria: Dict[str, Any]):
    return (
        compare_values(criteria, "max_duration_ms", analysis.duration_ms)
        and compare_values(criteria, "min_duration_ms", analysis.duration_ms)
        and compare_values(criteria, "min_valence", analysis.valence)
        and compare_values(criteria, "max_valence", analysis.valence)
        and compare_values(criteria, "min_energy", analysis.energy)
        and compare_values(criteria, "max_energy", analysis.energy)
        and compare_values(criteria, "min_tempo", analysis.tempo)
        and compare_values(criteria, "max_tempo", analysis.tempo)
        and compare_values(criteria, "mode", analysis.mode)
        and compare_values(criteria, "min_instrumentalness", analysis.instrumentalness)
        and compare_values(criteria, "max_instrumentalness", analysis.instrumentalness)
        and compare_values(criteria, "min_speechiness", analysis.speechiness)
        and compare_values(criteria, "min_speechiness", analysis.speechiness)
        and valence_energy_relationship(criteria, analysis)
    )


def log_output_csv(artist: Artist):
    logger.info("Writing results to '%s.csv'", artist.name)


def log_track_characteristics(artist: Artist, track: Track, analysis: AudioFeatures):
    minutes, seconds = divmod(analysis.duration_ms / 1000, 60)
    logger.debug("")
    logger.debug("'%s' by %s. Explicit = %s", track.name, artist.name, track.explicit)
    logger.debug("--Track Duration: %d min %d sec", minutes, seconds)
    logger.debug("--Track Valence: %s", analysis.valence)
    logger.debug("--Track Energy: %s", analysis.energy)
    logger.debug("--Track Speechiness: %s", analysis.speechiness)
    # logger.debug("---- %s BPM; %s %s", analysis.tempo, KEY_INTEGER_TO_NAME_MAP[analysis.key], MODE_MAP[analysis.mode])
    # logger.debug("-- instrumentalness: %s", analysis.instrumentalness)
