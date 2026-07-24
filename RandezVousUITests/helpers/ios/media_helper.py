from datetime import datetime
import subprocess
import os
import time
import piexif
from PIL import Image


def push_image_to_simulator_gallery(local_image_path):
    """ Injects an image directly into the booted iOS Simulator's Camera Roll."""
    absolute_path = os.path.abspath(local_image_path)

    if not os.path.exists(absolute_path):
        raise FileNotFoundError(f"Could not find test image at: {absolute_path}")

    command = f"xcrun simctl addmedia booted '{absolute_path}'"

    try:
        subprocess.run(command, shell=True, check=True)
        print(f"Successfully pushed {absolute_path} to Simulator Camera Roll")
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to push image to simulator. Is it booted? Error: {e}")


def make_image_recent(local_image_path):
    """
    Forcefully injects the current date and time into the EXIF metadata
    and updates OS-level timestamps to fool strict iOS validations.
    """
    if not os.path.exists(local_image_path):
        raise FileNotFoundError(f"Could not find test image at: {local_image_path}")

    with Image.open(local_image_path) as img:
        clean_img = img.convert('RGB')
        clean_img.save(local_image_path, format='JPEG')

    now_str = datetime.now().strftime("%Y:%m:%d %H:%M:%S")

    exif_dict = {"0th": {}, "Exif": {}}

    exif_dict["0th"][piexif.ImageIFD.DateTime] = now_str.encode('utf-8')
    exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = now_str.encode('utf-8')
    exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = now_str.encode('utf-8')

    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, local_image_path)

    current_time = time.time()
    os.utime(local_image_path, (current_time, current_time))

    print(f"Injected current EXIF timestamp ({now_str}) into {local_image_path}.")