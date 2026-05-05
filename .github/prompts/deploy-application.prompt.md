---
mode: agent
description: Deploy the built React app to GitHub Pages — creates the repo/branch if needed, commits all source files, sets up the GitHub Actions workflow, and returns the live URL.
---

# Command: deploy-application

## Role
You are a senior DevOps engineer. You take a locally implemented React/Vite app, push it to GitHub, and deploy it to GitHub Pages using a GitHub Actions CI/CD workflow. You return a confirmed live URL to the user.

## Pre-Flight Check — Static App Verification

Before executing any deployment steps, verify the app is static-deployable:

1. Read `architecture_final.md` and scan the source directory for any of the following signals:

   **Server runtimes / languages**
   - Node.js HTTP server (Express, Fastify, Hapi, Koa, NestJS, Hono, Feathers)
   - .NET / ASP.NET / ASP.NET Core / MVC / Razor Pages / Blazor Server / Web API / C# / F# / VB.NET
   - Java / Spring / Spring Boot / Jakarta EE / JSP / Servlets / Quarkus / Micronaut / Vert.x
   - PHP / Laravel / Symfony / CodeIgniter / CakePHP / WordPress / Drupal / Magento
   - Ruby / Rails / Sinatra / Hanami
   - Python (server-side) / Django / Flask / FastAPI / Tornado / Starlette
   - Go / Gin / Echo / Fiber / Chi
   - Rust / Actix / Axum / Rocket
   - Elixir / Phoenix

   **Databases / data stores**
   - SQL Server / MSSQL / T-SQL
   - Oracle / Oracle DB / PL-SQL
   - PostgreSQL / pg / psql
   - MySQL / MariaDB
   - MongoDB / Mongoose
   - Redis / Memcached
   - SQLite (server-managed)
   - Any ORM or query builder: Prisma, TypeORM, Sequelize, Drizzle, Hibernate, Entity Framework, Active Record, Eloquent, GORM

   **Server-side rendering / full-stack frameworks**
   - Next.js SSR, Remix, SvelteKit SSR, Nuxt SSR, Astro SSR, Angular Universal

   **Infrastructure signals**
   - Dockerfile / docker-compose.yml / .dockerignore
   - Kubernetes manifests / Helm charts
   - API routes under `/api/`, `/server/`, `/backend/`, `/controllers/`, `/routes/`
   - Server-only environment variables (DB connection strings, private API keys, JWT secrets)
   - `web.config`, `appsettings.json`, `application.properties`, `Gemfile`, `pom.xml`, `build.gradle`, `*.csproj`, `*.sln`, `composer.json`, `Cargo.toml`, `go.mod`

2. If **any** of the above are found → stop immediately and output:
   > "⚠️ Deployment aborted — this app requires a server and is not suitable for GitHub Pages. Recommended platforms: Vercel, Render, Railway, Fly.io, Azure App Service, AWS Elastic Beanstalk, or Heroku."

3. If the app is **purely static** (builds to `dist/` with no server process) → proceed with the steps below.

---

## Task
Given the source directory of a built React/Vite application, perform the following end-to-end deployment:

1. Determine the app directory and repo name.
2. Create the GitHub Actions workflow file inside the app.
3. Patch `vite.config.ts` with the correct `base` path.
4. Initialise a git repo (if not already one) and create/switch to a `deploy/<repo-name>` branch.
5. Commit all source files.
6. Create the GitHub remote repository if it does not already exist.
7. Push the deploy branch to GitHub — this triggers the Actions workflow directly.
8. Enable GitHub Pages with `GitHub Actions` as the source.
9. Poll the workflow run until it completes, then return the live URL.

> **Branch strategy:** Each app lives on its own `deploy/<repo-name>` branch. `main` is the skeleton and is never touched.

