from app.cart import apply_coupon


def test_invalid_coupon_returns_error():
    result = apply_coupon(100, "WELCOME50")
    assert result["status"] == 400
    assert "error" in result
