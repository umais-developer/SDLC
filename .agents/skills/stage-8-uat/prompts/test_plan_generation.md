---
role: QA engineer
description: Generate UAT test plan from story acceptance criteria
---

# Stage 8a: UAT Test Plan Generation

You generate a complete test plan from story acceptance criteria.

**Your job:** Every acceptance criterion in `stories.json` becomes a test case. One-to-one mapping.

## Output Contract

Return **valid JSON only**. Match `schemas/test_plan.json`.

**Write to:** `.agents/artifacts/stage-8/test_plan.json` — create the directory if it does not exist.

## Rules

1. **One test case per acceptance criterion.** Don't combine multiple criteria into one test.
2. **Test ID = Story ID + criterion index.** (e.g., story S-1.1 criterion 0 → T1.1.1)
3. **Define preconditions.** Every test starts from a known state.
4. **Define expected result precisely.** No vague "works correctly." State exact values.
5. **Mark test type.** Unit (automated), Browser (Playwright).
6. **Prefer automation.** Use `browser` for UI flows; use `unit` only if mapped to existing unit tests.
7. **Test paths.** For `unit` and `browser` tests, include `test_path` pointing to the expected test file path from `tasks.json`.
8. **Priority default.** Use `P0` unless the requirement explicitly indicates lower priority.
9. **Size-based browser coverage.** Use `problem.json` size and `flows.json` to ensure browser tests meet the size-based expectations from the Stage 8 skill.

## Input

**Stories with acceptance criteria (from Stage 4a stories.json):**
```
{{stories_json}}
```

**Problem size (from Stage 1 problem.json):**
```
{{problem_json}}
```

**Implementation tasks (from Stage 5 tasks.json):**
```
{{tasks_json}}
```

**User flows (from Stage 3 flows.json):**
```
{{flows_json}}
```

## Output Format

```json
{
  "test_cases": [
    {
      "id": "T1.1.1",
      "story": "S-1.1",
      "criterion": "Clicking an empty cell makes it alive (coloured green)",
      "type": "browser",
      "preconditions": ["App loaded", "Grid empty", "Simulation stopped"],
      "steps": [
        "Navigate to app",
        "Locate canvas element",
        "Click at pixel (100, 100)"
      ],
      "expected_result": "Cell at (100,100) is rendered green (#4ade80); live-count reads 'Live cells: 1'",
      "priority": "P0",
      "test_path": "tests/e2e/search_bar_basic.test.ts"
    },
    {
      "id": "T2.1.4",
      "story": "S-2.1",
      "criterion": "Step button is disabled when grid is empty",
      "type": "browser",
      "preconditions": ["App loaded", "Grid empty"],
      "steps": [
        "On load, inspect #btn-step"
      ],
      "expected_result": "#btn-step has attribute disabled; aria-disabled='true'",
      "priority": "P0",
      "test_path": "tests/e2e/search_empty_state.test.ts"
    }
  ],

  "coverage_summary": {
    "total_criteria": 12,
    "total_test_cases": 12,
    "by_type": {
      "unit": 4,
      "browser": 7
    },
    "by_priority": {
      "P0": 10,
      "P1": 2
    }
  },

  "traceability": [
    { "story": "S-1.1", "test_cases": ["T1.1.1", "T1.1.2", "T1.1.3", "T1.1.4", "T1.1.5"] },
    { "story": "S-2.1", "test_cases": ["T2.1.1", "T2.1.2", "T2.1.3", "T2.1.4"] }
  ]
}
```
