from setuptools import find_packages, setup

requirements = [
    "python-dotenv",
    "spotipy",
]

setup(
    name="spotify-dj",
    version="0.1",
    description="Collection of scripts to auto-generate playlists",
    url="https://github.com/michellesenar/spotify-dj",
    author="Michelle Senar Dressler",
    license="MIT",
    install_requires=requirements,
    packages=find_packages("src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "information = dj.cli_information:main",
        ],
    },
)
