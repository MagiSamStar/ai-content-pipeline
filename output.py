from pathlib import Path
from datetime import datetime



def save_content_package(reading, content, filename):
    """
    Save the complete ReadingPackage + ContentPackage
    as a Markdown file.
    """

    output_dir = Path("readings")
    output_dir.mkdir(exist_ok=True)
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"mystic_samstar_reading_{timestamp}.md"
        
    if not filename.endswith(".md"):
        filename += ".md"

    output_path = output_dir / filename

    markdown = f"""# 🔮 Mystic SamStar Reading & Content Package

# 🌙 READING

## Cleaned Reading

{reading.cleaned_reading}

---

## Summary

{reading.summary}

---

## Core Themes

"""

    for theme in reading.core_themes:
        markdown += f"- {theme}\n"

    markdown += """

---

## Key Messages

"""

    for message in reading.key_messages:
        markdown += f"- {message}\n"

    markdown += f"""

---

## Spiritual Guidance

    {reading.spiritual_guidance}

---

# 📱 CONTENT PACKAGE

## Theme

    {content.theme}

## Energy Summary

    {content.energy_summary}

## Self-Reflection

    {content.self_reflection}

## Chakrascopes

"""

    for chakra in content.chakrascopes:
        markdown += f"""### {chakra.chakra}

**Energy:** 
{chakra.energy}

**Meaning:**  
{chakra.meaning}

**Reflection:**  
{chakra.reflection}


"""


    markdown += f""" 
## Hook

{content.hook}

## Quotes

"""

    for quote in content.quotes:
        markdown += f"- {quote}\n"

    markdown += f"""

## Visual Concept

    {content.visual_concept}

"""

    output_path.write_text(markdown, encoding="utf-8")

    print(f"📄 Reading & content package saved to: {output_path}")

    return output_path
