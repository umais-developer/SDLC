# Promptfoo Starter Exercise: Testing a PRD Writing Skill

This exercise walks you through installing Promptfoo, writing a basic eval config, and running your first evaluation against a skill you've built for generating Product Requirements Documents (PRDs).

---

## Prerequisites

You need **Node.js 20 or later**. Verify with:

```bash
node --version
```

If you don't have Node.js:
- **Mac:** `brew install node` (requires [Homebrew](https://brew.sh))
- **Windows:** Download the installer from [nodejs.org](https://nodejs.org)

---

## Part 1 — Install Promptfoo

Choose one method. `npx` is the easiest for a first run since it requires no install.

**Option A — npx (no install, always latest):**
```bash
npx promptfoo@latest --version
```

**Option B — Global install via npm:**
```bash
npm install -g promptfoo
promptfoo --version
```

**Option C — Mac Homebrew:**
```bash
brew install promptfoo
promptfoo --version
```

**Option D — Python pip (wraps npm under the hood, requires Node.js):**
```bash
pip install promptfoo
promptfoo --version
```

All commands below use `npx promptfoo@latest`. If you did a global install, you can drop the `npx` prefix and just run `promptfoo`.

---

## Part 2 — Set Your API Key

Promptfoo calls the model API on your behalf. Set your Anthropic key as an environment variable before running evals.

**Mac / Linux:**
```bash
export ANTHROPIC_API_KEY=your-key-here
```

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY = "your-key-here"
```

> **Tip:** Add the export line to your `~/.zshrc` or `~/.bashrc` so you don't have to repeat it each session.

---

## Part 3 — Project Structure

Skills live in `.agents/skills/` so that Claude Code, Codex, and other agentic tools discover them automatically. Evals live beside the skill they test. Your repo should look like this:

```
your-repo/
└── .agents/
    └── skills/
        └── create-prd/
            ├── SKILL.md                             ← your PRD skill (system prompt + description)
            └── evals/
                ├── promptfooconfig.yaml             ← output quality eval
                ├── cases.yaml                       ← quality test cases
                ├── promptfooconfig-routing.yaml     ← description / skill selection eval
                └── cases-routing.yaml               ← routing test cases
```

Create the directories from the repo root:

```bash
mkdir -p .agents/skills/create-prd/evals
```

---

## Part 4 — Write Your Skill

Create `.agents/skills/create-prd/SKILL.md` with your PRD-writing system prompt. Here is a minimal starting point — replace this with the skill you built:

```markdown
You are an expert product manager. When given a feature request or problem statement,
produce a structured Product Requirements Document (PRD) that includes:

1. **Overview** — A one-paragraph summary of the feature and its purpose.
2. **Goals & Success Metrics** — What this feature is trying to achieve and how success will be measured.
3. **User Stories** — At least three user stories in the format "As a [user], I want [action] so that [benefit]."
4. **Functional Requirements** — A numbered list of specific behaviors the feature must exhibit.
5. **Out of Scope** — What this feature explicitly will NOT do.

Write clearly and concisely. Target audience is engineers and designers who will build the feature.
```

---

## Part 5 — Write Your Test Cases

Create `.agents/skills/create-prd/evals/cases.yaml`. Each test case provides an input and a set of assertions that define what "good output" looks like.

```yaml
# .agents/skills/create-prd/evals/cases.yaml

- description: "Simple feature request — user notifications"
  vars:
    request: "We need to add email notifications when a user's order ships."
  assert:
    # Deterministic checks (fast, free, always run first)
    - type: icontains        # case-insensitive contains
      value: "overview"
    - type: icontains
      value: "user stories"
    - type: icontains
      value: "out of scope"
    - type: javascript
      value: output.split(' ').length > 150   # must be substantive
    # LLM-as-judge checks (slower, costs tokens, run for quality)
    - type: llm-rubric
      value: >
        The PRD contains at least three user stories in the format
        "As a [user], I want [action] so that [benefit]."
      threshold: 0.8
    - type: llm-rubric
      value: >
        The functional requirements section contains a numbered list
        of specific, testable behaviors.
      threshold: 0.8

- description: "Ambiguous request — should still produce a complete PRD"
  vars:
    request: "Make the dashboard better."
  assert:
    - type: icontains
      value: "goals"
    - type: javascript
      value: output.split('\n').length > 20   # multi-section output
    - type: llm-rubric
      value: >
        Despite the vague input, the PRD makes reasonable assumptions explicit
        and proposes concrete, actionable requirements.
      threshold: 0.7

- description: "Technical feature — API rate limiting"
  vars:
    request: "Add rate limiting to our public REST API — 100 requests per minute per API key."
  assert:
    - type: icontains
      value: "functional requirements"
    - type: icontains
      value: "success metrics"
    - type: llm-rubric
      value: >
        The PRD includes specific technical details about the rate limit
        (100 requests per minute) and describes how violations will be handled.
      threshold: 0.8
    - type: llm-rubric
      value: >
        The out of scope section is present and meaningful — it excludes at least
        one related concern (e.g., authentication, billing, or monitoring).
      threshold: 0.7
```

---

## Part 6 — Write Your Config

Create `.agents/skills/create-prd/evals/promptfooconfig.yaml`. Because the config lives inside `evals/`, all `file://` paths are written relative to that directory — so `../SKILL.md` reaches up one level to the skill file.

```yaml
# .agents/skills/create-prd/evals/promptfooconfig.yaml
description: "PRD Skill Evaluation"

prompts:
  - file://../SKILL.md    # one level up — this IS your skill, the system prompt under test

providers:
  - id: anthropic:messages:claude-sonnet-4-6
    label: Claude Sonnet 4.6
    config:
      temperature: 0.3    # lower temp = more consistent PRD structure

# Variables are injected into the prompt via {{request}}
# The user turn is constructed from the test case vars automatically
defaultTest:
  options:
    provider: anthropic:messages:claude-sonnet-4-6   # pin the judge model

tests: file://cases.yaml
```

> **Comparing skill versions:** To A/B test two versions of your skill, add a second prompt file alongside the first:
>
> ```yaml
> prompts:
>   - file://../SKILL.md          # current version
>   - file://../SKILL-v2.md       # candidate version
> ```
>
> Promptfoo runs all test cases against both and shows a side-by-side matrix so you can see which version produces better PRDs before committing the change.

---

## Part 7 — Run the Eval

All `promptfoo` commands must be run from the `evals/` directory (or you pass `-c` to point at the config). The simplest approach is to `cd` into `evals/` first:

```bash
cd .agents/skills/create-prd/evals
npx promptfoo@latest eval --no-cache
```

When it finishes, open the results in the web UI:

```bash
npx promptfoo@latest view
```

This opens a browser with a matrix view showing pass/fail for every test case and assertion. You can click into any cell to see the full output and the judge's reasoning.

You can also run the eval from the repo root by passing the config path explicitly:

```bash
npx promptfoo@latest eval -c .agents/skills/create-prd/evals/promptfooconfig.yaml --no-cache
```

**Useful flags:**

| Flag | Purpose |
|---|---|
| `--no-cache` | Always re-run (don't use cached results during development) |
| `--repeat 3` | Run each test 3 times (helps with non-deterministic outputs) |
| `-o results.json` | Save output to a file (good for CI) |
| `--filter-description "ambiguous"` | Run only tests whose description matches |

---

## Part 8 — Testing the Skill Description (Tool Selection)

This is a distinct and important test from everything above. Parts 5–7 test **what the skill produces** once it's running. This part tests **whether the skill gets invoked at all** — which is entirely determined by the `description` field in your `SKILL.md` front matter.

When an agent receives a request, it reads each available skill's description and decides which tool to call. A weak or ambiguous description means the skill gets skipped even when it's the right choice. A description that's too broad means it gets invoked when it shouldn't be. Both are bugs you can catch with evals.

### How it works in Promptfoo

You register your skill as a **tool** in the provider config, using its description as `function.description`. Promptfoo then sends the model a bare user request with that tool available, and you assert on whether the tool was called — without forcing the model's hand.

### Add a description to your SKILL.md

Your `SKILL.md` front matter should already have a `description` field. Make it accurate and specific — this is the text the model reads to decide whether to invoke the skill:

```markdown
---
name: create-prd
description: >
  Creates a structured Product Requirements Document (PRD) from a feature
  request or problem statement. Use when the user needs to document a new
  feature, capability, or product change for an engineering or design team.
---

You are an expert product manager. When given a feature request...
```

### Create a separate eval config for description testing

Create `.agents/skills/create-prd/evals/promptfooconfig-routing.yaml`. This config is intentionally separate from `promptfooconfig.yaml` — the routing test and the output quality test have different shapes. The routing config does **not** load `SKILL.md` as a system prompt. Instead, it exposes the skill as a tool and tests whether the model selects it.

```yaml
# .agents/skills/create-prd/evals/promptfooconfig-routing.yaml
description: "PRD Skill — description / routing eval"

prompts:
  - "{{request}}"    # bare user turn — no system prompt, just the request

providers:
  - id: anthropic:messages:claude-sonnet-4-6
    label: Claude Sonnet 4.6
    config:
      temperature: 0        # deterministic for routing decisions
      tools:
        - type: function
          function:
            name: create_prd
            # This description comes directly from your SKILL.md front matter.
            # When you update the description there, update it here to match.
            description: >
              Creates a structured Product Requirements Document (PRD) from a
              feature request or problem statement. Use when the user needs to
              document a new feature, capability, or product change for an
              engineering or design team.
            parameters:
              type: object
              properties:
                request:
                  type: string
                  description: The feature request or problem statement to turn into a PRD.
              required: [request]

tests: file://cases-routing.yaml
```

### Create the routing test cases

Create `.agents/skills/create-prd/evals/cases-routing.yaml`. You need both **positive cases** (the skill should be invoked) and **negative cases** (the skill should not be invoked). The negative cases are just as important — they prove the description isn't so vague it triggers on everything.

```yaml
# .agents/skills/create-prd/evals/cases-routing.yaml

# --- Positive cases: skill SHOULD be invoked ---

- description: "Routing — clear feature request should invoke create_prd"
  vars:
    request: "We need to add email notifications when a user's order ships."
  assert:
    - type: javascript
      value: |
        // The model should call the tool, not answer directly
        context.response.toolCalls?.some(tc => tc.function?.name === 'create_prd')
      metric: skill_invoked

- description: "Routing — product problem statement should invoke create_prd"
  vars:
    request: "Users are dropping off during onboarding. We want to add a guided setup wizard."
  assert:
    - type: javascript
      value: |
        context.response.toolCalls?.some(tc => tc.function?.name === 'create_prd')
      metric: skill_invoked

- description: "Routing — technical feature request should invoke create_prd"
  vars:
    request: "Add rate limiting to our public REST API — 100 requests per minute per API key."
  assert:
    - type: javascript
      value: |
        context.response.toolCalls?.some(tc => tc.function?.name === 'create_prd')
      metric: skill_invoked

# --- Negative cases: skill should NOT be invoked ---

- description: "Routing — general coding question should NOT invoke create_prd"
  vars:
    request: "How do I paginate results in a REST API?"
  assert:
    - type: javascript
      value: |
        // No tool call expected — the model should answer directly
        !context.response.toolCalls?.some(tc => tc.function?.name === 'create_prd')
      metric: skill_not_invoked

- description: "Routing — status question should NOT invoke create_prd"
  vars:
    request: "What's the current sprint velocity for the platform team?"
  assert:
    - type: javascript
      value: |
        !context.response.toolCalls?.some(tc => tc.function?.name === 'create_prd')
      metric: skill_not_invoked
```

### Run the routing eval

```bash
cd .agents/skills/create-prd/evals
npx promptfoo@latest eval -c promptfooconfig-routing.yaml --no-cache
```

### What this catches

If a positive case fails, your description isn't clear enough to trigger selection for that type of request — rewrite it to be more explicit about when the skill applies. If a negative case fails, your description is too broad — tighten it to exclude the categories that are matching incorrectly.

> **Keep the description in sync.** The `function.description` in `promptfooconfig-routing.yaml` must match what's in your `SKILL.md` front matter. When you update one, update the other. If this becomes error-prone, a simple shell script or Makefile target can extract the front matter field and validate they're identical before running evals.

---

## Part 9 — Testing Tools the Skill Calls Out To (Bonus)

If your skill invokes tools of its own (web search, document retrieval, etc.), Promptfoo can verify that behavior too — not just the final output. Add trajectory assertions to `cases.yaml`:

```yaml
- description: "Agent should use web search for current market data"
  vars:
    request: "PRD for a feature that shows real-time competitor pricing."
  assert:
    - type: trajectory:tool-used
      value: web_search                         # assert the tool was actually called
    - type: llm-rubric
      value: "The PRD cites specific, sourced market data rather than vague claims."
      threshold: 0.75
```

This lets you distinguish between a model that *says* it used a tool and one that actually did.

---

## Part 10 — CI/CD Integration (GitHub Actions)

Add this workflow file at `.github/workflows/eval-create-prd.yml`. The `paths` trigger fires whenever the skill or its evals change, keeping CI tightly scoped to just this skill's files. Both the output quality eval and the routing eval run on every PR.

```yaml
name: Eval — create-prd skill

on:
  pull_request:
    paths:
      - '.agents/skills/create-prd/**'

jobs:
  eval-quality:
    name: Output quality
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/checkout@v4

      - uses: actions/cache@v4
        with:
          path: ~/.cache/promptfoo
          key: promptfoo-quality-${{ hashFiles('.agents/skills/create-prd/evals/promptfooconfig.yaml') }}

      - uses: promptfoo/promptfoo-action@v1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          config: .agents/skills/create-prd/evals/promptfooconfig.yaml
          fail-on-threshold: 80
          repeat: 3
          repeat-min-pass: 2
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

  eval-routing:
    name: Description / skill routing
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/checkout@v4

      - uses: actions/cache@v4
        with:
          path: ~/.cache/promptfoo
          key: promptfoo-routing-${{ hashFiles('.agents/skills/create-prd/evals/promptfooconfig-routing.yaml') }}

      - uses: promptfoo/promptfoo-action@v1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          config: .agents/skills/create-prd/evals/promptfooconfig-routing.yaml
          fail-on-threshold: 100    # routing must be correct every time
          repeat: 3
          repeat-min-pass: 3
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

Promptfoo posts separate PR comments for each job, so a description regression and an output regression are reported independently.

> **Adding more skills later:** Each skill gets its own `evals/` folder with both a quality config and a routing config, and its own workflow file. The `paths` trigger in each workflow ensures only the relevant evals run when a specific skill changes.

---

## Cheat Sheet — Common Assertion Types

| Type | What it checks | Cost |
|---|---|---|
| `contains` / `icontains` | Output includes a string (case-sensitive / insensitive) | Free |
| `equals` | Exact match | Free |
| `regex` | Matches a regular expression | Free |
| `is-json` | Output is valid JSON | Free |
| `javascript` | Custom JS expression (e.g., `output.length > 100`) | Free |
| `llm-rubric` | LLM grades output against a written rubric | API cost |
| `factuality` | LLM checks output against a known ground truth | API cost |
| `answer-relevance` | LLM checks output is relevant to the input | API cost |
| `trajectory:tool-used` | Agent called a specific tool | Free |
| `trajectory:tool-sequence` | Agent called tools in the right order | Free |

---

## Quick Reference

```bash
# Validate a config without running evals (from repo root)
npx promptfoo@latest validate -c .agents/skills/create-prd/evals/promptfooconfig.yaml

# Run output quality eval (from repo root)
npx promptfoo@latest eval -c .agents/skills/create-prd/evals/promptfooconfig.yaml --no-cache

# Run description / routing eval (from repo root)
npx promptfoo@latest eval -c .agents/skills/create-prd/evals/promptfooconfig-routing.yaml --no-cache

# Run either eval from the evals/ directory
cd .agents/skills/create-prd/evals
npx promptfoo@latest eval --no-cache                           # quality
npx promptfoo@latest eval -c promptfooconfig-routing.yaml --no-cache   # routing

# View results in the browser
npx promptfoo@latest view

# Compare two skill versions side-by-side
# List both files under prompts: in promptfooconfig.yaml, then run eval
```

---

## Next Steps

- Add more test cases covering edge cases (empty input, very long input, non-English requests)
- Try replacing `claude-sonnet-4-6` with `openai:gpt-4.1` in providers to compare models
- Experiment with temperature settings and observe how output consistency changes
- Graduate from `llm-rubric` to `factuality` assertions once you have ground-truth example PRDs
- Add a second skill under `.agents/skills/` and give it its own `evals/` folder following the same pattern
