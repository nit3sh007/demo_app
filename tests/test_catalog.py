from app.catalog import cheapest_in_category


def test_cheapest_book():
    assert cheapest_in_category("books")["name"] == "Pocket Atlas"
