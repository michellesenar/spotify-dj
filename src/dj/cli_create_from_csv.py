import argparse
import sys
import toml
from typing import Any, Dict, List

from .data import Track, AudioFeatures
from .log_setup import get_logger
from dj.wrapper.playlist import add_to_playlist_from_csv

logger = get_logger(__name__)


def parse_args(arguments):
    parser = argparse.ArgumentParser(description="Spotify Add to Playlist")
    parser.add_argument(
        "-i",
        "--input_csv_file",
        help="CSV file with tracks to add.",
    )
    parser.add_argument(
        "-p", "--playlist_id", required=True, help="Playlist ID (from 'Share' in UI"
    )
    parser.add_argument(
        "-u",
        "--username",
        help="firstnamelastname (all lowercase; no spaces)",
        required=True,
    )

    return parser.parse_args()


def main():
    arguments = sys.argv[-1]
    parsed_args = parse_args(arguments)

    add_to_playlist_from_csv(
        parsed_args.username, parsed_args.playlist_id, parsed_args.input_csv_file
    )


if __name__ == "__main__":
    main()
