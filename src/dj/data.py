from typing import List
from dataclasses import dataclass


@dataclass
class AudioFeatures:
    danceability: float
    energy: float
    key: float
    loudness: float
    mode: float
    speechiness: float
    acousticness: float
    instrumentalness: float
    liveness: float
    valence: float
    tempo: float
    type: str
    id: str
    uri: str
    track_href: str
    analysis_url: str
    duration_ms: str
    time_signature: str


@dataclass
class Artist:
    name: str
    id: str
    genres: List[str]


@dataclass
class Track:
    name: str
    uri: str
    explicit: bool


@dataclass
class TrackAnalysis:
    track: Track
    analysis: AudioFeatures


@dataclass
class Album:
    id: str
    name: str
    uri: str
