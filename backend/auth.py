import os
from dataclasses import dataclass
from fastapi import Header, HTTPException

import firebase_admin
from firebase_admin import auth, credentials


_initialized = False
def _init_app():
    global _initialized
    if _initialized:
        return
    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path or not os.path.exists(cred_path):
        raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS not set or file not found")
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {
        'projectId': os.environ.get('FIREBASE_PROJECT_ID')
    })
    _initialized = True


@dataclass
class User:
    uid: str
    email: str | None


def verify_id_token(authorization: str = Header(None)) -> User:
    _init_app()
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1]
    try:
        decoded = auth.verify_id_token(token)
        return User(uid=decoded.get('uid'), email=decoded.get('email'))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid ID token")


