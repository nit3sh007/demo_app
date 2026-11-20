from app.orders import average_item_price


def test_average():
    assert average_item_price([10, 20, 30]) == 20.0


def test_average_empty_list():
    """When no prices are provided, the average should be 0.0 rather than raising.
    This mirrors the endpoint's expected behaviour for an empty cart.
    """
    assert average_item_price([]) == 0.0
