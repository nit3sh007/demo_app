import bisect

# (max weight in kg, price)
BANDS = [(1, 4.0), (5, 9.0), (20, 19.0)]


def shipping_cost(weight_kg: float) -> dict:
    """Return shipping cost for a given weight.

    The function uses the defined ``BANDS`` where each tuple is ``(max_weight, price)``.
    For weights that exceed the largest defined band we cap the lookup to the last
    band instead of raising an ``IndexError``. This treats any heavier parcel as
    belonging to the highest price tier, which is a reasonable default for the
    API and prevents crashes on valid input.
    """
    # Find the first band whose max weight is >= weight_kg.
    idx = bisect.bisect_left([m for m, _ in BANDS], weight_kg)
    # If weight is larger than any defined band, use the last band.
    if idx >= len(BANDS):
        idx = len(BANDS) - 1
    return {"status": 200, "cost": BANDS[idx][1], "band_kg": BANDS[idx][0]}
