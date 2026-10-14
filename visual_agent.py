from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

visual_guide = (BASE_DIR / "visual_reference.md").read_text(
    encoding="utf-8"
)
bible = (BASE_DIR / "mystic_samstar_bible.md").read_text(
    encoding="utf-8"
)
# -----------------------------
# LLM
# -----------------------------

llm = ChatOpenAI(
    model="gpt-5-mini",
    temperature=1
)

local_llm = ChatOllama(
    model="gemma4:e4b",
    temperature=0
)

# -----------------------------
# Structured Output
# -----------------------------

class VisualPackage(BaseModel):
    visual_concept: str
    video_prompt: str
    image_prompt: str
    general_image_prompt: str
    chakrascope_visual_concept: str
    chakrascope_image_prompt: str
    aspect_ratio: str
    duration: int = Field(ge=5, le=15)
    recommended_model: str


# -----------------------------
# Structured LLM
# -----------------------------

structured_llm = local_llm.with_structured_output(VisualPackage)




# -----------------------------
# Visual Agent
# -----------------------------

def create_visual(state):

    content = state["content_package"]

    result = structured_llm.invoke(
    f"""
You are the Mystic SamStar Visual Agent.

Your job is to translate the content package into
visual instructions for AI image generation.

You are creating TWO separate visual assets:

1. A GENERAL READING image
2. A CHAKRASCOPE image

The two images should belong to the same Mystic SamStar
visual universe, but they must represent different purposes.

The visual reference guide below is an AUTHORITATIVE
creative constraint.

Do NOT invent a different visual style.

MYSTIC SAMSTAR SPIRITUAL BIBLE:
{bible}
========================
MYSTIC SAMSTAR VISUAL GUIDE
========================

{visual_guide}

VISUAL_SAFETY_RULES = 
IMPORTANT VISUAL GUIDELINES:

Create spiritual, symbolic, artistic imagery appropriate for a general-audience
social media platform.

No sexual content.
No nudity.
No erotic or sensual posing.
No sexualized anatomy.
No fetish imagery.
No suggestive clothing or poses.

Human figures must be fully clothed and presented in a non-sexual,
non-suggestive manner.

Focus on symbolism, spirituality, tarot archetypes, cosmic imagery,
nature, energy, light, sacred geometry, mythology, and emotional themes.

========================
VISUAL STYLE REQUIREMENTS
========================

ALL generated visual concepts and image prompts MUST
follow the visual reference guide.

Pay particular attention to:

- Art style
- Character style
- Anime / painterly direction
- Retro gaming influences
- Color palette
- Lighting
- Mood
- Composition
- Recurring symbolism

Do NOT default to:

- Photorealism
- Live-action photography
- Generic cinematic photography
- Generic fantasy artwork

If the visual guide specifies an anime or stylized
art direction, explicitly include that direction
in BOTH image prompts.


========================
CHARACTER CONSISTENCY
========================

If the visual reference guide specifies a character's
identity or appearance, preserve it exactly.

Do not change the character's ethnicity, gender,
age range, or defining visual characteristics.

Do not replace specified character direction with
generic terms such as "young woman" or "person."

========================
GENERAL READING IMAGE
========================

Create a visual concept and image prompt that represents
the OVERALL reading.

The General Reading image should communicate:

- The central theme
- The overall emotional and spiritual energy
- The primary message
- Important symbolism from the reading
- The overall Mystic SamStar atmosphere

Do NOT allow one individual ChakraScope to dominate
the General Reading image.

The General Reading image should feel like the
primary visual introduction to the reading.

========================
CHAKRASCOPE IMAGE
========================

Create a separate visual concept and image prompt
specifically representing the ChakraScope information.

Use the chakra, energy, meaning, and reflection to
guide the symbolism and composition.

The ChakraScope image should have a clearer focus
on the specific energetic theme represented by
the ChakraScope.

Do NOT simply copy the General Reading image.

The ChakraScope image should feel like a companion
visual within the same Mystic SamStar visual universe.

Do not introduce spiritual, chakra, tarot, astrological,
or healing concepts that are not supported by the
provided Content Package.

========================
CONTENT PACKAGE
========================

Theme:
{content.theme}

Energy Summary:
{content.energy_summary}

Self-Reflection:
{content.self_reflection}

Chakrascopes:
{content.chakrascopes}

Hook:
{content.hook}

Quotes:
{content.quotes}

Visual Concept:
{content.visual_concept}

========================
GENERATE
========================

Create:

GENERAL READING
- A general_visual_concept
- A general_image_prompt

CHAKRASCOPE
- A chakrascope_visual_concept
- A chakrascope_image_prompt

Also provide:

- An aspect ratio

Prefer 9:16 for social media content.

Both image prompts should contain enough visual
detail for a separate image generation model to
reproduce the intended Mystic SamStar visual style.

The General Reading image and ChakraScope image
must be visually distinct while remaining
consistent with the Mystic SamStar brand.
"""
    )

    return {
        "visual_package": result
    }

