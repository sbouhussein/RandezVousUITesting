import shutil
import subprocess
from datetime import timedelta
from pathlib import Path

import pytest

from helpers.ios import feed_data_helper as feed_data
from helpers.ios.firebase_cleanup_helper import cleanup_user_data


@pytest.fixture(autouse=True)
def feed_cleanup():
    """Clears the test user's Photo flags before the test and deletes the feed posts it authored during the test, pass or fail."""
    since = feed_data.utc_now() - timedelta(seconds=10)  # margin for sim-vs-server clock skew
    feed_data.clear_photo_submission()
    yield
    removed = feed_data.delete_feed_posts_since(since=since)
    feed_data.clear_photo_submission()
    print(f"Feed cleanup: removed {removed} post(s) authored during the test")


@pytest.fixture
def other_user_cleanup():
    """Resets a second account's quest history, grant and leaderboard row before and after the test."""
    cleanup_user_data(target_email=feed_data.OTHER_EMAIL)
    yield
    cleanup_user_data(target_email=feed_data.OTHER_EMAIL)


@pytest.fixture
def distinct_photo(request, seed_simulator_photos, tmp_path):
    """Adds a fresh copy of fixtures/private_photo.png as the newest image (the picker sorts by file creation date) and returns its path."""
    path = str(tmp_path / "private_photo.png")
    shutil.copyfile(Path(__file__).resolve().parents[3] / "fixtures" / "private_photo.png", path)
    subprocess.run(["xcrun", "simctl", "addmedia", request.config.getoption("--udid"), path],
                   capture_output=True, text=True, check=True)
    return path
