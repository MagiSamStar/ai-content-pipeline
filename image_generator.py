import base64
from pathlib import Path
from datetime import datetime

from openai import OpenAI


# -----------------------------
# Output Directory
# -----------------------------

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs" / "images"


# -----------------------------
# Image Generator
# -----------------------------

def generate_image(prompt: str, name: str = "generated_image") -> str:
    """
    Generate an image and save it locally.

    A timestamp is added to the filename so
    existing images are never overwritten.

    Returns the path to the generated image.
    """

    client = OpenAI()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    result = client.images.generate(
        model="gpt-image-2.5-sunburst",
        prompt=prompt,
    )

    image_base64 = result.data[0].b64_json

    image_bytes = base64.b64decode(image_base64)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"{name}_{timestamp}.png"

    output_path = OUTPUT_DIR / filename

    with open(output_path, "wb") as f:
        f.write(image_bytes)

    return str(output_path)
