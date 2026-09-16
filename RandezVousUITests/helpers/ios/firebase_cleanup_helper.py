from firebase_admin import auth, firestore


def _clear_quest_residue(db, uid):
    """Deletes quest-participation residue for this uid: the QuestHist and
    questGrants subcollection docs, plus any Organizations/{orgId}/leaders/{uid}
    leaderboard entry, across every org. These are test-run byproducts of
    joining/completing quests, not user profile data -- nothing here touches
    username, email, icon, or anything else on the Users/{uid} doc itself.

    A stale doc in either subcollection is what caused the join-race bug we
    hit earlier: /api/quest/join is idempotent on an existing questGrants
    doc, so a leftover grant from a prior run makes a test's own "join" a
    no-op that never rewrites questHist, silently breaking any assertion
    that depends on a fresh join having happened.
    """
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

