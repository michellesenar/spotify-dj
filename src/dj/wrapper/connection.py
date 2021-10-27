import spotipy
from dotenv import load_dotenv

from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

scope = "user-library-read playlist-modify-public playlist-modify-private"
spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
