"""Application settings loaded from environment variables."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM (required)
    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-4-20250514"

    # Web search (optional - enables Serper; DuckDuckGo is always available)
    serper_api_key: str = ""

    # Reddit (optional)
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "podcaster:v0.1.0"

    # Behaviour
    request_timeout: int = 30

    model_config = {"env_prefix": "PODCASTER_", "env_file": ".env", "extra": "ignore"}