# if __name__ == "__main__":
#      from content_agent import ContentPackage, ChakraScope
#      # -------------------------------- # TEST CONTENT PACKAGE # -------------------------------- 
# test_content = ContentPackage(
#     theme="Finding Your Voice: Releasing Fear and Trusting Your Inner Truth",

#     hook="What changes when you stop silencing what your Soul has been asking you to say?",

#     energy_summary=(
#         "This reading centers on releasing fear, trusting your inner truth, "
#         "and finding the courage to express what has been held within. "
#         "Transformation comes through honest self-expression, emotional "
#         "awareness, and trusting your own inner knowing."
#     ),

#     self_reflection=[
#         "What truth have you been afraid to express?",
#         "Where have you been silencing your own needs?",
#         "What would change if you trusted your inner knowing?",
#         "What emotion needs to be acknowledged rather than suppressed?"
#     ],

#     chakrascopes=[
#         ChakraScope(
#             chakra="Throat Chakra",
#             energy="Authentic expression",
#             meaning=(
#                 "The energy of the Throat Chakra asks you to communicate "
#                 "your truth honestly and release the fear of being heard."
#             ),
#             reflection="What truth is ready to be spoken?"
#         ),

#         ChakraScope(
#             chakra="Heart Chakra",
#             energy="Emotional openness",
#             meaning=(
#                 "The Heart Chakra invites compassion and emotional honesty, "
#                 "creating space to acknowledge what you truly feel."
#             ),
#             reflection="What feeling are you ready to meet with compassion?"
#         ),

#         ChakraScope(
#             chakra="Third Eye Chakra",
#             energy="Inner knowing",
#             meaning=(
#                 "The Third Eye encourages you to look beyond uncertainty "
#                 "and trust the wisdom you already carry within."
#             ),
#             reflection="What does your inner knowing already understand?"
#         )
#     ],

#     quotes=[
#         "Your truth deserves to be heard.",
#         "Your inner knowing already carries the wisdom you seek.",
#         "Compassion creates space for honest expression.",
#         "You do not have to silence yourself to find peace."
#     ],

#     caption=(
#         "May your Soul be your Guide. "
#         "Sometimes transformation begins when we finally allow ourselves "
#         "to acknowledge what we already know within. "
#         "Your truth does not need to be forced. It simply needs space "
#         "to be heard."
#     ),

#     hashtags=[
#         "#MysticSamStar",
#         "#SoulGuidance",
#         "#InnerWisdom",
#         "#AuthenticExpression",
#         "#ThroatChakra",
#         "#HeartChakra",
#         "#ThirdEyeChakra",
#         "#SoulWork"
#     ],

#     visual_concept=(
#         "A mystical anime-painterly representation of a woman discovering "
#         "the courage to express her inner truth, surrounded by symbolic "
#         "light and subtle cosmic elements. The primary visual should "
#         "focus on self-expression and inner knowing rather than depicting "
#         "all three chakras literally."
#     )
# )
#      # -------------------------------- # TEST STATE # -------------------------------- 
# test_state = { "content_package": test_content } # -------------------------------- 
#      # RUN VISUAL AGENT # -------------------------------- 
# result = create_visual(test_state) 
# visual = result["visual_package"] 

# print("==============================\n") 
# print("VISUAL AGENT TEST")
# print("VISUAL CONCEPT:") 
# print(visual.visual_concept) 
# print("\nIMAGE PROMPT:") 
# print(visual.image_prompt) 
# print("\nVIDEO PROMPT:") 
# print(visual.video_prompt) 
# print("\nASPECT RATIO:") 
# print(visual.aspect_ratio) 
# print("\nDURATION:") 
# print(visual.duration) 
# print("\nRECOMMENDED MODEL:") 
# print(visual.recommended_model)