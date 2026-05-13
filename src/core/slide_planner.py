"""
core/slide_planner.py
======================
Uses Claude to plan a professional presentation from MeetingInsights.
Applies design rules: 6x6, 10/20/30, visual storytelling over text.
Returns a structured SlidesPlan consumed by slides_generator.py.
"""

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from src.core.analyser import MeetingInsights

load_dotenv()


# ── Output schema ─────────────────────────────────────────────────────────────

class SlideContent(BaseModel):
    slide_number: int = Field(description="Slide number starting from 1")
    title: str = Field(description="Slide title — max 6 words, bold and clear")
    layout: str = Field(description="One of: cover, summary, bullets, cards, image_left, youtube, action_items")
    bullets: list[str] = Field(default=[], description="Max 6 bullets, max 6 words each. Empty for cover/youtube layouts")
    cards: list[dict] = Field(default=[], description="List of {title, body} dicts for cards layout")
    image_query: str = Field(default="", description="Unsplash search query for this slide's image. Empty if no image needed")
    speaker_notes: str = Field(description="2-3 sentences of talking points for the presenter")
    visual_suggestion: str = Field(description="Brief suggestion for visual element or emphasis")


class SlidesPlan(BaseModel):
    title: str = Field(description="Presentation title")
    color_theme: str = Field(description="One of: cyan, purple, green, amber — based on content type")
    total_slides: int = Field(description="Total number of slides")
    slides: list[SlideContent] = Field(description="All slides in order")


# ── Prompt ────────────────────────────────────────────────────────────────────

_SYSTEM = """
<Role>
You are an expert Presentation Designer and Communication Strategist with decades of experience 
creating compelling presentations for Fortune 500 companies, TED talks, and startup pitches.
Your expertise combines visual design principles, storytelling techniques, and audience psychology.
</Role>

<Context>
You will receive structured insights extracted from a meeting or class transcript.
Your job is to transform these insights into a professional slide presentation plan.
The plan will be rendered automatically into a PowerPoint file.
Always respond in the same language as the content provided.
</Context>

<Instructions>
1. Create a presentation with maximum 12 slides following this structure:
   - Slide 1: Cover (title, type, tone)
   - Slide 2: Executive Summary
   - Slides 3-10: Main content (key points, concepts, examples, decisions)
   - Last slide: Closing impact (key takeaway or next steps)

2. For each slide decide:
   - The best layout: cover / summary / bullets / cards / image_left / action_items / youtube
   - Whether an image adds value (only suggest image_query when it genuinely helps)
   - Concise bullets following the 6x6 rule (max 6 bullets, max 6 words each)
   - Cards layout for complex concepts that benefit from visual separation
   - Speaker notes with 2-3 sentences of talking points

3. Apply these design principles:
   - 10/20/30 rule: max 10 content slides, 20 min delivery, 30pt font minimum
   - 6x6 rule: max 6 bullets per slide, max 6 words per bullet
   - Visual storytelling: prefer cards and visuals over text walls
   - One key message per slide — never overload
   - Strong opening, strong closing

4. Content type rules:
   - Meeting: focus on decisions, action items, next steps. Never use youtube layout.
   - Class/Webinar/Presentation: focus on learning, concepts, examples.

5. YouTube layout rule:
   - Only include a youtube layout slide if Include YouTube slide is "Yes"
   - If yes, add exactly ONE slide with layout: youtube near the end
   - If no, never include youtube layout under any circumstances
</Instructions>

<Constraints>
- Maximum 12 slides total
- Maximum 6 bullets per slide
- Maximum 6 words per bullet point
- Minimum font equivalent: keep text concise enough for 30pt
- No text walls — if content is long, use cards layout
- Image queries only when visual genuinely adds context
- Speaker notes in same language as content
</Constraints>

{format_instructions}
"""

_HUMAN = """
Content Type: {content_type}
Title: {title}
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

Include YouTube slide: {include_youtube}
"""


# ── Main function ─────────────────────────────────────────────────────────────

def plan_slides(insights: MeetingInsights, include_youtube: bool = False) -> SlidesPlan:
    """
    Generate a professional slide plan from MeetingInsights.

    Args:
        insights:         Structured insights from analyse_transcript().
        include_youtube:  Whether to include a YouTube resources slide.

    Returns:
        SlidesPlan with slide-by-slide content and layout decisions.

    Raises:
        RuntimeError: LLM call or parsing failure.
    """
    parser = PydanticOutputParser(pydantic_object=SlidesPlan)

    prompt = ChatPromptTemplate.from_messages([
        ("system", _SYSTEM),
        ("human", _HUMAN),
    ]).partial(format_instructions=parser.get_format_instructions())

    llm = ChatAnthropic(
        model="claude-sonnet-4-5",
        temperature=0.3,
        max_tokens=4096,
    )

    chain = prompt | llm | parser

    key_points   = "\n".join(f"- {p}" for p in insights.key_points)
    key_concepts = "\n".join(f"- {c.concept}: {c.explanation}" for c in insights.key_concepts)
    examples     = "\n".join(f"- {e.context}: {e.description}" for e in insights.examples)
    action_items = "\n".join(f"- [{a.owner}] {a.task} (Due: {a.deadline})" for a in insights.action_items)
    decisions    = "\n".join(f"- {d}" for d in insights.key_decisions)
    questions    = "\n".join(f"- {q}" for q in insights.open_questions)

    youtube_instruction = (
        "Yes — include exactly ONE slide with layout: youtube near the end of the presentation"
        if include_youtube else
        "No — do not include any youtube layout slides under any circumstances"
    )

    try:
        return chain.invoke({
            "content_type":    insights.content_type,
            "title":           insights.title,
            "sentiment":       insights.sentiment,
            "summary":         insights.summary,
            "key_points":      key_points or "None",
            "key_concepts":    key_concepts or "None",
            "examples":        examples or "None",
            "action_items":    action_items or "None",
            "key_decisions":   decisions or "None",
            "open_questions":  questions or "None",
            "include_youtube": youtube_instruction,
        })
    except Exception as exc:
        raise RuntimeError(f"Slide planning failed: {exc}") from exc