from firebase_admin import auth, firestore


def _clear_quest_residue(db, uid):
    """Deletes the uid's QuestHist and questGrants subcollection docs and its leaderboard entry in
    every org. Leaves the Users/{uid} doc itself alone.

    /api/quest/join is a no-op on an existing questGrants doc, so a leftover grant would stop a
    test's join from rewriting questHist."""
    user_ref = db.collection("Users").document(uid)
    for subcollection in ("QuestHist", "questGrants"):
        for doc in user_ref.collection(subcollection).stream():
            doc.reference.delete()

    for org in db.collection("Organizations").stream():
        leader_ref = org.reference.collection("leaders").document(uid)
        if leader_ref.get().exists:
            leader_ref.delete()


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
            _clear_quest_residue(db, uid)

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
            _clear_quest_residue(db, uid)

            score_msg = f" and score reset to {target_score}" if target_score is not None else ""
            print(f"Successfully cleared 'questHist'{score_msg} for: {target_email}")

        except auth.UserNotFoundError:
            print(f"No Auth account found for email: {target_email}")
        except Exception as e:
            print(f"Error cleaning up data for {target_email}: {e}")

