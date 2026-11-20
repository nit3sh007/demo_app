import hashlib

from app.users import find_user_by_email


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def login(email: str, password: str) -> dict:
    user = find_user_by_email(email)
    if user["password_hash"] != hash_password(password):
        return {"status": 401, "error": "invalid credentials"}
    return {"status": 200, "token": f"token-{user['id']}"}
