from app.providers.apple_music_adapter import AppleMusicAdapter
from app.providers.base import MusicProviderAdapter
from app.providers.spotify_adapter import SpotifyAdapter

_adapters: dict[str, MusicProviderAdapter] = {
    "apple_music": AppleMusicAdapter(),
    "spotify": SpotifyAdapter(),
}


def get_provider_adapter(provider: str) -> MusicProviderAdapter:
    return _adapters[provider]


def list_provider_adapters() -> list[MusicProviderAdapter]:
    return list(_adapters.values())
