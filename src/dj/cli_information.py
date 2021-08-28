import argparse
import sys

from . import wrapper


def parse_args(arguments):
    parser = argparse.ArgumentParser(description="Spotify Track Analysis")
    parser.add_argument(
        "-a",
        "--artist_uri",
        help="Spotify Artist URI. Default is for Frank Ocean.",
        default="spotify:artist:2h93pZq0e7k5yf4dywlkpM",
    )
    parser.add_argument("-e", "--allow_explicit", default=False)
    subparsers = parser.add_subparsers()

    top_tracks_parser = subparsers.add_parser("top_tracks_per_artist")
    top_tracks_parser.set_defaults(func=show_top_tracks_per_artist)

    related_artists_parser = subparsers.add_parser("related_artists")
    related_artists_parser.set_defaults(func=show_related_artists)

    return parser.parse_args()


def show_top_tracks_per_artist(args):
    wrapper.get_top_tracks_per_artist(args.artist_uri, args.allow_explicit)


def show_related_artists(args):
    artist = wrapper.get_artist(args.artist_uri)
    wrapper.get_related_artists(artist.id)


def main():
    arguments = sys.argv[-1]
    parsed_args = parse_args(arguments)
    parsed_args.func(parsed_args)


if __name__ == "__main__":
    main()
