import argparse
import csv
import sys
import toml
from pathlib import Path

from . import matcher, wrapper


ARTIST_INFO_BY_NAME = "by_name"


def parse_args(arguments):
    parser = argparse.ArgumentParser(description="Spotify Track Analysis")
    parser.add_argument("-e", "--allow_explicit", default=False)
    subparsers = parser.add_subparsers()

    artist_parser = subparsers.add_parser("artist")
    artist_parser.add_argument(
        "mode",
        help="Which mode of information?",
        choices=["all_tracks", "info", "related_artists", "top_tracks"],
    )
    artist_parser.add_argument(
        "-a",
        "--artist_uri",
        help="Spotify Artist URI. Default is for Frank Ocean.",
        default="spotify:artist:2h93pZq0e7k5yf4dywlkpM",
    )
    artist_parser.add_argument(
        "-n",
        "--artist_name",
        help="Spotify Artist Name",
        required=False,
    )
    artist_parser.add_argument(
        "-r",
        "--recommend",
        type=bool,
        default=False,
    )
    artist_parser.add_argument(
        "-i",
        "--input_toml_file",
        help="TOML file with criteria for playlist",
        required=False,
    )
    artist_parser.add_argument(
        "-o",
        "--output_csv_file",
        help="CSV file",
        required=False,
    )
    artist_parser.add_argument(
        "-l",
        "--limit",
        type=int,
        help="Limit search results to first N albums",
        required=False,
    )
    artist_parser.set_defaults(func=artist_information)

    track_parser = subparsers.add_parser("track")
    track_parser.add_argument(
        "-t",
        "--track_name",
        help="Spotify Track Name",
        required=True,
    )
    track_parser.set_defaults(func=show_track_info)

    genre_parser = subparsers.add_parser("genre")
    genre_parser.add_argument(
        "genre_mode",
        help="List all available genres or recommend songs from a genre",
        choices=["list", "recommend"],
    )
    genre_parser.add_argument(
        "-g",
        "--genre",
        help="Genre(s) to seed recs from",
        nargs="+",
        required=False,
    )
    genre_parser.add_argument(
        "-n",
        "--artist_name",
        help="Spotify Artist Name(s)",
        nargs="+",
        required=False,
    )
    genre_parser.set_defaults(func=show_genre_info)

    return parser.parse_args()


def show_genre_info(args):
    if args.genre_mode == "list":
        wrapper.genres()
    elif args.genre_mode == "recommend":
        if args.genre:  # and args.artist_name:
            recs = wrapper.recommendations_from_genres(args.artist_name, args.genre)
        else:
            print("At least 1 genre and 1 artist required.")


def show_track_info(args):
    track = wrapper.search(args.track_name, "track")
    artist_name = track["artists"][0]["name"]
    track = wrapper.build_track(track)
    track_analysis = wrapper.build_track_analysis(track)

    wrapper.log_track_info(artist_name, track_analysis)


def show_top_tracks_per_artist(args):
    wrapper.get_top_tracks_per_artist(args.artist_uri, args.allow_explicit)


def show_related_artists(args):
    artist = wrapper.build_artist(args.artist_uri)
    wrapper.get_related_artists(artist.id)


def get_artist_uri(args):
    if args.artist_uri == ARTIST_INFO_BY_NAME and args.artist_name:
        artist = wrapper.search(args.artist_name, "artist")
        artist_uri = artist["uri"]
    else:
        artist_uri == args.artist_uri

    return artist_uri


def artist_information(args):
    artist_uri = get_artist_uri(args)
    artist = wrapper.build_artist(artist_uri)

    if args.mode == "all_tracks":
        track_analyses = wrapper.get_all_tracks(artist, limit=args.limit)

        if args.recommend:
            criteria = toml.load(args.input_toml_file)["characteristics"]
            track_recommender(
                artist,
                criteria,
                track_analyses,
                output_file_name=args.output_csv_file,
                allow_explicit=args.allow_explicit,
            )

    elif args.mode == "info":
        print(artist)

    elif args.mode == "related_artists":
        wrapper.get_related_artists(artist.id)

    elif args.mode == "top_tracks":
        wrapper.get_top_tracks_per_artist(artist_uri, args.allow_explicit)


def track_recommender(
    artist, criteria, track_analyses, output_file_name=None, allow_explicit=False
):
    if output_file_name:
        filename = f"artist_csvs/{output_file_name}.csv"
    else:
        filename = f"artist_csvs/{artist.name}.csv"
        matcher.log_output_csv(artist)

    if Path(filename).exists():
        print(f"Continue to write to %s", filename)
        existing = True
    else:
        print(f"Creating new CSV %s", filename)
        existing = False

    already_seen = []

    with open(filename, "a") as fh:
        fieldnames = [
            "track_uri",
            "track_name",
            "artist_name",
            "valence",
            "energy",
            "speechiness",
            "bpm",
            "duration_ms",
        ]
        writer = csv.DictWriter(fh, fieldnames=fieldnames)

        if not existing:
            writer.writeheader()

        for track_analysis in track_analyses:
            track = track_analysis.track
            if analysis := track_analysis.analysis:
                if matcher.allowable_track(
                    track, allow_explicit=allow_explicit
                ) and matcher.acceptable_track(track, analysis, criteria):
                    songname = f"{track.name}__{artist.name}"
                    if songname not in already_seen:
                        writer.writerow(
                            {
                                fieldnames[0]: track.uri,
                                fieldnames[1]: track.name,
                                fieldnames[2]: artist.name,
                                fieldnames[3]: str(analysis.valence),
                                fieldnames[4]: str(analysis.energy),
                                fieldnames[5]: str(analysis.speechiness),
                                fieldnames[6]: str(analysis.tempo),
                                fieldnames[7]: str(analysis.duration_ms),
                            }
                        )
                        already_seen.append(songname)
                    matcher.log_track_characteristics(artist, track, analysis)


def main():
    arguments = sys.argv[-1]
    parsed_args = parse_args(arguments)
    parsed_args.func(parsed_args)


if __name__ == "__main__":
    main()
