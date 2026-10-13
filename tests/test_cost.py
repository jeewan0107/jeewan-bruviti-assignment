from app.cost import calculate_repair_cost

def test_example_one_cost(case):
    assert calculate_repair_cost(case) == 8150.0

def test_missing_part_price_returns_none(case):
    case["parts"][0]["price"] = None
    assert calculate_repair_cost(case) is None

def test_missing_labour_returns_none(case):
    case["labour_hours"] = None
    assert calculate_repair_cost(case) is None

def test_multiple_parts(case):
    case["parts"].append({
        "sku": "WM-BELT", "description": "Belt",
        "price": 500, "lead_time_days": 2
    })
    assert calculate_repair_cost(case) == 8650.0
