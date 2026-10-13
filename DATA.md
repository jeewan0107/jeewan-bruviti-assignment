# Data and Test Design

## Data source

The policy thresholds, product categories, expected product lives and three reference cases come from the supplied Bruviti Campus Drive 2026 Use Case 2 brief.

## Test data created

The tests use:
1. The three reference examples from the brief.
2. Synthetic edge cases for D1, D2, D3, D4, D5 and D6.
3. API contract tests for `/health`, `/` and `/decide`.

The synthetic tests are authored for policy coverage; they are not a representative sample of real appliance service cases and do not establish real-world predictive accuracy.

## Test strategy

- Cost arithmetic: parts, labour, travel, null part price, null labour hours.
- Rule precedence: D5 before D3, and D3 before warranty rules.
- Threshold boundaries: 50%, 60%, 70% expected life, 21-day lead time, 120-minute travel and 24-month unknown-warranty boundary.
- Text: explicit safety terms and an example structured-field contradiction.
- API: response shape, health check and local UI route.

## Limitations and expected failure modes

- Synthetic examples may not match the hidden evaluation distribution.
- Symptom checks use a small keyword mapping and may miss paraphrases or incorrectly flag unusual wording.
- The brief does not specify a formula for confidence; confidence values are deterministic heuristics.
- The brief does not explicitly define how null travel minutes affect the estimate. This implementation treats the cost as unavailable rather than assuming zero.
- Required-part identification and which part lead times are applicable are assumed to be represented by the supplied `parts` array.
