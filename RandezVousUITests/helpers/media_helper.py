import os
from pathlib import Path
import base64


def get_base64_image(filename, folder_name="photos"):
    """Reads an image from a dynamic folder location."""

    project_root = Path(__file__).resolve().parent.parent
    image_path = project_root / "photos" / folder_name / filename

    if not image_path.exists():
        raise FileNotFoundError(f"Image not found at: {image_path}")

    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_simulator_path(filename="test_image.jpg"):
    sim_udid = os.getenv("02702BB3-0AE0-4167-9651-39F68787A375")
    return f"/Users/{os.getlogin()}/Library/Developer/CoreSimulator/Devices/{sim_udid}/data/Media/DCIM/100APPLE/{filename}"