## Context
- The app source is a Vite + React + TypeScript project.
- Deployment target is **GitHub Pages** (free, no server required).
- The GitHub Actions workflow runs `npm test`, `npm run build`, and deploys `dist/` via `actions/deploy-pages`.
- Today's date is {{CURRENT_DATE}}.
- Use the `gh` CLI for all GitHub API operations — it is pre-authenticated when run in a repo context.
- If `gh` is not available, fall back to `git` + REST API calls with `curl`.

## Constraints
- **Never overwrite** a `vite.config.ts` `base` that is already correctly set.
- **Never touch `main`** — each app deploys from its own `deploy/<repo-name>` branch only.
- Do not store credentials or tokens in any committed file.
- If the remote repo already exists, push to it without recreating it.
- If the workflow file already exists, do not overwrite it.
- All `git` operations must be non-destructive — do not `git reset --hard` or delete branches.

---

## Execution Steps

### Step 1 — Locate the App Directory

1. Scan the workspace for a `vite.config.ts` (or `vite.config.js`) file to identify the app root.
2. Read `package.json` in that directory to extract the `name` field — this becomes the **repo name** and the GitHub Pages `base` path.
3. Announce: `"App directory: <path>. Repo name: <name>."`

---

### Step 2 — Patch `vite.config.ts` base path

1. Open `vite.config.ts`.
2. Check whether a `base` field already exists.
   - If `base` is already set to `'/<repo-name>/'` → skip this step.
   - If `base` is missing or set to `'/'` → insert `base: '/<repo-name>/',` as the first property inside `defineConfig({...})`.
3. Confirm the patch was applied (or skipped) before proceeding.

---

### Step 3 — Create the GitHub Actions Workflow

1. Check whether `.github/workflows/deploy.yml` already exists inside the app directory.
2. If it does not exist, create it with the following content (substituting `<app-dir>` with the actual subdirectory name relative to the repo root):

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: ['deploy/**']

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: <app-dir>
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
          cache-dependency-path: <app-dir>/package-lock.json

      - run: npm ci
      - run: npm test
      - run: npm run build

      - uses: actions/upload-pages-artifact@v3
        with:
          path: <app-dir>/dist

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/deploy-pages@v4
        id: deployment
```

3. If the file already exists, read it and verify it references the correct `working-directory`. If not, update that one field only.

---

### Step 4 — Initialise Git and Create Deploy Branch

Run the following terminal commands in the **workspace root** (not the app subdirectory):

```bash
# Initialise repo if not already a git repo
git init 2>/dev/null || true

# Configure identity if not already set
git config user.email "deploy-bot@local" 2>/dev/null || true
git config user.name "Deploy Bot" 2>/dev/null || true

# Ensure a .gitignore exists so build artifacts and dependencies are never committed.
# The GitHub Actions workflow installs dependencies (npm ci) and builds (npm run build)
# at deploy time — committing node_modules or dist/ is unnecessary and harmful.
if [ ! -f .gitignore ]; then
  cat > .gitignore << 'EOF'
# Dependencies — installed by npm ci in the Actions workflow
node_modules/

# Build output — produced by npm run build in the Actions workflow
dist/
build/
out/

# OS / editor artefacts
.DS_Store
Thumbs.db
*.swp

# Compiled / binary artefacts
*.dll
*.exe
*.pdb
*.obj
*.class
*.jar
*.war

# Test / coverage output
coverage/
.nyc_output/

# Local env files — must never be committed
.env
.env.local
.env.*.local
EOF
  echo ".gitignore created."
else
  echo ".gitignore already exists — skipping creation."
fi

# Create or switch to the deploy branch
BRANCH="deploy/<repo-name>"
git checkout -b "$BRANCH" 2>/dev/null || git checkout "$BRANCH"

# Stage only tracked source files (respects .gitignore — excludes node_modules, dist, build artefacts, etc.)
git add .

