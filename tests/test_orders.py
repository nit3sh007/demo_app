from app.orders import average_item_price


def test_average():
    assert average_item_price([10, 20, 30]) == 20.0
