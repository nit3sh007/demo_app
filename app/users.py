import hashlib

# Emails are stored normalized to lowercase.
USERS = {
    "alice@example.com": {"id": 1, "password_hash": hashlib.sha256(b"secret123").hexdigest()},
}


def find_user_by_email(email):
    return USERS.get(email)
