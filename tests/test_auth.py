from app.auth import login


def test_login_success():
    assert login("alice@example.com", "secret123")["status"] == 200


def test_login_wrong_password():
    assert login("alice@example.com", "nope")["status"] == 401
