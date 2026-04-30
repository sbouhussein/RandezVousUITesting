import argparse
from firebase_admin_client import get_auth, get_db


def delete_account(uid: str):
    get_auth().delete_user(uid)
    get_db().collection("Users").document(uid).delete()
    print(f"Deleted auth and Firestore record for {uid}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--uid", required=True, help="Firebase UID to delete")
    args = parser.parse_args()
    delete_account(args.uid)
