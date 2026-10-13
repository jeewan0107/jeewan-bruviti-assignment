# Repair vs Replace Classification API

A local FastAPI service implementing the Bruviti Repair vs Replace policy rules (D0-D6), with a one-page UI.

## Requirements

- Python 3.10+
- No external API keys or runtime network calls are required.

## Install and run

From the repository root, run this single command:

```bash
python -m pip install -r requirements.txt && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open:
- UI: http://localhost:8000/
- Health: http://localhost:8000/health
- Interactive API docs: http://localhost:8000/docs

## Run tests

In another terminal, from the repository root:

```bash
python -m pytest -q
```

Tests are local and do not call external services.

## API

`POST /decide` accepts the case fields described in the assignment and returns:

- `case_id`
- `decision`: `repair`, `replace`, or `escalate`
- `estimated_repair_cost`: number or null
- `confidence`: number from 0 to 1
- `reason`: one-sentence explanation

## Policy implementation notes

- Escalation checks are evaluated before normal decisions.
- D3 travel rule is evaluated before warranty-specific rules.
- Unknown warranty is inferred from product age per D4.
- Cost formula follows Appendix D.
- When travel time is null, the cost estimate is unavailable because the published formula requires travel minutes. This is an explicit implementation assumption documented in NOTES.md.
- Symptom consistency checks are transparent keyword heuristics, not a general language-understanding model.
