def format_content(content):
    output = []

    output.append("=" * 60)
    output.append("        MYSTIC SAMSTAR CONTENT")
    output.append("=" * 60)

    output.append("\nTHEME")
    output.append(content.theme)

    output.append("\nHOOK")
    output.append(content.hook)

    output.append("\nENERGY SUMMARY")
    output.append(content.energy_summary)

    output.append("\nSELF-REFLECTION")
    for i, reflection in enumerate(content.self_reflection, 1):
        output.append(f"{i}. {reflection}")

    output.append("\nCHAKRASCOPE")
    for i, scope in enumerate(content.chakrascopes, 1):
        output.append(f"\n{i}. {scope.chakra}")
        output.append(f"Energy: {scope.energy}")
        output.append(f"Meaning: {scope.meaning}")
        output.append(f"Reflection: {scope.reflection}")

    output.append("\nQUOTES")
    for i, quote in enumerate(content.quotes, 1):
        output.append(f"{i}. {quote}")

    output.append("\nCAPTION")
    output.append(content.caption)

    output.append("\nHASHTAGS")
    output.append(" ".join(content.hashtags))

    output.append("\nVISUAL CONCEPT")
    output.append(content.visual_concept)

    output.append("\n" + "=" * 60)

    return "\n".join(output)

def format_visual(visual):
    output = []

    output.append("=" * 60)
    output.append("        MYSTIC SAMSTAR VISUAL")
    output.append("=" * 60)

    output.append("\nVISUAL CONCEPT")
    output.append(visual.visual_concept)

    output.append("\nIMAGE PROMPT")
    output.append(visual.image_prompt)

    output.append("\nVIDEO PROMPT")
    output.append(visual.video_prompt)

    output.append("\nASPECT RATIO")
    output.append(visual.aspect_ratio)

    output.append("\nDURATION")
    output.append(f"{visual.duration} seconds")

    output.append("\nRECOMMENDED MODEL")
    output.append(visual.recommended_model)

    output.append("\n" + "=" * 60)

    return "\n".join(output)

def format_reading(reading):
    output = []

    output.append("=" * 60)
    output.append("        MYSTIC SAMSTAR READING")
    output.append("=" * 60)

    output.append("\nCLEANED READING")
    output.append(reading.cleaned_reading)

    output.append("\nSUMMARY")
    output.append(reading.summary)

    output.append("\nCORE THEMES")
    for theme in reading.core_themes:
        output.append(f"• {theme}")

    output.append("\nKEY MESSAGES")
    for message in reading.key_messages:
        output.append(f"• {message}")

    output.append("\nSPIRITUAL GUIDANCE")
    output.append(reading.spiritual_guidance)

    output.append("\n" + "=" * 60)

    return "\n".join(output)