"""
core/analyser.py
=================
Extracts structured insights from any meeting or learning content.
Auto-detects content type and adapts extraction accordingly.
Uses Claude claude-sonnet-4-5 via LangChain + PydanticOutputParser.
"""

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


# ── Output schema ─────────────────────────────────────────────────────────────

class ActionItem(BaseModel):
    owner: str = Field(description="Person responsible (or 'Unassigned')")
    task: str = Field(description="Clear, verb-first task description")
    deadline: str = Field(description="Deadline if mentioned, else 'TBD'")


class KeyConcept(BaseModel):
    concept: str = Field(description="Name or title of the concept")
    explanation: str = Field(description="Detailed explanation in 2-4 sentences")


class Example(BaseModel):
    context: str = Field(description="What the example illustrates")
    description: str = Field(description="Full description of the example in 2-3 sentences")


class MeetingInsights(BaseModel):
    title: str = Field(description="Short descriptive title inferred from content")
    content_type: str = Field(description="One of: Meeting, Class, Webinar, Presentation")
    summary: str = Field(description="Comprehensive summary in 8-10 sentences covering all major points discussed")
    sentiment: str = Field(description="Overall tone: Productive / Neutral / Tense / Engaging / Informative")

    # Meeting fields
    action_items: list[ActionItem] = Field(default=[], description="Action items (for Meeting type only)")
    key_decisions: list[str] = Field(default=[], description="Decisions made (for Meeting type only)")
    open_questions: list[str] = Field(default=[], description="Unresolved questions (for Meeting type only)")

    # Learning fields
    key_points: list[str] = Field(default=[], description="Main takeaways learned (for Class/Webinar/Presentation, minimum 5, each 2-3 sentences long)")
    key_concepts: list[KeyConcept] = Field(default=[], description="Core concepts explained (for Class/Webinar/Presentation, minimum 4)")
    examples: list[Example] = Field(default=[], description="Real examples mentioned (for Class/Webinar/Presentation, minimum 3)")


# ── Prompt ────────────────────────────────────────────────────────────────────

_SYSTEM = """You are an expert content analyst.
Always respond in the same language as the transcript.
First, classify the content type: Meeting, Class, Webinar, or Presentation.

For MEETING content: extract action items with clear owners and deadlines, key decisions made, and open questions.

For CLASS/WEBINAR/PRESENTATION content:
- Extract minimum 5 key points learned, each explained in 2-3 sentences
- Extract minimum 4 key concepts with detailed explanations
- Extract minimum 3 concrete examples mentioned with full context
- Write a comprehensive 8-10 sentence summary covering ALL major topics

Always be specific and detailed. Never be vague. Use the actual content from the transcript.
{format_instructions}"""

_HUMAN = """TRANSCRIPT:
{transcript}"""


# ── Main function ─────────────────────────────────────────────────────────────

def analyse_transcript(transcript: str) -> MeetingInsights:
    """
    Analyse transcript and return structured insights adapted to content type.

    Args:
        transcript: Full transcript text from Whisper.

    Returns:
        MeetingInsights Pydantic model instance.

    Raises:
        RuntimeError: LLM call or parsing failure.
    """
    parser = PydanticOutputParser(pydantic_object=MeetingInsights)

    prompt = ChatPromptTemplate.from_messages([
        ("system", _SYSTEM),
        ("human", _HUMAN),
    ]).partial(format_instructions=parser.get_format_instructions())

    llm = ChatAnthropic(
        model="claude-sonnet-4-5",
        temperature=0.2,
        max_tokens=4096,
    )

    chain = prompt | llm | parser

    try:
        return chain.invoke({"transcript": transcript})
    except Exception as exc:
        raise RuntimeError(f"Analysis failed: {exc}") from exc