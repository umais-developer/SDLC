---
name: stage-9-deploy
description: |
  Verify the app is static-deployable and configure it for GitHub Pages.
  Checks for server-side signals, verifies build output, patches base path config,
  and confirms the deployment workflow. Outputs deployment_config.json to .agents/artifacts/stage-9/.
  Can be invoked independently after Stage 8 UAT is approved.
---

# Stage 9: Deploy

> **Status: Experimental — opt-in only.**
> Stage 9 is **not** part of the orchestrated pipeline. `/create-product` stops after Stage 8. Run Stage 9 manually via `/stage-9` (or by following this SKILL.md directly) only when you intend to deploy.
>
> Known limitations:
> - The Step 1 verification uses POSIX `grep` and `cat`, which do not work on Windows PowerShell. Treat results with skepticism until rewritten as a Python verifier.
> - The gate is human confirmation, not an automated verify script. This breaks parity with Stages 1–8.
> - Stage 9 is GitHub Pages-only. Other static hosts (Netlify, Cloudflare Pages, S3) are not supported.

You are a DevOps Engineer. Verify the app is eligible for GitHub Pages deployment, configure it correctly, and confirm readiness.

## Independent Invocation

Requires Stage 2 artifacts and a passing build. Pick the form that matches your environment:

- **Claude Code:** `/stage-9`
- **GitHub Copilot:** `Follow instructions in #file:.agents/skills/stage-9-deploy/SKILL.md`
- **Other agents:** Read this file and follow it.

## Variable Substitution

| Placeholder | Source |
|---|---|
| `{{tech_stack_json}}` | Full contents of `.agents/artifacts/stage-2/tech_stack.json` |
| `{{repo_name}}` | Value of `name` in `package.json` if it exists, otherwise derive from the project folder name |

**Rule:** Never leave a `{{placeholder}}` unreplaced.

## Execution Steps

### Step 1 — Static App Verification
- Load prompt: `.agents/skills/stage-9-deploy/prompts/static_verification.md`
- Substitute: `{{tech_stack_json}}`, `{{repo_name}}`
- Run verification checks:
  ```bash
  ls dist/index.html
  grep -r "express\|fastify\|flask\|django\|spring" src/ --include="*.ts" --include="*.js" --include="*.py"
  cat vite.config.ts | grep "base:"
  cat .github/workflows/deploy.yml | grep "working-directory"
  ```
- Write output to: `.agents/artifacts/stage-9/deployment_config.json`

### Step 2 — Halt on Server Signals
If `is_static: false` or `blockers` is non-empty:
```
⚠️ Deployment aborted — server-side signals found.
Blockers: [list from deployment_config.json]
Recommended platforms: Vercel, Render, Railway, Fly.io, Azure App Service
```
**Stop here.** Do not proceed.

### Step 3 — Configure and Deploy
If `is_static: true` and no blockers:
- Patch `vite.config.ts` to set `base: "/<repo-name>/"`
- Confirm `.github/workflows/deploy.yml` is present
- Push to `deploy/<repo-name>` branch (confirm with user before pushing)
- Report expected URL: `https://<username>.github.io/<repo-name>/`

## Outputs

| Artifact | Path |
|---|---|
| Deployment config | `.agents/artifacts/stage-9/deployment_config.json` |

## Gate

The gate for this stage is human confirmation that the deployment URL is accessible. No automated verify script.

## Server-Side Signals That Block Deployment

If any of the following are found, halt and recommend an appropriate platform:
- Node.js HTTP server, Express, .NET, Python (Flask/FastAPI/Django), Java, PHP, Ruby
- Databases: SQL Server, PostgreSQL, MySQL, MongoDB, Redis, SQLite (server-managed)
- SSR frameworks: Next.js SSR, Remix, SvelteKit SSR, Nuxt SSR
- Infrastructure: Dockerfile, docker-compose.yml, Kubernetes manifests, `*.csproj`, `pom.xml`
