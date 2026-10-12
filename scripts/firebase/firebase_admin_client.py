import os
from pathlib import Path
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, auth, firestore

_REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_REPO_ROOT / ".env")

_app = None


def _init():
    global _app
    if _app is not None:
        return
    # Defaults to the randezvous-qa key -- same one conftest.py's firebase_init uses.
    key_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY_PATH", "private/service-account-key-qa.json")
    cred = credentials.Certificate(_REPO_ROOT / key_path)
    _app = firebase_admin.initialize_app(cred)


def get_auth():
    _init()
    return auth


def get_db():
    _init()
    return firestore.client()
