import bisect

# (max weight in kg, price)
BANDS = [(1, 4.0), (5, 9.0), (20, 19.0)]


def shipping_cost(weight_kg: float) -> dict:
    idx = bisect.bisect_left([m for m, _ in BANDS], weight_kg)
    return {"status": 200, "cost": BANDS[idx][1], "band_kg": BANDS[idx][0]}
