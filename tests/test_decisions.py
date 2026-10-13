from app.decision import decide

def test_example_one(case):
    result = decide(case)
    assert result["decision"] == "repair"
    assert result["estimated_repair_cost"] == 8150.0
    assert result["case_id"] == "C-2001"

def test_example_two(case):
    case.update({
        "case_id": "C-2002",
        "product_category": "refrigerator",
        "product_age_months": 8,
        "purchase_price": 52000,
        "replacement_price": 49000,
        "warranty_status": "in_warranty",
        "fault_category": "not_cooling",
        "parts": [{
            "sku": "RF-CMP-220", "description": "Compressor",
            "price": 14500, "lead_time_days": 28
        }],
        "labour_hours": 2.0,
        "labour_rate_per_hour": 900,
        "technician_travel_minutes": 25,
        "prior_repairs_12m": 0,
        "customer_sentiment": "negative",
        "symptom_text": "fridge warm for 3 days, food spoiled"
    })
    result = decide(case)
    assert result["decision"] == "replace"
    assert result["estimated_repair_cost"] == 16675.0

def test_example_three_escalates(case):
    case.update({
        "case_id": "C-2003",
        "product_category": "dishwasher",
        "product_age_months": 50,
        "purchase_price": 41000,
        "replacement_price": None,
        "warranty_status": "extended",
        "fault_category": "water_leak",
        "parts": [{
            "sku": "DW-PMP-031", "description": "Drain pump",
            "price": None, "lead_time_days": 6
        }],
        "labour_hours": 1.0,
        "labour_rate_per_hour": 900,
        "technician_travel_minutes": 70,
        "prior_repairs_12m": 2,
        "customer_sentiment": "negative",
        "symptom_text": "third leak this year, I want this sorted or taken away"
    })
    result = decide(case)
    assert result["decision"] == "escalate"
    assert result["estimated_repair_cost"] is None

def test_safety_hazard_escalates(case):
    case["symptom_text"] = "smoke coming from the back"
    assert decide(case)["decision"] == "escalate"

def test_repeated_repairs_escalate(case):
    case["prior_repairs_12m"] = 2
    case["customer_sentiment"] = "negative"
    assert decide(case)["decision"] == "escalate"

def test_d3_travel_replace(case):
    case["technician_travel_minutes"] = 121
    # cost ratio is 8150/18000 = 45.3%
    case["replacement_price"] = 18000
    assert decide(case)["decision"] == "replace"

def test_unknown_warranty_under_or_equal_24_is_in_warranty(case):
    case["warranty_status"] = "unknown"
    case["product_age_months"] = 24
    case["replacement_price"] = 10000
    # Ratio > 60%, so the inferred in-warranty branch replaces.
    assert decide(case)["decision"] == "replace"

def test_cost_threshold_d1_exactly_60_percent_repairs(case):
    case["warranty_status"] = "in_warranty"
    case["replacement_price"] = 8150 / 0.60
    assert decide(case)["decision"] == "repair"

def test_missing_travel_escalates(case):
    case["technician_travel_minutes"] = None
    assert decide(case)["decision"] == "escalate"

def test_contradiction_escalates(case):
    case["fault_category"] = "not_cooling"
    case["symptom_text"] = "door will not close"
    assert decide(case)["decision"] == "escalate"
