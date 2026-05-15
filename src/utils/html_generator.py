"""
utils/html_generator.py
========================
Generates a single HTML presentation file from MeetingInsights.
McKinsey/BCG style — CSS gradients and shapes only, no external images.
YouTube thumbnails embedded as base64 when requested.
"""

import os
import re
import base64
import requests
from anthropic import Anthropic
from src.core.analyser import MeetingInsights
from dotenv import load_dotenv

load_dotenv()


def _fetch_as_base64(url: str) -> str | None:
    """Download image and return as base64 data URI."""
    try:
        r = requests.get(url, timeout=15)
        b64 = base64.b64encode(r.content).decode("utf-8")
        content_type = r.headers.get("content-type", "image/jpeg").split(";")[0]
        return f"data:{content_type};base64,{b64}"
    except Exception as exc:
        print(f"Fetch failed: {exc}")
        return None


_SYSTEM = """You are an Elite Presentation Designer (McKinsey/BCG style).
Generate a single HTML file containing a complete slide deck based on the provided content.

MANDATORY TECHNICAL GUIDELINES:

1. Slide Structure:
   - Each slide must be a <div class="slide-container"> with fixed dimensions 1280px x 720px
   - Body background: #1a1a1a to highlight slides like a carousel
   - Slides stacked vertically with 40px margin between them

2. Design System:
   - Background: Black/Dark Grey (#000, #121212)
   - Text: Ice White (#f5f5f5)
   - Accent: Neon Green/Lime (#deff9a)
   - Typography: Google Fonts — 'Urbanist' (700) for titles, 'Lato' (400) for body
   - Visual accents: subtle gradients, geometric SVG shapes, thin lines (1px solid #deff9a)

3. Required Layouts (vary between them):
   - title_slide: Giant title with accent colour, abstract SVG shape background
   - two_column: FontAwesome icons + text left, decorative gradient block right
   - tiled_tiles: 3-4 tiles with #1a1a1a background, subtle borders, accent numbers
   - highlighted_numbers: Huge accent-coloured statistic number, minimal text
   - quote_slide: Large pull quote in accent colour, thin border left accent

4. Visual Design Rules:
   - Use CSS gradients and SVG geometric shapes for visual interest — NO external images
   - FontAwesome icons only (import via CDN: https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css)
   - Slide titles always Top-Left position
   - Maximum 60 words per slide
   - Use abstract geometric shapes (circles, lines, polygons) as decorative elements
   - No JavaScript

5. YouTube Rules (only when YouTube data is provided):
   - Use <img src="{{YOUTUBE_1_THUMB}}" style="width:100%;border-radius:12px;object-fit:cover"> 
   - Wrap in <a href="{{YOUTUBE_1_URL}}" target="_blank">
   - Same pattern for {{YOUTUBE_2_THUMB}} and {{YOUTUBE_2_URL}}
   - Create a dedicated "Resources" slide for YouTube content

OUTPUT FORMAT:
- Single HTML block with CSS in <style> tag and slides in <body>
- No markdown fences, no explanations
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

YouTube Videos:
{youtube_links}

Generate 10-12 slides. Make it visually stunning using CSS gradients and SVG shapes.
Do NOT use any external image URLs — only CSS, SVG, and FontAwesome for visuals.
"""


def generate_html_slides(insights: MeetingInsights,
                         include_youtube: bool = False) -> str:
    """
    Generate HTML slide deck — pure CSS/SVG visuals, no external images.
    YouTube thumbnails embedded as base64 when requested.

    Args:
        insights:         Structured insights from analyse_transcript().
        include_youtube:  Whether to include YouTube video thumbnails.

    Returns:
        Complete HTML string ready for download.
    """
    from src.utils.youtube_search import search_youtube

    # ── YouTube ───────────────────────────────────────────────────────────────
    youtube_links = "None"
    youtube_map   = {}

    if include_youtube and insights.content_type != "Meeting":
        yt_queries = []
        if insights.key_points:
            yt_queries.append(insights.key_points[0][:80])
        if insights.key_concepts:
            yt_queries.append(insights.key_concepts[0].concept)

        videos = []
        for q in yt_queries:
            results = search_youtube(q, max_results=1)
            videos.extend(results)
            if len(videos) >= 2:
                break

        if videos:
            youtube_links = "\n".join(
                f"- {v['title']}: {v['url']}"
                for v in videos
            )
            for i, v in enumerate(videos[:2], 1):
                youtube_map[f"YOUTUBE_{i}_URL"]   = v["url"]
                youtube_map[f"YOUTUBE_{i}_THUMB"] = v["thumbnail"]

    # ── Format content ────────────────────────────────────────────────────────
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
        max_tokens=16000,
        system=_SYSTEM,
        messages=[{
            "role": "user",
            "content": _HUMAN.format(
                title=insights.title,
                content_type=insights.content_type,
                sentiment=insights.sentiment,
                summary=insights.summary,
                key_points=key_points   or "None",
                key_concepts=key_concepts or "None",
                examples=examples       or "None",
                action_items=action_items or "None",
                key_decisions=decisions  or "None",
                open_questions=questions or "None",
                youtube_links=youtube_links,
            ),
        }],
    )

    html = message.content[0].text.strip()

    if html.startswith("```"):
        html = html.split("\n", 1)[1]
    if html.endswith("```"):
        html = html.rsplit("```", 1)[0]

    html = html.strip()

    # ── Inject YouTube base64 thumbnails ──────────────────────────────────────
    for key, value in youtube_map.items():
        if key.endswith("_THUMB"):
            b64 = _fetch_as_base64(value)
            replacement = b64 if b64 else value
            html = html.replace("{{" + key + "}}", replacement)
        else:
            html = html.replace("{{" + key + "}}", value)

    # ── Remove any stray placeholders ─────────────────────────────────────────
    html = re.sub(r'\{\{[^}]+\}\}', '', html)

    return html