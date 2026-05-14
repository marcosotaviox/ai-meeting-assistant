"""
utils/html_generator.py
========================
Generates a single HTML presentation file from MeetingInsights.
Uses Claude to produce a McKinsey/BCG-style slide deck.
Images fetched from real Unsplash API URLs — no invented URLs.
"""

import os
import requests
from anthropic import Anthropic
from src.core.analyser import MeetingInsights
from dotenv import load_dotenv

load_dotenv()


_SYSTEM = """You are an Elite Presentation Designer (McKinsey/BCG style).
Generate a single HTML file containing a complete slide deck based on the provided content.

MANDATORY TECHNICAL GUIDELINES:

1. Slide Structure:
   - Each slide must be a <div class="slide-container"> with fixed dimensions 1280px x 720px
   - Body background: dark grey to highlight slides like a carousel
   - Slides stacked vertically with margin between them

2. Design System:
   - Background: Black/Dark Grey (#000, #121212)
   - Text: Ice White (#f5f5f5)
   - Accent/Highlight: Neon Green/Lime (#deff9a)
   - Typography: Google Fonts — 'Urbanist' (700) for titles, 'Lato' (400) for body
   - Visual accents: subtle gradients, abstract background shapes, thin lines (1px solid #deff9a)

3. Required Layouts (vary between them):
   - title_slide: Giant title with accent colour highlight
   - two_column: Text with FontAwesome icons left, image right with rounded borders (24px)
   - tiled_tiles: 3-4 rectangular tiles with #1a1a1a background and subtle borders
   - bleed_image: Image occupying exactly 50% of slide width, edge to edge vertically
   - highlighted_numbers: Huge number in accent colour for impactful statistics

4. Business Rules:
   - Use only FontAwesome icons (import via CDN)
   - Keep slide titles always in the same position (Top-Left) to avoid visual jumps
   - Maximum 60 words per slide
   - Use object-fit: cover for images
   - ONLY use image URLs explicitly provided in the prompt under "Real Unsplash Image URLs"
   - NEVER invent, guess, or generate image URLs
   - If no image URL is provided for a slide, use CSS gradients and geometric shapes instead
   - YouTube thumbnails: use the exact thumbnail URL provided, make them clickable links
   - No JavaScript
   - Clean, modern, high-contrast, extremely professional

OUTPUT FORMAT:
- Single HTML block with CSS in <style> tag and slides in <body>
- No markdown, no explanation, no code fences
- Start directly with <!DOCTYPE html>
- Always respond in the same language as the content provided
"""

_HUMAN = """Create a professional slide deck for this content:

Title: {title}
Content Type: {content_type}
Sentiment: {sentiment}

Summary:
{summary}

Key Points:
{key_points}

Key Concepts:
{key_concepts}

Examples:
{examples}

Action Items:
{action_items}

Key Decisions:
{key_decisions}

Open Questions:
{open_questions}

Real Unsplash Image URLs (use ONLY these URLs for images, never invent others):
{image_urls}

YouTube Videos (include as thumbnails + clickable links):
{youtube_links}

Generate maximum 12 slides. Make it visually stunning and professional.
IMPORTANT: Only use image URLs from the list above. Never invent or guess image URLs.
"""


def _get_unsplash_url(query: str) -> str | None:
    """Fetch a real image URL from Unsplash API."""
    key = os.environ.get("UNSPLASH_ACCESS_KEY")
    if not key:
        return None
    try:
        r = requests.get(
            "https://api.unsplash.com/search/photos",
            params={"query": query, "per_page": 1, "orientation": "landscape"},
            headers={"Authorization": f"Client-ID {key}"},
            timeout=10,
        )
        return r.json()["results"][0]["urls"]["regular"]
    except Exception as exc:
        print(f"Unsplash fetch failed: {exc}")
        return None


def generate_html_slides(insights: MeetingInsights,
                         include_youtube: bool = False) -> str:
    """
    Generate a complete HTML slide deck from MeetingInsights.

    Args:
        insights:         Structured insights from analyse_transcript().
        include_youtube:  Whether to include YouTube video thumbnails.

    Returns:
        Complete HTML string ready for download.
    """
    from src.utils.youtube_search import search_youtube

    # ── Fetch real Unsplash image URLs ────────────────────────────────────────
    queries = []
    if insights.key_points:
        queries.extend([p[:60] for p in insights.key_points[:2]])
    if insights.key_concepts:
        queries.extend([c.concept for c in insights.key_concepts[:2]])

    image_lines = []
    for query in queries[:4]:
        url = _get_unsplash_url(query)
        if url:
            image_lines.append(f"- {query[:40]}: {url}")

    images_section = "\n".join(image_lines) if image_lines else "None — use CSS gradients only"

    # ── Fetch YouTube videos ──────────────────────────────────────────────────
    youtube_links = ""
    if include_youtube and insights.content_type != "Meeting":
        yt_queries = []
        if insights.key_points:
            yt_queries.append(insights.key_points[0][:80])
        if insights.key_concepts:
            yt_queries.append(insights.key_concepts[0].concept)

        videos = []
        for query in yt_queries:
            results = search_youtube(query, max_results=1)
            videos.extend(results)
            if len(videos) >= 2:
                break

        if videos:
            youtube_links = "\n".join(
                f"- {v['title']}: {v['url']} (thumbnail: {v['thumbnail']})"
                for v in videos
            )

    # ── Format content ─────────────────────────────────────────────────────────
    key_points   = "\n".join(f"- {p}" for p in insights.key_points)
    key_concepts = "\n".join(f"- {c.concept}: {c.explanation}" for c in insights.key_concepts)
    examples     = "\n".join(f"- {e.context}: {e.description}" for e in insights.examples)
    action_items = "\n".join(f"- [{a.owner}] {a.task} (Due: {a.deadline})" for a in insights.action_items)
    decisions    = "\n".join(f"- {d}" for d in insights.key_decisions)
    questions    = "\n".join(f"- {q}" for q in insights.open_questions)

    # ── Call Claude ───────────────────────────────────────────────────────────
    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=8192,
        system=_SYSTEM,
        messages=[
            {
                "role": "user",
                "content": _HUMAN.format(
                    title=insights.title,
                    content_type=insights.content_type,
                    sentiment=insights.sentiment,
                    summary=insights.summary,
                    key_points=key_points or "None",
                    key_concepts=key_concepts or "None",
                    examples=examples or "None",
                    action_items=action_items or "None",
                    key_decisions=decisions or "None",
                    open_questions=questions or "None",
                    image_urls=images_section,
                    youtube_links=youtube_links or "None",
                ),
            }
        ],
    )

    html = message.content[0].text.strip()

    # Strip accidental markdown fences
    if html.startswith("```"):
        html = html.split("\n", 1)[1]
    if html.endswith("```"):
        html = html.rsplit("```", 1)[0]

    return html.strip()