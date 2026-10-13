from typing import Any


def calculate_repair_cost(case: Any) -> float | None:
    """
    Appendix D formula:
      sum(part prices) + labour_hours * rate
      + (one-way travel minutes / 60) * rate

    The brief explicitly says null part prices or null labour hours make
    the cost unavailable. It does not specify null travel handling; because
    the formula requires travel minutes, this implementation returns None
    when travel minutes are unknown and documents that assumption.
    """
    parts = case.parts if hasattr(case, "parts") else (case.get("parts") or [])
    labour_hours = (
        case.labour_hours if hasattr(case, "labour_hours")
        else case.get("labour_hours")
    )
    rate = (
        case.labour_rate_per_hour if hasattr(case, "labour_rate_per_hour")
        else case.get("labour_rate_per_hour")
    )
    travel = (
        case.technician_travel_minutes if hasattr(case, "technician_travel_minutes")
        else case.get("technician_travel_minutes")
    )

    if labour_hours is None or travel is None:
        return None

    part_prices = []
    for part in parts:
        price = part.price if hasattr(part, "price") else part.get("price")
        if price is None:
            return None
        part_prices.append(float(price))

    total = sum(part_prices) + float(labour_hours) * float(rate)
    total += (float(travel) / 60.0) * float(rate)
    return round(total, 2)
