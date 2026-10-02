import os
import spotipy

from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth


load_dotenv()


CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv(
    "SPOTIFY_REDIRECT_URI",
    "http://127.0.0.1:8888/callback"
)


SCOPE = (
    "user-modify-playback-state "
    "user-read-playback-state"
)


def conectar_spotify():

    if not CLIENT_ID or not CLIENT_SECRET:
        raise RuntimeError(
            "SPOTIFY_CLIENT_ID ou SPOTIFY_CLIENT_SECRET "
            "não foram configurados no .env"
        )

    auth_manager = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        open_browser=True,
        cache_path=".spotify_cache"
    )

    return spotipy.Spotify(
        auth_manager=auth_manager
    )


def encontrar_playlist_joao_gomes(sp):

    resultado = sp.search(
        q="João Gomes",
        type="playlist",
        limit=10
    )

    playlists = resultado.get(
        "playlists",
        {}
    ).get(
        "items",
        []
    )

    if not playlists:
        return None

    # Primeiro tenta encontrar uma playlist
    # cujo nome tenha João/Gomes.
    for playlist in playlists:

        nome = playlist.get(
            "name",
            ""
        ).lower()

        if (
            "joão gomes" in nome
            or
            "joao gomes" in nome
        ):
            return playlist

    # Caso não encontre exatamente,
    # usa o primeiro resultado da pesquisa.
    return playlists[0]


def tocar_playlist_joao_gomes():

    sp = conectar_spotify()

    playlist = encontrar_playlist_joao_gomes(
        sp
    )

    if not playlist:

        raise RuntimeError(
            "Não encontrei uma playlist do João Gomes."
        )

    playlist_uri = playlist.get(
        "uri"
    )

    playlist_name = playlist.get(
        "name",
        "Playlist"
    )

    if not playlist_uri:

        raise RuntimeError(
            "A playlist encontrada não possui URI."
        )

    # Inicia a playlist no dispositivo Spotify
    # atualmente ativo.
    sp.start_playback(
        context_uri=playlist_uri
    )

    return playlist_name
