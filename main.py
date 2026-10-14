from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from pathlib import Path
from dotenv import load_dotenv
from reading_agent import analyze_reading, ReadingPackage
from canva import CanvaDesign,create_canva_design_from_image
from content_agent import ContentPackage, create_content
from visual_agent import VisualPackage, create_visual
from higgsfield import generate_video
from formatters import format_content,format_visual,format_reading
from image_generator import generate_image
from output import save_content_package
from utils import create_run_id


load_dotenv()


# -----------------------------
# Shared Graph State
# -----------------------------

class ContentState(TypedDict):
    run_id: str
    source_text: str
    reading_package: ReadingPackage | None
    content_package: ContentPackage | None
    visual_package: VisualPackage | None
    content_type: str
    general_image_path: str | None
    chakrascope_image_path: str | None
    canva_design: CanvaDesign | None
    video_result: object | None
   

#-----------------------------
# Nodes
#-----------------------------
def analyze_reading_node(state: ContentState):
    result = analyze_reading(state)

    return {
        "reading_package": result["reading_package"]
    }

def generate_image_node(state: ContentState):
    general_image_path = generate_image(
        state["visual_package"].general_image_prompt,
        name=f"{state['run_id']}_general.png"
    )
    
    chakrascope_image_path = generate_image(
        state["visual_package"].chakrascope_image_prompt,
            name=f"{state['run_id']}_chakrascope.png"
    )

    return {
        "general_image_path": general_image_path,
        "chakrascope_image_path": chakrascope_image_path

    }


def create_canva_node(state: ContentState):
    result = create_canva_design_from_image(
        image_path=state["general_image_path"],
        title=state["content_package"].theme
    )

    return {
        "canva_design": result
    }


def generate_video_node(state: ContentState):
    try:
        video = generate_video(
            state["visual_package"]
        )

        return {
            "video_result": video
        }

    except Exception as e:
        print(f"⚠️ Video generation unavailable: {e}")
        print("Continuing workflow without video.")

        return {
            "video_result": None
        }

# -----------------------------
# LangGraph
# -----------------------------


builder = StateGraph(ContentState)

builder.add_node("analyze_reading", analyze_reading_node)
builder.add_node("create_content", create_content)
builder.add_node("create_visual", create_visual)
builder.add_node("create_canva", create_canva_node)
builder.add_node("generate_video", generate_video_node)
builder.add_node("generate_image", generate_image_node)

builder.add_edge(START, "analyze_reading")
builder.add_edge("analyze_reading", "create_content")
builder.add_edge("create_content", "create_visual")
builder.add_edge("create_visual", "generate_image")
builder.add_edge("generate_image", "create_canva")
builder.add_edge("create_canva", "generate_video")
builder.add_edge("generate_video", END)

graph = builder.compile()


# -----------------------------
# Demo State
# -----------------------------
EXAMPLE_INPUT = Path(__file__).parent / "examples" / "sample_input.md"
source_text = EXAMPLE_INPUT.read_text(encoding="utf-8")

state: ContentState = {
    "run_id": create_run_id(source_text),
    "source_text": source_text,

    "reading_package": None,
    "content_package": None,
    "visual_package": None,
    "content_type": "",
    "general_image_path": None,
    "chakrascope_image_path":None,
    "canva_design": None,
    "video_result": None,
}



# -----------------------------
# Run Graph
# -----------------------------

if __name__ == "__main__":
    result = graph.invoke(state)


# -----------------------------
# Save Reading
# -----------------------------

    save_content_package(
        result["reading_package"],
        result["content_package"],
        result["run_id"]
    )

    print("\n--READING PACKAGE:")
    print(format_reading(result["reading_package"]))

    print("\n--CONTENT PACKAGE:")
    print(format_content(result["content_package"]))

    print("\n--VISUAL PACKAGE:")
    print(format_visual(result["visual_package"]))

    print("\n--VIDEO RESULT:")
    print(result["video_result"])

    print("\n--IMAGE PATHS:")
    print(result["general_image_path"])
    print(result["chakrascope_image_path"])

    print("\n--CANVA DESIGN:")
    print(result["canva_design"])

