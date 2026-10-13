import re

SAFETY_PATTERNS = [
    r"\bsparks?\b", r"\bsmoke\b", r"\bgas smell\b", r"\bsmell of gas\b",
    r"\belectric(?:al)? shock\b", r"\bfire\b", r"\bcatch(?:ing)? fire\b",
]

# Lightweight, transparent keyword mapping. This is intentionally not an LLM.
FAULT_TERMS = {
    "no_power": ["no power", "won't turn on", "will not turn on", "does not turn on",
                 "doesn't turn on", "not powering on", "power failure"],
    "not_heating": ["not heating", "no heat", "not getting hot", "cold oven",
                    "water is cold", "does not heat"],
    "not_cooling": ["not cooling", "not cold", "warm fridge", "fridge warm",
                    "refrigerator warm", "not getting cold"],
    "water_leak": ["leak", "leaking", "water on floor", "dripping water"],
    "drainage_or_blockage": ["not draining", "won't drain", "blocked drain",
                             "clogged", "blockage", "water not draining"],
    "noise_or_vibration": ["loud noise", "vibrating", "vibration", "rattling",
                           "grinding noise", "unusual noise"],
    "door_seal_or_latch": ["door won't close", "door will not close",
                           "door not closing", "latch", "door seal"],
    "control_panel_or_display": ["display blank", "panel not responding",
                                 "control panel", "display error", "screen blank"],
    "electrical_or_control_board": ["control board", "burnt circuit", "electrical fault"],
    "motor_or_drive": ["motor hums", "motor failure", "drum does not turn",
                       "drum won't turn", "motor not running", "drive motor"],
    "installation_or_setup": ["installation", "setup issue", "not installed"],
}

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", (text or "").lower())).strip()

def safety_hazard(text: str) -> str | None:
    text = (text or "").lower()
    for pattern in SAFETY_PATTERNS:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None

def symptom_contradiction(fault_category: str, symptom_text: str) -> str | None:
    text = normalize(symptom_text)
    if not text:
        return None

    # Explicitly catch the example described in the brief.
    if fault_category == "not_cooling":
        door_terms = FAULT_TERMS["door_seal_or_latch"]
        cooling_terms = FAULT_TERMS["not_cooling"]
        if any(normalize(term) in text for term in door_terms) and not any(
            normalize(term) in text for term in cooling_terms
        ):
            return "fault_category is not_cooling but symptom text describes a door/latch fault"

    # If text clearly matches another known category and not the supplied category,
    # treat it as a contradiction. Avoid over-interpreting vague text.
    current_terms = FAULT_TERMS.get(fault_category, [])
    current_match = any(normalize(term) in text for term in current_terms)
    other_matches = []
    for category, terms in FAULT_TERMS.items():
        if category == fault_category:
            continue
        if any(normalize(term) in text for term in terms):
            other_matches.append(category)

    if other_matches and not current_match:
        return (
            f"fault_category is {fault_category} but symptom text more clearly "
            f"matches {other_matches[0]}"
        )
    return None
