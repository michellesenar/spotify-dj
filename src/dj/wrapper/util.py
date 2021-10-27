from dj.wrapper.connection import spotify


def search(query: str, type_: str):
    s = spotify.search(query, type=type_, limit=1)

    for item in s[f"{type_}s"]["items"]:
        return item
