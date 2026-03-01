"""Shared test fixtures."""

from __future__ import annotations

import pytest

from podcaster.config import Settings
from podcaster.models import PersonInput, ResearchItem, ResearchResult


@pytest.fixture
def settings():
    return Settings(
        anthropic_api_key="test-key",
        serper_api_key="",
        reddit_client_id="",
        reddit_client_secret="",
    )


@pytest.fixture
def sample_person():
    return PersonInput(
        name="Jane Smith",
        bio="AI researcher at Stanford",
        twitter_handle="@janesmith",
        medium_username="janesmith",
        target_audience="Software engineers interested in AI",
        topic="Practical applications of LLMs",
    )


@pytest.fixture
def sample_research(sample_person):
    return ResearchResult(
        person=sample_person,
        items=[
            ResearchItem(
                source="web",
                title="Jane Smith on the future of AI",
                content="In a recent interview, Jane Smith discussed how LLMs are transforming software engineering workflows...",
                url="https://example.com/interview",
            ),
            ResearchItem(
                source="medium",
                title="Building Responsible AI Systems",
                content="Jane Smith's latest Medium article explores the challenges of deploying LLMs in production environments...",
                url="https://medium.com/@janesmith/responsible-ai",
                date="2025-12-01",
            ),
            ResearchItem(
                source="twitter",
                title="Tweet thread on AI safety",
                content="Excited to share our new paper on AI alignment. Key findings: (1) RLHF has significant limitations...",
                url="https://x.com/janesmith/status/123",
            ),
        ],
        sources_attempted=["web", "twitter", "linkedin", "medium", "reddit"],
        sources_succeeded=["web", "medium", "twitter"],
        sources_failed={"linkedin": "no results", "reddit": "no results"},
    )
