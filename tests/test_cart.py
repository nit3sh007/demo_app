from app.cart import apply_coupon


def test_valid_coupon():
    assert apply_coupon(100, "SAVE10")["total"] == 90.0


def test_coupon_is_case_insensitive():
    assert apply_coupon(200, "save20")["total"] == 160.0
