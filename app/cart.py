COUPONS = {"SAVE10": 10, "SAVE20": 20}  # percent off


def apply_coupon(total: float, code: str) -> dict:
    percent = COUPONS[code.strip().upper()]
    new_total = round(total * (100 - percent) / 100, 2)
    return {"status": 200, "total": new_total, "discount_percent": percent}