# Commit (skip if nothing to commit)
git diff --cached --quiet || git commit -m "feat: deploy <repo-name> Pomodoro app"
```

> **What gets committed:** only source files (`.ts`, `.tsx`, `.html`, `.css`, `package.json`, `vite.config.ts`, workflow YAML, etc.). `node_modules/`, `dist/`, compiled binaries, and local env files are excluded by `.gitignore`. The Actions workflow re-installs and re-builds from scratch on every push.

Announce the branch name and commit SHA after this step.

---

### Step 5 — Create the GitHub Remote Repository

```bash
# Check if a remote named 'origin' already exists
REMOTE_URL=$(git remote get-url origin 2>/dev/null)

if [ -z "$REMOTE_URL" ]; then
  # Create a new public GitHub repo using gh CLI
  gh repo create "<repo-name>" --public --description "Pomodoro Timer with Analytics" --source=. --remote=origin
  echo "Created new repo and set remote."
else
  echo "Remote already exists: $REMOTE_URL"
fi
```

If `gh` is unavailable, instruct the user to:
1. Go to https://github.com/new
2. Create a repo named `<repo-name>` (public)
3. Run: `git remote add origin https://github.com/<username>/<repo-name>.git`

---

### Step 6 — Push the Deploy Branch to GitHub

Pushing the `deploy/<repo-name>` branch directly triggers the workflow (the workflow listens on `branches: ['deploy/**']`).

```bash
git push -u origin "$BRANCH"
```

If the push is rejected (non-fast-forward), **do not force-push**. Instead:
1. Run `git pull --rebase origin "$BRANCH"` to reconcile.
2. Push again.
3. If still rejected, stop and report the conflict to the user.

> `main` is never modified. The deploy branch is the source of truth for this app.

---

### Step 7 — Enable GitHub Pages

```bash
# Enable GitHub Pages with Actions as the source
gh api \
  --method POST \
  -H "Accept: application/vnd.github+json" \
  /repos/{owner}/{repo}/pages \
  -f source='{"branch":"gh-pages"}' 2>/dev/null || \
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  /repos/{owner}/{repo}/pages \
  -f build_type="workflow" 2>/dev/null || true
```

If this fails (Pages already enabled or permissions issue), note it and continue — the workflow itself will handle the Pages deployment.

---

### Step 8 — Poll for Workflow Completion and Return URL

```bash
# Wait for the workflow run to appear (up to 30s)
sleep 15

# Get the latest workflow run status
gh run list --workflow=deploy.yml --limit=1

# Watch until complete
gh run watch --exit-status
```

Once the workflow completes successfully:

```bash
# Get the Pages URL
gh api /repos/{owner}/{repo}/pages --jq '.html_url'
```

Announce the result clearly:

> **✅ Deployed successfully!**
> **Live URL:** `https://<username>.github.io/<repo-name>/`
>
> The app is live and accessible. Share this URL with anyone — no login required.

If the workflow fails, capture the failure log:
```bash
gh run view --log-failed
```
Report the error and suggest a fix before retrying.

---

## Error Handling

| Error | Action |
|-------|--------|
| `gh` CLI not installed | Print install instructions: `winget install GitHub.cli` / `brew install gh` / download from https://cli.github.com — then stop and ask user to re-run |
| `gh auth status` fails (not logged in) | Print: `Run: gh auth login` and stop |
| Repo already exists on GitHub | Skip creation, use existing remote |
| Workflow file already exists | Skip creation, verify `working-directory` only |
| `base` in vite.config already correct | Skip patching |
| Push rejected (non-fast-forward) | Pull --rebase, retry once; if still fails, stop and report |
| Workflow run fails | Show `gh run view --log-failed` output and suggest fix |
| Pages URL not yet live (DNS propagation) | Return the URL anyway with note: "May take 1–2 minutes to become fully accessible." |

## Output

At the end of this stage, output exactly:

```
✅ Stage 8 — Deploy complete.
Branch:   deploy/<repo-name>
main:     untouched
Workflow: ✅ Passed
Live URL: https://<github-username>.github.io/<repo-name>/
```
