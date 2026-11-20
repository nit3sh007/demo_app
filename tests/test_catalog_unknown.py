from app.catalog import cheapest_in_category

def test_cheapest_unknown_category():
    assert cheapest_in_category("toys") == {}
