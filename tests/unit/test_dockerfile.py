"""Dockerfile regression tests."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_dockerfile_uses_playwright_base_image_1_59() -> None:
    """Base image should align with installed Playwright runtime."""
    dockerfile = (PROJECT_ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "mcr.microsoft.com/playwright/python:v1.59.0-noble" in dockerfile
