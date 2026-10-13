# Implementation Notes

## Decisions

- Used Python and FastAPI because the assignment permits any language and suggests FastAPI.
- Used deterministic rules rather than machine learning: no labeled training dataset is supplied, and the policy thresholds are explicit.
- Implemented the published precedence: escalation (D5), travel (D3), then warranty rules (D1/D2).
- Unknown warranty is inferred from age per D4; confidence is lowered.
- Confidence is a documented heuristic because the brief specifies no confidence-calibration formula.
- Symptom contradiction detection is a transparent keyword heuristic, not an LLM.

## Assumptions

- A null part price or labour hours prevents cost computation, as explicitly specified.
- Null travel minutes also prevent cost computation because the formula requires travel time; this is not explicitly specified by the brief.
- Missing replacement price triggers escalation where the policy cost ratio is needed.
- Null lead time is not treated as over 21 days; only known lead times can trigger D1b.

## Scope cuts

- No trained ML model, external LLM, external API, database, authentication or persistent case storage.
- The UI supports a single part entry; the API accepts any number of parts.
- Text matching is deliberately lightweight to keep requests fast and fully offline.

## Next steps

- Expand symptom/fault contradiction tests using reviewed examples.
- Calibrate confidence using labeled real cases if they become available.
- Add multi-part editing in the UI and stronger schema/error messaging.
