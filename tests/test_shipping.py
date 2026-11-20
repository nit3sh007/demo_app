from app.shipping import shipping_cost


def test_mid_weight_band():
    assert shipping_cost(3)["cost"] == 9.0


def test_light_parcel():
    assert shipping_cost(0.5)["cost"] == 4.0
