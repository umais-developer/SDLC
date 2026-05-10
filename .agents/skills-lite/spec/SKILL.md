---
name: lite-spec
description: |
  Stage A of the lite pipeline. Produce a single spec.md with Problem, FRs,
  Assumptions, and Acceptance Criteria. No JSON, no other artifacts.
---

# Lite Stage A — Spec

You are a PM + tech lead writing a working spec. One markdown file. No ceremony.

## Output

Write `.agents/artifacts-lite/spec.md` with exactly these four sections in this order:

```markdown
# Spec: <feature name>

## Problem
<one paragraph: what the user wants and why. No more.>

## Functional Requirements
- **FR-1** — <one sentence>
- **FR-2** — <one sentence>
... (cap at 10)

## Assumptions
- [assumed: <value> — <one-line reason>]
- ...

## Acceptance Criteria
- **FR-1**: <binary, testable condition>
- **FR-1**: <another binary condition, if needed>
- **FR-2**: <binary condition>
- ...
```

## Rules

1. **Problem is one paragraph.** If you need more, you're scoping too big for lite.
2. **FR count cap: 10.** Bigger than that, use the 9-stage pipeline.
3. **Every assumption is tagged.** No invented numbers without `[assumed: ...]`.
4. **Acceptance criteria are binary.** "User can X" passes or fails. No prose.
5. **Every FR has at least one acceptance criterion.** The verifier checks this.

## What this stage does NOT do

- Pick a tech stack (defer to Stage B unless the user pinned one).
- Decompose into stories or tasks.
- Map components or write architecture diagrams.
- Define UX flows, microcopy, or accessibility specs.

If you genuinely need any of those, use `/create-product` not `/lite-build`.

## Gate

```bash
python .agents/skills-lite/_verify.py spec
```

Pass criteria: spec.md exists with all four sections, ≥1 FR, every FR has ≥1
acceptance criterion, all assumptions are tagged with `[assumed: ...]`.
