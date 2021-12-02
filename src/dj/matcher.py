from typing import Any, Dict

from .data import Artist, AudioFeatures, Track
from .log_setup import get_logger

logger = get_logger(__name__)


def allowable_track(track, allow_explicit=False):
    return allow_explicit or not track.explicit


def compare_values(section: Dict[str, Any], keyname: str, actual_value: float) -> bool:
    if criteria_value := section.get(keyname):
        if keyname.startswith("min"):
            if keyname == "tempo":
                return actual_value >= criteria_value or (2 * actual_value >= 2 * criteria_value)
            else:
                return actual_value >= criteria_value
        elif keyname.startswith("max"):
            if keyname == "tempo":
                return actual_value <= criteria_value or (2 * actual_value <= 2 * criteria_value)
            else:
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
        and compare_values(criteria, "min_acousticness", analysis.acousticness)
        and compare_values(criteria, "max_acousticness", analysis.acousticness)
        and compare_values(criteria, "min_danceability", analysis.danceability)
        and compare_values(criteria, "max_danceability", analysis.danceability)
        and compare_values(criteria, "min_liveness", analysis.liveness)
        and compare_values(criteria, "max_liveness", analysis.liveness)
        and compare_values(criteria, "min_loudness", analysis.loudness)
        and compare_values(criteria, "max_loudness", analysis.loudness)
        and valence_energy_relationship(criteria, analysis)
    )


def log_output_csv(artist: Artist):
    logger.info("Writing results to '%s.csv'", artist.name)


def keep_track(criteria, track, analysis, allow_explicit=False):
    return allowable_track(track, allow_explicit=allow_explicit) and acceptable_track(track, analysis, criteria)
