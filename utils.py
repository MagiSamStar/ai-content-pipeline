import re
from datetime import datetime


def slugify(text: str) -> str:
    """Convert text into a safe filename slug."""

    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", "_", text)

    return text.strip("_")


def create_run_id(source_text: str) -> str:
    """
    Create a readable unique ID for a reading.

    Example:
    libra_dark_moon_9_of_disks_20261008_182445
    """

    text = source_text.lower()

    card_match = re.search(
        r"\b(ace|2|3|4|5|6|7|8|9|10|page|knight|queen|prince|princess|the\s+\w+)"
        r"\s+(?:of\s+)?"
        r"(disks|wands|cups|swords|pentacles)\b",
        text,
        re.IGNORECASE
    )

    moon_match = re.search(
        r"\b(libra|scorpio|aries|taurus|gemini|cancer|leo|virgo|"
        r"sagittarius|capricorn|aquarius|pisces)"
        r"\s+(dark\s+moon|new\s+moon|full\s+moon)\b",
        text,
        re.IGNORECASE
    )

    parts = []

    if moon_match:
        parts.append(slugify(moon_match.group(0)))

    if card_match:
        parts.append(slugify(card_match.group(0)))

    if not parts:
        parts.append("mystic_samstar_reading")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    return f"{'_'.join(parts)}_{timestamp}"