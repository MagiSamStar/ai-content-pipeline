import base64
import requests
import json
import urllib.request
import time
from pydantic import BaseModel
from auth import get_access_token
import re

class CanvaDesign(BaseModel):
    design_id: str
    edit_url: str
    view_url: str

def wait_for_asset_upload(job_id: str) -> dict:
    """
    Wait for Canva to finish processing an uploaded asset.
    """

    for _ in range(10):

        result = get_asset_upload_job(job_id)

        status = result["job"]["status"]

        print(f"Canva upload status: {status}")

        if status == "success":
            return result

        if status == "failed":
            raise RuntimeError(
                "Canva asset upload failed."
            )

        time.sleep(2)

    raise TimeoutError(
        "Canva asset upload did not finish in time."
    )

def canva_get(path: str) -> dict:
    access_token = get_access_token()

    url = f"https://api.canva.com/rest{path}"

    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        method="GET",
    )

    with urllib.request.urlopen(
        request,
        timeout=30
    ) as response:

        response_body = response.read().decode("utf-8")

        return (
            json.loads(response_body)
            if response_body
            else {}
        )


def list_designs() -> dict:
    return canva_get("/v1/designs")


def create_design(
    title: str,
    width: int = 1080,
    height: int = 1920,
) -> dict:

    access_token = get_access_token()

    url = "https://api.canva.com/rest/v1/designs"

    payload = {
        "type": "type_and_asset",
        "design_type": {
            "type": "custom",
            "width": width,
            "height": height,
        },
        "title": title,
    }

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(
        request,
        timeout=30
    ) as response:

        response_body = response.read().decode("utf-8")

        return (
            json.loads(response_body)
            if response_body
            else {}
        )

def create_design_from_asset(
    asset_id: str,
    title: str,
    width: int = 1080,
    height: int = 1920,
) -> CanvaDesign:
    """
    Create a Canva design using an existing Canva asset.
    """

    access_token = get_access_token()

    url = (
        "https://api.canva.com/rest/v1/designs"
    )

    payload = {
        "type": "type_and_asset",
        "design_type": {
            "type": "custom",
            "width": width,
            "height": height,
        },
        "asset_id": asset_id,
        "title": title,
    }

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": (
                f"Bearer {access_token}"
            ),
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=30
        ) as response:

            response_body = (
                response.read()
                .decode("utf-8")
            )

            response_data = (
                json.loads(response_body)
                if response_body
                else {}
            )

            design = response_data["design"]

            return CanvaDesign(
                design_id=design["id"],
                edit_url=design["urls"]["edit_url"],
                view_url=design["urls"]["view_url"],
            )

    except urllib.error.HTTPError as error:

        error_body = (
            error.read()
            .decode("utf-8")
        )

        raise RuntimeError(
            f"Canva API error "
            f"{error.code}: {error_body}"
        ) from error
    
def upload_asset(file_path: str, asset_name: str) -> dict:
    """
    Upload a local image to the user's Canva library.

    Returns Canva's upload job information.
    """
    safe_name = re.sub(
    r"[^a-zA-Z0-9 _-]",
    "",
    asset_name
)

    safe_name = safe_name[:50]

    encoded_name = base64.b64encode(
    safe_name.encode("utf-8")
    ).decode("utf-8")
    
    access_token = get_access_token()

    url = (
        "https://api.canva.com/rest/v1/asset-uploads"
    )

    # Canva expects the asset name to be Base64 encoded
    encoded_name = base64.b64encode(
        asset_name.encode("utf-8")
    ).decode("utf-8")

    with open(file_path, "rb") as file:
        image_bytes = file.read()

    request = urllib.request.Request(
        url,
        data=image_bytes,
        headers={
            "Authorization": (
                f"Bearer {access_token}"
            ),
            "Content-Type": (
                "application/octet-stream"
            ),
           "Asset-Upload-Metadata": json.dumps({
    "name_base64": encoded_name
}),
        },
        method="POST",
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=60
        ) as response:

            response_body = (
                response.read()
                .decode("utf-8")
            )

            return (
                json.loads(response_body)
                if response_body
                else {}
            )

    except urllib.error.HTTPError as error:

        error_body = (
            error.read()
            .decode("utf-8")
        )

        raise RuntimeError(
            f"Canva API error "
            f"{error.code}: {error_body}"
        ) from error



def get_asset_upload_job(job_id: str) -> dict:
    """
    Check the status of a Canva asset upload job.
    """

    return canva_get(
        f"/v1/asset-uploads/{job_id}"
    )
def create_canva_design_from_image(
    image_path: str,
    title: str
) -> CanvaDesign:
    """
    Create a new Canva design based on a local image file.
    """

    # 1. Upload the image to Canva
    upload_job = upload_asset(
        image_path,
        "Mystic SamStar Image"
    )

    # 2. Get the upload job ID
    job_id = upload_job["job"]["id"]

    # 3. Wait for Canva to finish processing
    completed_job = wait_for_asset_upload(
        job_id
    )

    # 4. Get the Canva asset ID
    asset_id = completed_job["job"]["asset"]["id"]

    # 5. Create the Canva design
    return create_design_from_asset(
        asset_id=asset_id,
        title=title
    )
