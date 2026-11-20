COUPONS = {"SAVE10": 10, "SAVE20": 20}  # percent off


def apply_coupon(total: float, code: str) -> dict:
    # Normalise the coupon code
    code_clean = code.strip().upper()
    percent = COUPONS.get(code_clean)
    if percent is None:
        # Return a client error for unknown coupon codes
        return {"status": 400, "error": "Invalid coupon code"}
    new_total = round(total * (100 - percent) / 100, 2)
    return {"status": 200, "total": new_total, "discount_percent": percent}
