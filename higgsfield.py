import higgsfield_client
from visual_agent import VisualPackage




# -----------------------------
# Higgsfield
# -----------------------------

def generate_video(visual_package: VisualPackage):

    result = higgsfield_client.subscribe(
        "bytedance/seedance-2.0/text-to-video",
        arguments={
            "prompt": visual_package.video_prompt,
            "duration": visual_package.duration,
            "resolution": "720p",
            "aspect_ratio": visual_package.aspect_ratio,
            "aigc_watermark": False,
        },
    )

    return result



