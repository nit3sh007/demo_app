def average_item_price(prices: list) -> float:
    if not prices:
        return 0.0
    return round(sum(prices) / len(prices), 2)
