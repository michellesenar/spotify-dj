import argparse
import sys

from .log_setup import get_logger
from dj.wrapper.playlist import create_new_playlist, add_to_existing_playlist

logger = get_logger(__name__)


def parse_args(arguments):
    parser = argparse.ArgumentParser(description="Spotify Add to Playlist")
    parser.add_argument(
        "-p", "--playlist_name", required=True, help="Name for new playlist"
    )
    parser.add_argument(
        "-d", "--description", required=True, help="Description for new playlist"
    )
    parser.add_argument(
        "-e", "--existing", required=False, help="Existing Playlist?", default=False
    )
    parser.add_argument(
        "-u",
        "--username",
        help="firstnamelastname (all lowercase; no spaces)",
        required=True,
    )
    parser.add_argument(
        "-g",
        "--genre",
        help="Genre(s) to seed recs from",
        nargs="+",
        required=False,
    )
    parser.add_argument(
        "-n",
        "--artist_name",
        help="Spotify Artist Name(s)",
        nargs="+",
        required=False,
    )

    return parser.parse_args()


def main():
    arguments = sys.argv[-1]
    parsed_args = parse_args(arguments)

    if parsed_args.existing:
        add_to_existing_playlist(
            parsed_args.username,
            parsed_args.playlist_name,
            parsed_args.artist_name,
            parsed_args.genre,
        )
    else:
        create_new_playlist(
            parsed_args.username,
            parsed_args.playlist_name,
            parsed_args.description,
            parsed_args.artist_name,
            parsed_args.genre,
        )


if __name__ == "__main__":
    main()
