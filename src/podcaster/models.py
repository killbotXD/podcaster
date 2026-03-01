"""Pydantic data models used throughout the pipeline."""

from __future__ import annotations

from pydantic import BaseModel


class PersonInput(BaseModel):
    name: str
    bio: str | None = None
    linkedin_url: str | None = None
    twitter_handle: str | None = None
    medium_username: str | None = None
    reddit_username: str | None = None
    target_audience: str | None = None
    topic: str | None = None


class ResearchItem(BaseModel):
    source: str
    title: str | None = None
    content: str
    url: str | None = None
    date: str | None = None


class ResearchResult(BaseModel):
    person: PersonInput
    items: list[ResearchItem] = []
    sources_attempted: list[str] = []
    sources_succeeded: list[str] = []
    sources_failed: dict[str, str] = {}


class TalkingPoint(BaseModel):
    number: int
    question: str
    context: str
    sources: list[str] = []
    follow_up_angles: list[str] = []


class PodcastBrief(BaseModel):
    guest_name: str
    guest_summary: str
    talking_points: list[TalkingPoint]
    research_summary: str
