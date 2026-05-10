# Stage Conventions

This document defines patterns shared across all SDLC pipeline stages. Each SKILL.md references this doc rather than re-inventing these rules. If a convention changes, update it here — all stages inherit the change.

---

## 1. Size Classification

Every stage reads the `size` field from `.agents/artifacts/stage-1/problem.json`. If absent, default to the same size Stage 1 used — do not re-derive it using stage-specific criteria.

| Size | Set by | Meaning |
|------|--------|---------|
| `trivial` | Stage 1 problem.json | ≤ 2 files, single isolated change |
| `medium` | Stage 1 problem.json | Self-contained feature, 1–3 new components |
| `large` | Stage 1 problem.json | Cross-cutting, new subsystem, or greenfield |

**Default when absent:** `medium`

Each stage's SKILL.md defines what "trivial / medium / large" means for its own output format. The size classification is shared; the output profiles are stage-specific.

---

## 2. Anti-Hallucination Rule

**Every justification must be traceable to a specific upstream artifact ID.**

- Stage 1 justifications: must reference user-stated facts, or be labeled `[assumed: value — rationale]`
- Stage 2 justifications: must cite `FR-X`, `NFR-Y`, `CON-Z`, or `GOAL-N` IDs from `goals.json`
- Stage 3+ justifications: must cite IDs from the most recent upstream artifact (components.json, stories.json, etc.)

**Prohibited patterns (regardless of stage):**
- "chosen per industry best practices"
- "derived from testing norms / playability research / user studies" — unless you can name the study
- "React for its component model" / "Postgres for proven scalability" — generic virtue claims
- Any number, threshold, or benchmark not stated in the upstream artifact and not a universal standard (HTTP codes, WCAG ratios, etc.)

**For invented values:** use `[assumed: value — one-line rationale]` and add to the ambiguities list.

---

## 3. Upstream ID Traceability Chain

Each stage must trace its outputs back to the IDs produced by the preceding stage.

| Stage produces | Next stage must reference |
|---|---|
| Stage 1: `GOAL-N`, `FR-N`, `NFR-N`, `CON-N` | Stage 2: every component's `fr_links` |
| Stage 2: component names, `fr_links` | Stage 3: every flow/state maps to a component |
| Stage 3: flow IDs | Stage 4: every epic/story cites a flow ID |
| Stage 4: story IDs | Stage 5: every task cites a story ID |
| Stage 5: task IDs | Stage 6: every implementation file cites a task ID |

**Silence-implies-compliance:** Do not enumerate satisfied requirements. List only those that cannot be satisfied or are at risk. This avoids mechanical compliance theater.

---

## 4. Pipeline Leakage Rule

**No stage's output may reference other pipeline stages as product dependencies.**

- Do NOT write: "This will be refined in Stage 3 (UX)" or "Stage 4 will break this into stories"
- DO write about real product dependencies: "Requires the replay recording feature (defined in Requirements 1.md) to be built first"
- The PRD, architecture doc, UX flows, and epics describe the product. The pipeline is invisible to the product.

---

## 5. Proportionality Rule

**Documentation effort must match feature complexity.**

- A trivial change gets a trivial artifact. A one-line bug fix does not need a traceability matrix.
- A medium feature gets standard coverage — no ceremony beyond what helps a reviewer confirm correctness.
- A large/greenfield feature gets the full treatment.

**Signs of over-engineering (fail these silently in LLM checks):**
- A single-component change with 9 sections and 7 goals
- A SOLID assessment for a pure function with no classes
- A traceability matrix for a feature with 1 goal
- Enumerating constraints that are trivially met and add no signal

---

## 6. Section Omission Rules

These sections should be **omitted** when they contain no signal:

| Section | Omit when |
|---|---|
| Assumptions & Open Questions | No assumptions were made |
| Constraints Violated / At Risk | All constraints are satisfied (silence = compliance) |
| Risks & Open Questions | No genuine risks or open questions |
| Dependencies | No pre-existing product dependencies required |
| Traceability Matrix | Feature has ≤ 2 goals (Stage 1, Medium) |
| Design Principles Assessment | Feature introduces < 4 modules with non-trivial interactions |
| Data Flow | Flow is trivially obvious from the component list |

---

## 7. Verify Script Conventions

All verify scripts follow this pattern:

- Accept positional args for artifact files; accept `--size trivial|medium|large` or `--trivial` flag
- Exit code 0 = pass; exit code 1 = fail
- Print `✅ Stage N verification PASSED` on success with bullet-point summary
- Print `❌ [Stage N] ErrorType: message` on failure (to stderr)
- Warn (print `⚠️`) but do not fail for soft violations (missing optional fields, advisory notices)
- Gracefully degrade when optional tools (jsonschema, anthropic) are not installed

**Trivial gate minimum bar** (all stages): artifact exists, is non-empty (> 50 chars), names at least one file path, cites at least one upstream ID. This ensures "trivial" is a real result, not an empty output.

---

## 8. Prompt Versioning

Every file under `.agents/skills/<stage>/prompts/` carries a `prompt_version` (date string, e.g. `"2026-05-09"`) in its YAML frontmatter. When a stage produces a structured artifact (`problem.json`, `goals.json`, `components.json`, `flows.json`, `stories.json`, `tasks.json`, `review.json`, `test_plan.json`, `uat_results.json`), it must record the prompt versions that produced it under a `meta` field:

```json
{
  "meta": {
    "prompt_versions": {
      "problem_interpretation": "2026-05-09",
      "goals_extraction": "2026-05-09"
    },
    "generated_at": "2026-05-09T14:32:00Z"
  },
  ...
}
```

This lets a future verifier compare artifact versus current prompt and flag stale outputs ("artifact was produced under prompt v2026-04-01; current prompt is v2026-05-09 — re-run").

**Bumping `prompt_version`:** when you change a prompt's behavior in a way that should invalidate prior artifacts, bump the date. Cosmetic changes (typo, formatting) do not require a bump.

---

## 9. What Stages Do NOT Own

To prevent scope creep across stages:

| Stage | Must NOT include |
|---|---|
| Stage 1 (PRD) | Implementation tech choices, file names, code |
| Stage 2 (Architecture) | User flows, story points, test scripts |
| Stage 3 (UX) | Component file names, tech stack details |
| Stage 4 (Epics) | Implementation detail, architectural decisions |
| Stage 5 (Plan) | Code, architecture changes |
| Stage 6 (Implement) | New requirements not in Stage 5 tasks |
| Stage 7 (Review/UAT) | New features; only evaluates what was built |

---

## Referencing This Document

In any SKILL.md, reference shared conventions with:
```
See `.agents/skills/STAGE-CONVENTIONS.md` for: size classification, anti-hallucination rule, traceability chain, pipeline leakage rule, prompt versioning.
```
