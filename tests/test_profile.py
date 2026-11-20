from app.profile import display_name


def test_with_middle_name():
    assert display_name("Ravi", "kumar", "Rao") == "Ravi K. Rao"
