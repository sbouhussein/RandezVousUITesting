from firebase_admin import auth, firestore


def cleanup_user_data(target_username=None, target_email=None, target_score=None):
    db = firestore.client()

    if target_username:
        docs = db.collection("Users").where("username", "==", target_username).stream()

        found = False
        for doc in docs:
            found = True
            uid = doc.id
            doc_ref = db.collection("Users").document(uid)

            update_data = {
                "username": firestore.DELETE_FIELD,
                "questHist": firestore.DELETE_FIELD
            }

            if target_score is not None:
                update_data["score"] = target_score

            doc_ref.update(update_data)

            score_msg = f" and score reset to {target_score}" if target_score is not None else ""
            print(f"Fields 'username' and 'questHist' wiped{score_msg} for UID: {uid}")

        if not found:
            print(f"Could not find username '{target_username}' to reset.")

    if target_email:
        try:
            user = auth.get_user_by_email(target_email)
            uid = user.uid
            print(f"Found UID for {target_email}: {uid}")

            doc_ref = db.collection("Users").document(uid)

            update_data = {
                "questHist": firestore.DELETE_FIELD
            }

            if target_score is not None:
                update_data["score"] = target_score

            doc_ref.update(update_data)

            score_msg = f" and score reset to {target_score}" if target_score is not None else ""
            print(f"Successfully cleared 'questHist'{score_msg} for: {target_email}")

        except auth.UserNotFoundError:
            print(f"No Auth account found for email: {target_email}")
        except Exception as e:
            print(f"Error cleaning up data for {target_email}: {e}")

