from pydantic import BaseModel, Field
from typing import List
from langchain_openai import ChatOpenAI
from pathlib import Path


llm = ChatOpenAI(
    model="gpt-6-luna",
    temperature=1
)


# -----------------------------
# Brand Guide
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent

brand_guide = (BASE_DIR / "mystic_samstar_brand.md").read_text(
    encoding="utf-8"
)
bible = (BASE_DIR / "mystic_samstar_bible.md").read_text(
    encoding="utf-8"
)
# -----------------------------
# Structured Output
# -----------------------------

class ReadingPackage(BaseModel):
    cleaned_reading: str
    summary: str
    core_themes: List[str] = Field(
        min_length=4,
        max_length=6
    )
    key_messages: List[str] = Field(
        min_length=3,
        max_length=5
    )
    spiritual_guidance: str


structured_llm = llm.with_structured_output(
    ReadingPackage
)


# -----------------------------
# Reading Agent
# -----------------------------

def analyze_reading(state):

    result = structured_llm.invoke(
    f"""
You are the Mystic SamStar Reading Editor and Interpreter.

Your job is to take SamStar's raw reading and turn it into a
clearer, polished version while preserving SamStar's original
meaning, personality, spiritual perspective, and intuitive voice.

EDITING RULES:

- Clean up grammar, spelling, punctuation, and awkward wording.
- Fix obvious typos and speech-to-text errors.
- Break up overly long or confusing sentences.
- Improve readability and flow.
- Preserve SamStar's natural conversational and spiritual voice.
- Keep personal experiences and intuitive impressions intact.
- Do not make the writing sound overly formal, academic, or generic.
- Do not replace SamStar's wording with generic AI spiritual language.
- Do not add new interpretations that are not supported by the reading.
- Do not invent spiritual experiences, messages, channeling, predictions,
  or tarot meanings.
- Preserve the original sequence and important details of the reading.
- When SamStar's wording is imperfect but the intended meaning is clear,
  improve the wording without changing the meaning.

Think of this as a LIGHT EDIT, not a rewrite.

SOURCE READING:
{state["source_text"]}

MYSTIC SAMSTAR SPIRITUAL BIBLE:
{bible}

BRAND GUIDE:
{brand_guide}

Return the completed ReadingPackage.
"""
)

    return {
    "reading_package": result
    }

# if __name__ == "__main__":

#     test_state = {
#         "source_text": """
#         Shadow Reflections:

# We have Self- Doubt



# As we go through deep transformation, we may come into conflict with self-doubt; self-doubt dims out clarity and creates internal confusion and often bends our perception of what's in front of us and what we know is true. This is about trust and our own inner courage to prevail and move forward; this is indeed a fight with ourselves.  Again, we have lightning around a lightbulb this time. So there is intuitive clarity happening, sudden insights that are helping u see glimpses of the truth.  This may feel unfamiliar, new territory, a new path. it could be an aspect of things we doubt about ourselves and out own journey, but these glimpses are here to help you grow and transform just as the lightbulb provides the light to help navigate you through the path.  When we are in self-doubt, it's easy to get comfortable doing the wrong things that seem familiar. To see a new perspective than what we know, or break an unhealthy routine. But it's trusting and believing in ourselves that allows us to break feree from these cycles, stagnation and blocks which create the self-doubt. when we look at what actually happening and be honst we come more self aware rather then supressing it that self doubt becomes immnated with truth and claritym ehich thenm can help embdy confice and perosonal power to create the change wer need for ourselves, to trust ourselves, our own power and be the light that sheads the old, patterns, the old expectation of ourselves and others, th inetal fears that keeops up from making that move forward. when we act more from self-care and love of ourselves, we won't keep ourselves at the bottom and choose to change to take action and grow. We overcome that self-doubt, and it turns into clarity, which in turn turns into power we can act on and move with clarity, insight, and trust.



# May your soul be your guide. 
# Namaste
#         """
#     }

#     result = analyze_reading(test_state)

#     print(
#         result["reading_package"].model_dump_json(
#             indent=2
#         )
#     )