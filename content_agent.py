from pydantic import BaseModel,Field, ValidationError
from typing import List
from langchain_openai import ChatOpenAI
from pathlib import Path
from formatters import format_content
from reading_agent import ReadingPackage
from langchain_ollama import ChatOllama
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
logger = logging.getLogger(__name__)


def load_guide(filename: str) -> str:
    path = BASE_DIR / filename

    try:
        return path.read_text(encoding="utf-8")

    except FileNotFoundError as exc:
        logger.error("Required guide file is missing: %s", path)
        raise RuntimeError(
            f"Required guide file not found: {filename}"
        ) from exc

    except (OSError, UnicodeDecodeError) as exc:
        logger.exception("Could not read guide file: %s", filename)
        raise RuntimeError(
            f"Could not load guide file: {filename}"
        ) from exc
# -----------------------------
# LLM
# -----------------------------

llm = ChatOpenAI(
    model="gpt-6-luna",
    temperature=1
)

local_llm = ChatOllama(
    model="gemma4:e4b",
    temperature=0
)

# -----------------------------
# Structured Output
# -----------------------------

class ChakraScope(BaseModel):
 chakra:str
 energy:str
 meaning:str
 reflection: str
 
class ContentPackage(BaseModel):
    theme: str
    hook: str
    energy_summary: str
    self_reflection: List[str] = Field(
        min_length=3,
        max_length=4
    )

    chakrascopes: List[ChakraScope] = Field(
        min_length=1,
        max_length=3
    )

    quotes: List[str] = Field(min_length=3, max_length=5)
    caption: str
    hashtags: List[str]
    visual_concept: str

class CarouselItem(BaseModel):
    img_prompt: str
    text: str
    composition: str


# Primary: local Ollama model
ollama_structured = local_llm.with_structured_output(
    ContentPackage
)

# Backup: OpenAI cloud model
openai_structured = llm.with_structured_output(
    ContentPackage
)

# Try Ollama first, then OpenAI if Ollama fails
structured_llm = ollama_structured.with_fallbacks(
    [openai_structured]
)

# -----------------------------
# Model Helper
# -----------------------------

def generate_content(prompt: str) -> ContentPackage:
    try:
        result = structured_llm.invoke(prompt)
        return result

    except Exception:
        logger.exception("Content generation failed.")
        raise

# -----------------------------
# Content Agent
# -----------------------------

def create_content(state):
    # Step 1: Validate incoming state
    if not isinstance(state, dict):
        raise TypeError("Content agent state must be a dictionary.")

    reading = state.get("reading_package")

    if reading is None:
        raise ValueError(
            "Missing 'reading_package' in content agent state."
        )
    
# Step 2: Validate reading package fields
    required_fields = [
        "cleaned_reading",
        "summary",
        "core_themes",
        "key_messages",
        "spiritual_guidance",
    ]

    missing_fields = [
        field for field in required_fields
        if not hasattr(reading, field)
        or getattr(reading, field) is None
    ]

    if missing_fields:
        raise ValueError(
            f"Reading package is missing fields: {missing_fields}"
        )

    # Step 3: Load your guides
    brand_guide = load_guide("mystic_samstar_brand.md")
    visual_guide = load_guide("visual_reference.md")
    bible = load_guide("mystic_samstar_bible.md")

    # Step 4: Continue with your existing prompt and LLM call
    prompt = f"""
You are the Mystic SamStar Content Agent.

Your job is to transform the provided Reading Package into
social media content while preserving the meaning and
spiritual perspective of the reading.

IMPORTANT:
The Mystic SamStar brand guide and visual reference guide
below are authoritative creative instructions.

Do not replace them with your own default style.

========================
MYSTIC SAMSTAR BIBLE GUIDE
========================

{bible}

========================
MYSTIC SAMSTAR BRAND GUIDE
========================

{brand_guide}

========================
MYSTIC SAMSTAR VISUAL GUIDE
========================

{visual_guide}

VISUAL DIRECTION RULES:

- The visual guide is a creative constraint, not a suggestion.
- Follow its specified art style.
- Follow its character direction.
- Follow its color palette.
- Follow its lighting direction.
- Follow its mood and atmosphere.
- Follow its composition preferences.
- Use its recurring symbolism when appropriate.
- Do NOT default to photorealism.
- Do NOT default to generic cinematic photography.
- Do NOT replace the specified anime, painterly, or retro-gaming
  aesthetic with your own interpretation.

The visual_concept you generate MUST explicitly reflect the
visual guide.

========================
READING PACKAGE
========================

CLEANED READING:
{reading.cleaned_reading}

SUMMARY:
{reading.summary}

CORE THEMES:
{reading.core_themes}


KEY MESSAGES:
{reading.key_messages}

SPIRITUAL GUIDANCE:
{reading.spiritual_guidance}

========================
CONTENT REQUIREMENTS
========================

Generate:

- A central theme for the reading
- An engaging hook
- An energy summary describing the overall energetic message
- 3–4 self-reflection prompts based directly on the reading
- 1–3 chakrascopes based on chakra energies genuinely present in the reading
- 3–5 meaningful quotes derived from the reading
- An Instagram caption
- Relevant hashtags
- A visual concept for AI image/video generation

The content should be:

- Engaging
- Authentic
- Spiritual
- Reflective
- Compassionate
- Appropriate for Instagram and short-form video

The visual concept should describe how the reading is
represented visually while remaining faithful to the
Mystic SamStar visual guide.

"""
    result = generate_content(prompt)

    return {
        "content_package": result
    }

# if __name__ == "__main__":

#     test_reading = ReadingPackage(
#         cleaned_reading="Self-doubt can create confusion during transformation...",
#         summary="A period of transformation is asking us to trust ourselves.",
#         core_themes=[
#             "Self-doubt",
#             "Clarity",
#             "Transformation",
#             "Inner courage"
#         ],
#         key_messages=[
#             "Self-doubt can distort our perception.",
#             "Transformation requires self-trust.",
#             "Compassion can help us move through uncertainty."
#         ],
#         spiritual_guidance="Practice compassion toward yourself and trust your inner wisdom."
#     )

#     test_state = {
#         "reading_package": test_reading,
#         "source_text": test_reading.cleaned_reading
#     }

#     result = create_content(test_state)

#     content = result["content_package"]

#     print(format_content(content))