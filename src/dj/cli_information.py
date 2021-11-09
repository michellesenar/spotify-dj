import argparse
import csv
import sys
import toml
from pathlib import Path

import dj.wrapper.artist
import dj.wrapper.genre
import dj.wrapper.playlist
import dj.wrapper.track
import dj.wrapper.util
from . import matcher
from .logging import log_track_characteristics, KEY_INTEGER_TO_NAME_MAP, MODE_MAP
from .log_setup import get_logger


ARTIST_INFO_BY_NAME = "by_name"


logger = get_logger(__name__)


def parse_args(arguments):
    parser = argparse.ArgumentParser(description="Spotify Track Analysis")
    parser.add_argument("-e", "--allow_explicit", default=False)
    subparsers = parser.add_subparsers()

    artist_parser = subparsers.add_parser("artist")
    artist_parser.add_argument(
        "mode",
        help="Which mode of information?",
        choices=["all_tracks", "info", "related_artists", "top_tracks", "master"],
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

    official_parser = subparsers.add_parser("official")
    official_parser.add_argument(
        "-p", "--playlist_id", required=True, help="Playlist ID (from 'Share' in UI"
    )
    official_parser.set_defaults(func=show_official_spotify_info)

    return parser.parse_args()


def show_official_spotify_info(args):
    dj.wrapper.playlist.get_official_spotify_playlist(args.playlist_id)


def show_genre_info(args):
    if args.genre_mode == "list":
        dj.wrapper.genre.list_genres()
    elif args.genre_mode == "recommend":
        if args.genre:  # and args.artist_name:
            dj.wrapper.genre.recommend_from_official_genres(
                args.artist_name, args.genre
            )
        else:
            print("At least 1 genre and 1 artist required.")


def show_track_info(args):
    track = dj.wrapper.util.search(args.track_name, "track")
    artist = dj.wrapper.artist.build_artist(track["artists"][0]["uri"])
    track = dj.wrapper.track.build_track(track)
    track_analysis = dj.wrapper.track.build_track_analysis(track)

    log_track_characteristics(artist, track_analysis)


def show_top_tracks_per_artist(args):
    dj.wrapper.artist.get_top_tracks_per_artist(args.artist_uri, args.allow_explicit)


def show_related_artists(args):
    artist = dj.wrapper.artist.build_artist(args.artist_uri)
    dj.wrapper.artist.get_related_artists(artist.id)


def get_artist_uri(args):
    if args.artist_uri == ARTIST_INFO_BY_NAME and args.artist_name:
        artist = dj.wrapper.util.search(args.artist_name, "artist")
        artist_uri = artist["uri"]
    else:
        artist_uri = args.artist_uri

    return artist_uri


def artist_information(args):
    artist_uri = get_artist_uri(args)
    artist = dj.wrapper.artist.build_artist(artist_uri)

    if args.mode == "master":
        related = [dj.wrapper.artist.build_artist(r['uri']) for r in dj.wrapper.artist.get_related_artists(artist.id)]

        all_artists = [artist] + related
        count = 0
        for artist in all_artists:
            count += 1
            if True or "chillhop" in related_artist['genres']:
                logger.info("Gathering results for %d out of %d related artists.", count, len(all_artists))
                track_analyses = dj.wrapper.track.get_all_tracks(artist, limit=args.limit)

                if args.recommend:
                    criteria = toml.load(args.input_toml_file)["characteristics"]
                    track_recommender(
                        artist,
                        criteria,
                        track_analyses,
                        output_file_name=args.output_csv_file,
                        allow_explicit=args.allow_explicit,
                    )


    if args.mode == "all_tracks":
        track_analyses = dj.wrapper.track.get_all_tracks(artist, limit=args.limit)

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
        dj.wrapper.artist.get_related_artists(artist.id)

    elif args.mode == "top_tracks":
        dj.wrapper.artist.get_top_tracks_per_artist(artist_uri, args.allow_explicit)


def track_recommender(
    artist, criteria, track_analyses, output_file_name=None, allow_explicit=False
):
    if output_file_name:
        filename = f"artist_csvs/{output_file_name}.csv"
    else:
        filename = f"artist_csvs/{artist.name}.csv"
        matcher.log_output_csv(artist)

    if Path(filename).exists():
        print(f"Continue to write to {filename}")
        existing = True
    else:
        print(f"Creating new CSV {filename}")
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
            "instrumentalness",
            "acousticness",
            "danceability",
            "key",
            "mode",
            "liveness",
            "loudness",
            "speechiness",
            "time_signature",
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
                                fieldnames[8]: str(analysis.instrumentalness),
                                fieldnames[9]: str(analysis.acousticness),
                                fieldnames[10]: str(analysis.danceability),
                                fieldnames[11]: str(KEY_INTEGER_TO_NAME_MAP[analysis.key]),
                                fieldnames[12]: str(MODE_MAP[analysis.mode]),
                                fieldnames[13]: str(analysis.liveness),
                                fieldnames[14]: str(analysis.loudness),
                                fieldnames[15]: str(analysis.speechiness),
                                fieldnames[16]: str(analysis.time_signature),
                            }
                        )
                        already_seen.append(songname)
                        log_track_characteristics(artist, track_analysis)


def main():
    arguments = sys.argv[-1]
    parsed_args = parse_args(arguments)
    parsed_args.func(parsed_args)


if __name__ == "__main__":
    main()
