PRODUCTS = [
    {"name": "Python Cookbook", "category": "books", "price": 39.0},
    {"name": "Pocket Atlas", "category": "books", "price": 12.5},
    {"name": "Chef Knife", "category": "kitchen", "price": 45.0},
    {"name": "Cast Iron Pan", "category": "kitchen", "price": 32.0},
    {"name": "USB-C Cable", "category": "electronics", "price": 9.0},
]


def cheapest_in_category(category: str) -> dict:
    return min((p for p in PRODUCTS if p["category"] == category), key=lambda p: p["price"])
