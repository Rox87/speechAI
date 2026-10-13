"""OpenAI client provider and factory for SpeechAI."""

from __future__ import annotations

from typing import Optional
from openai import OpenAI
from src.core.config import config
from src.core.logger import logger

_cached_client: Optional[OpenAI] = None
_cached_base_url: Optional[str] = None
_cached_api_key: Optional[str] = None


def get_openai_client(
    force_new: bool = False,
    base_url: Optional[str] = None,
) -> OpenAI:
    """Retrieve or initialize an authenticated OpenAI client instance.

    Args:
        force_new: If True, instantiates a new client instead of cached instance.
        base_url: Optional custom API Base URL. Defaults to config.openai_base_url.

    Returns:
        OpenAI: Authenticated client.

    Raises:
        ValueError: If neither OPENAI_API_KEY nor custom base_url is configured.
    """
    global _cached_client, _cached_base_url, _cached_api_key

    target_base_url = base_url if base_url is not None else config.openai_base_url
    if target_base_url is not None:
        target_base_url = target_base_url.strip() or None

    if not config.has_openai_key:
        raise ValueError(
            "OPENAI_API_KEY is not set or contains default placeholder. "
            "Please configure your OpenAI API key in the .env file."
        )

    # Re-instantiate if uninitialized, forced, or if base_url / api_key changed
    if (
        _cached_client is None
        or force_new
        or _cached_base_url != target_base_url
        or _cached_api_key != config.openai_api_key
    ):
        kwargs = {"api_key": config.openai_api_key.strip()}
        if target_base_url:
            kwargs["base_url"] = target_base_url
            logger.debug(f"Configuring OpenAI client with base_url: {target_base_url}")

        _cached_client = OpenAI(**kwargs)
        _cached_base_url = target_base_url
        _cached_api_key = config.openai_api_key

    return _cached_client


def reset_client() -> None:
    """Reset cached client instance."""
    global _cached_client, _cached_base_url, _cached_api_key
    _cached_client = None
    _cached_base_url = None
    _cached_api_key = None
