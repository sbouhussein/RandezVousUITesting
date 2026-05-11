from firebase_admin import auth, firestore

def cleanup_user_data(uid):
    db = firestore.client()
    # Your deletion logic here...
    try:
        db.collection("Users").document(uid).delete()
    except Exception as e:
        print(f"Firestore delete skipped: {e}")