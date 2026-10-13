from app.cost import calculate_repair_cost
from app.symptoms import safety_hazard, symptom_contradiction

EXPECTED_LIFE_MONTHS = {
    "washing_machine": 120,
    "refrigerator": 144,
    "dishwasher": 108,
    "oven_or_cooktop": 156,
    "air_conditioner": 120,
    "water_heater": 96,
    "microwave": 96,
}

def _get(case, name):
    value = getattr(case, name, None)
    if value is not None:
        return value
    if isinstance(case, dict):
        return case.get(name)
    return value

def _part_value(part, name):
    if hasattr(part, name):
        return getattr(part, name)
    return part.get(name)

def _result(case, decision, cost, reason, confidence):
    return {
        "case_id": _get(case, "case_id"),
        "decision": decision,
        "estimated_repair_cost": cost,
        "confidence": round(max(0.0, min(1.0, confidence)), 2),
        "reason": reason,
    }

def decide(case):
    cost = calculate_repair_cost(case)
    parts = _get(case, "parts") or []
    warranty = _get(case, "warranty_status")
    age = _get(case, "product_age_months")
    replacement = _get(case, "replacement_price")
    travel = _get(case, "technician_travel_minutes")
    sentiment = _get(case, "customer_sentiment")
    prior_repairs = _get(case, "prior_repairs_12m")
    symptom_text = _get(case, "symptom_text") or ""
    fault = _get(case, "fault_category")

    # D5 has precedence over every decision rule.
    escalation_reasons = []
    if prior_repairs >= 2 and sentiment == "negative":
        escalation_reasons.append("two or more prior repairs with negative customer sentiment (D5)")
    hazard = safety_hazard(symptom_text)
    if hazard:
        escalation_reasons.append(f"potential safety hazard ({hazard}) in symptom text (D5)")
    contradiction = symptom_contradiction(fault, symptom_text)
    if contradiction:
        escalation_reasons.append(f"symptom/structured-field contradiction: {contradiction} (D5)")
    if any(_part_value(part, "price") is None for part in parts):
        escalation_reasons.append("a required part price is missing, so repair cost cannot be computed (D5)")
    if _get(case, "labour_hours") is None:
        escalation_reasons.append("labour hours are missing, so repair cost cannot be computed (D5)")
    if cost is None and not any("missing" in r or "cannot be computed" in r for r in escalation_reasons):
        escalation_reasons.append("repair cost cannot be computed from the available inputs")

    # Replacement price is needed by the normal cost thresholds.
    if replacement is None and not hazard and not contradiction:
        escalation_reasons.append("replacement price is missing and the policy decision depends on it (D5)")
    elif replacement == 0 and not hazard and not contradiction:
        escalation_reasons.append("replacement price is zero, so cost ratios cannot be evaluated safely")

    if escalation_reasons:
        # If the estimate can be computed, retain it even when another D5
        # reason (e.g. safety or repeated repairs) requires escalation.
        confidence = 0.82 if hazard else 0.70
        return _result(case, "escalate", cost, "; ".join(escalation_reasons) + ".", confidence)

    # Without a cost or travel duration the published formula/thresholds cannot be evaluated.
    if cost is None:
        return _result(case, "escalate", None,
                       "Repair cost cannot be computed because a required cost input is unavailable.", 0.60)
    if travel is None:
        return _result(case, "escalate", cost,
                       "Technician travel time is unavailable, so the repair estimate cannot be fully verified.", 0.60)
    if replacement is None or replacement <= 0:
        return _result(case, "escalate", cost,
                       "Replacement price is unavailable or invalid, so policy cost thresholds cannot be evaluated.", 0.60)

    ratio = cost / replacement
    confidence = 0.90
    warranty_inferred = warranty == "unknown"

    # D4: unknown warranty is inferred from age. Missing age cannot resolve D4.
    if warranty_inferred:
        if age is None:
            return _result(case, "escalate", cost,
                           "Warranty status and product age are insufficient to select the policy branch (D4).", 0.60)
        warranty = "out_of_warranty" if age > 24 else "in_warranty"
        confidence -= 0.15

    # D3 applies before warranty-specific thresholds.
    if travel > 120 and ratio > 0.40:
        decision = "replace"
        reason = f"Travel exceeds 120 minutes and repair cost is {ratio:.1%} of replacement price: rule D3."
        threshold_distance = min(travel - 120, (ratio - 0.40) * 100)
        if threshold_distance <= 2:
            confidence -= 0.15
        return _result(case, decision, cost, reason, confidence)

    if warranty in ("in_warranty", "extended"):
        long_lead_parts = [
            _part_value(part, "lead_time_days") for part in parts
            if _part_value(part, "lead_time_days") is not None
            and _part_value(part, "lead_time_days") > 21
        ]
        if long_lead_parts:
            decision = "replace"
            reason = f"Required part lead time exceeds 21 days ({max(long_lead_parts)} days): rule D1b."
        elif ratio > 0.60:
            decision = "replace"
            reason = f"Repair cost is {ratio:.1%} of replacement price, exceeding 60%: rule D1a."
        else:
            decision = "repair"
            reason = f"Repair cost is {ratio:.1%} of replacement price, within the 60% threshold: rule D1a."
        if abs(ratio - 0.60) <= 0.02:
            confidence -= 0.15
            reason += " Confidence lowered because the cost ratio is within 2 percentage points of the threshold (D6)."
    else:
        expected_life = EXPECTED_LIFE_MONTHS[_get(case, "product_category")]
        age_limit = expected_life * 0.70
        age_ok = age is not None and age <= age_limit
        cost_ok = ratio <= 0.50
        if cost_ok and age_ok:
            decision = "repair"
            reason = (
                f"Repair cost is {ratio:.1%} of replacement price and age "
                f"{age} months is within the {age_limit:.0f}-month limit: rule D2."
            )
        else:
            decision = "replace"
            failures = []
            if not cost_ok:
                failures.append(f"repair cost {ratio:.1%} exceeds 50%")
            if age is None:
                failures.append("product age is unavailable")
            elif not age_ok:
                failures.append(f"age {age} months exceeds the {age_limit:.0f}-month limit")
            reason = "Out-of-warranty case: " + " and ".join(failures) + "; rule D2."
        if abs(ratio - 0.50) <= 0.02 or (age is not None and abs(age - age_limit) <= 2):
            confidence -= 0.15
            reason += " Confidence lowered because a threshold is within 2 percentage points/months (D6)."

    return _result(case, decision, cost, reason, confidence)
