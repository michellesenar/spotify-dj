import argparse
import sys
import toml

from .log_setup import get_logger
from . import matcher
from dj.data import TrackAnalysisArtist
from dj.wrapper.playlist import add_track_uris_to_existing_playlist_name
from dj.wrapper.recommender import build_recommended_tracklist, recommend

logger = get_logger(__name__)


def parse_args(arguments):
    parser = argparse.ArgumentParser(description="Spotify Add to Playlist")
    parser.add_argument("-E", "--allow_explicit", type=bool, default=False)
    parser.add_argument(
        "-p", "--playlist_name", required=True, help="Name for new playlist"
    )
    parser.add_argument(
        "-e", "--existing", required=False, type=bool, help="Existing Playlist?", default=False
    )
    parser.add_argument(
        "-u",
        "--username",
        help="firstnamelastname (all lowercase; no spaces)",
        required=True,
    )
    parser.add_argument(
        "-l",
        "--limit",
        default=20,
        help="Number of recommendations to limit to."
    )
    parser.add_argument(
        "-g",
        "--genres",
        help="Official Spotify Genre(s) to seed recs from",
        nargs="+",
        required=False,
    )
    parser.add_argument(
        "-a",
        "--artist_ids",
        help="Spotify Artist ID(s) or URI(s)",
        nargs="+",
        required=False,
    )
    parser.add_argument(
        "-t",
        "--track_ids",
        help="Spotify Track ID(s) or URI(s)",
        nargs="+",
        required=False,
    )

    parser.add_argument(
        "-f",
        "--filter",
        type=bool,
        default=False,
    )
    parser.add_argument(
        "-w",
        "--write_analysis_to_output_file",
        action=argparse.BooleanOptionalAction
    )
    parser.add_argument(
        "-i",
        "--input_toml_file",
        help="TOML file with criteria for playlist",
        required=False,
    )
    parser.add_argument(
        "-o",
        "--output_csv_file",
        help="CSV file",
        required=False,
    )


    return parser.parse_args()


def main():
    arguments = sys.argv[-1]
    parsed_args = parse_args(arguments)

    assert parsed_args.genres or parsed_args.artist_ids or parsed_args.track_ids

    tracks_artists_to_add = []

    recs = recommend(parsed_args.artist_ids, parsed_args.genres, track_ids=parsed_args.track_ids, limit=parsed_args.limit)
    track_analyses, artists = build_recommended_tracklist(recs)

    for track_analysis in track_analyses:
        track = track_analysis.track
        if analysis := track_analysis.analysis:
            if parsed_args.filter:
                criteria = toml.load(parsed_args.input_toml_file)["characteristics"]
                if matcher.keep_track(criteria, track, analysis, allow_explicit=parsed_args.allow_explicit):
                    track_analysis_index = track_analyses.index(track_analysis)
                    corresponding_artist = artists[track_analysis_index]
                    tracks_artists_to_add.append(
                        TrackAnalysisArtist(track_analysis=track_analysis, artist=corresponding_artist)
                    )
            else:
                track_analysis_index = track_analyses.index(track_analysis)
                corresponding_artist = artists[track_analysis_index]
                tracks_artists_to_add.append(
                    TrackAnalysisArtist(track_analysis=track_analysis, artist=corresponding_artist)
                )


    if parsed_args.existing:
        add_track_uris_to_existing_playlist_name(
            parsed_args.username,
            parsed_args.playlist_name,
            [taa.track_analysis.track.uri for taa in tracks_artists_to_add]
        )

        if parsed_args.write_analysis_to_output_file:
            assert parsed_args.output_file_name
            filename = f"artist_csvs/{parsed_args.output_file_name}.csv"

            if Path(filename).exists():
                existing = True
            else:
                existing = False

            with open(filename, "a") as fh:
                fieldnames = [
                    "track_uri",
                    "track_name",
                    "artist_name",
                    "valence", #1
                    "energy", #2
                    "speechiness", #3
                    "bpm",
                    "duration_ms",
                    "instrumentalness" #4,
                    "acousticness", #5
                    "danceability", #6
                    "key",
                    "mode",
                    "liveness", #7
                    "loudness", #9
                    "time_signature",
                ]
                writer = csv.DictWriter(fh, fieldnames=fieldnames)

                if not existing:
                    writer.writeheader()

                for taa in tracks_artists_to_add:
                    track = taa.track_analysis.track
                    analysis = taa.track_analysis.analysis
                    artist = taa.artist
                    writer.writerow({
                        fieldnames[0]: track.uri,
                        fieldnames[1]: track.name,
                        fieldnames[2]: artist.name,
                        fieldnames[3]: str(analysis.valence),
                        fieldnames[4]: str(analysis.energy),
                        fieldnames[5]: str(analysis.speechiness),
                        fieldnames[6]: str(analysis.tempo),
                        fieldnames[7]: str(analysis.duration_ms),
                        fieldnames[8]: str(analysis.instrumentalness),
                        fieldnames[9]: str(analysis.acousticness),
                        fieldnames[10]: str(analysis.danceability),
                        fieldnames[11]: str(
                            KEY_INTEGER_TO_NAME_MAP[analysis.key]
                        ),
                        fieldnames[12]: str(MODE_MAP[analysis.mode]),
                        fieldnames[13]: str(analysis.liveness),
                        fieldnames[14]: str(analysis.loudness),
                        fieldnames[15]: str(analysis.time_signature),
                    }
                )
    else:
        pass

if __name__ == "__main__":
    main()
