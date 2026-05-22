from firebase_admin import auth, firestore


def cleanup_user_data(target_username=None, target_email=None):
    db = firestore.client()
    if target_username:
        docs = db.collection("Users").where("username", "==", target_username).stream()

        found = False
        for doc in docs:
            found = True
            uid = doc.id
            doc_ref = db.collection("Users").document(uid)

            doc_ref.update({
                "username": firestore.DELETE_FIELD,
                "questHist": firestore.DELETE_FIELD
            })

            print(f"Fields 'username' and 'questHist' wiped for UID: {uid}")

        if not found:
            print(f"Could not find username '{target_username}' to reset.")

    if target_email:
        try:
            user = auth.get_user_by_email(target_email)
            uid = user.uid
            print(f"Found UID for {target_email}: {uid}")

            doc_ref = db.collection("Users").document(uid)
            doc_ref.update({
                "questHist": firestore.DELETE_FIELD
            })

            print(f"Successfully cleared 'questHist' for: {target_email}")

        except auth.UserNotFoundError:
            print(f"No Auth account found for email: {target_email}")
        except Exception as e:
            print(f"Error cleaning up data for {target_email}: {e}")

