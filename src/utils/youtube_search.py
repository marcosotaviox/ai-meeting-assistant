"""
utils/youtube_search.py
========================
Fetches relevant YouTube videos for a given concept/keyword.
Uses YouTube Data API v3.
"""

import os
import requests


def search_youtube(query: str, max_results: int = 2) -> list[dict]:
    """
    Search YouTube for videos related to a query.

    Args:
        query:       Search keyword or concept.
        max_results: Number of results to return (default 1).

    Returns:
        List of dicts with keys: title, url, thumbnail.
    """
    key = os.environ.get("YOUTUBE_API_KEY")
    if not key:
        return []

    try:
        r = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "key": key,
                "q": query,
                "part": "snippet",
                "type": "video",
                "maxResults": max_results,
                "relevanceLanguage": "pt",
            },
            timeout=10,
        )
        results = []
        for item in r.json().get("items", []):
            video_id = item["id"]["videoId"]
            results.append({
                "title": item["snippet"]["title"],
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
            })
        return results
    except Exception as exc:
        print(f"YouTube search failed: {exc}")
        return []