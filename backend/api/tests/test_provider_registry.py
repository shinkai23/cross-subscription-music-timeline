from app.providers.apple_music_adapter import AppleMusicAdapter
from app.providers.registry import get_provider_adapter, list_provider_adapters
from app.providers.spotify_adapter import SpotifyAdapter


def test_get_provider_adapter_returns_spotify_adapter() -> None:
    adapter = get_provider_adapter("spotify")

    assert isinstance(adapter, SpotifyAdapter)
    assert adapter.provider == "spotify"


def test_get_provider_adapter_returns_apple_music_adapter() -> None:
    adapter = get_provider_adapter("apple_music")

    assert isinstance(adapter, AppleMusicAdapter)
    assert adapter.provider == "apple_music"


def test_list_provider_adapters_includes_supported_providers() -> None:
    adapters = list_provider_adapters()
    providers = {adapter.provider for adapter in adapters}

    assert providers == {"spotify", "apple_music"}
