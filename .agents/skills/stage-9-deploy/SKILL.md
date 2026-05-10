---
name: stage-9-deploy
description: |
  Verify the app is deployable for its target platform and produce deployment_config.json.
  Branches on `target_platform` from tech_stack.json: `web` -> GitHub Pages flow;
  `desktop` -> signed-installer flow. Outputs deployment_config.json to
  .agents/artifacts/stage-9/. Can be invoked independently after Stage 8 UAT is approved.
---

# Stage 9: Deploy

> **Status: Experimental — opt-in only.**
> Stage 9 is **not** part of the orchestrated pipeline. `/create-product` stops after Stage 8. Run Stage 9 manually via `/stage-9` (or by following this SKILL.md directly) only when you intend to deploy.

You are a DevOps Engineer. Verify the app is eligible for deployment, configure it correctly, and confirm readiness.

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

---

## Branch on `target_platform`

Read `target_platform` from `tech_stack.json`. Default to `web` if absent (historical behavior). Then follow the matching path below.

| `target_platform` | Path |
|---|---|
| `web` | A — GitHub Pages flow |
| `desktop` | B — Signed installer flow |
| `cli` / `library` | Reserved — out of scope; halt with a recommendation. |

---

## Path A — `web` (GitHub Pages)

> Known limitations of this path:
> - The Step A1 verification uses POSIX `grep` and `cat`, which do not work on Windows PowerShell. Treat results with skepticism until rewritten as a Python verifier.
> - The gate is human confirmation rather than an automated verify script. This breaks parity with Stages 1–8.
> - This path is GitHub Pages-only. Other static hosts (Netlify, Cloudflare Pages, S3) are not supported.

### Step A1 — Static App Verification
- Load prompt: `.agents/skills/stage-9-deploy/prompts/static_verification.md`
- Substitute: `{{tech_stack_json}}`, `{{repo_name}}`
- Run verification checks:
  ```bash
  ls dist/index.html
  grep -r "express\|fastify\|flask\|django\|spring" src/ --include="*.ts" --include="*.js" --include="*.py"
  cat vite.config.ts | grep "base:"
  cat .github/workflows/deploy.yml | grep "working-directory"
  ```
- Write output to: `.agents/artifacts/stage-9/deployment_config.json` with `target: "web"`.

### Step A2 — Halt on Server Signals
If `is_static: false` or `blockers` is non-empty:
```
⚠️ Deployment aborted — server-side signals found.
Blockers: [list from deployment_config.json]
Recommended platforms: Vercel, Render, Railway, Fly.io, Azure App Service
```
**Stop here.** Do not proceed.

### Step A3 — Configure and Deploy
If `is_static: true` and no blockers:
- Patch `vite.config.ts` to set `base: "/<repo-name>/"`
- Confirm `.github/workflows/deploy.yml` is present
- Push to `deploy/<repo-name>` branch (confirm with user before pushing)
- Report expected URL: `https://<username>.github.io/<repo-name>/`

### Path A Server-Side Signals That Block Deployment

If any of the following are found, halt and recommend an appropriate platform:
- Node.js HTTP server, Express, .NET, Python (Flask/FastAPI/Django), Java, PHP, Ruby
- Databases: SQL Server, PostgreSQL, MySQL, MongoDB, Redis, SQLite (server-managed)
- SSR frameworks: Next.js SSR, Remix, SvelteKit SSR, Nuxt SSR
- Infrastructure: Dockerfile, docker-compose.yml, Kubernetes manifests, `*.csproj`, `pom.xml`

---

## Path B — `desktop` (signed installers)

The agent is responsible for **producing signed installers for every OS listed in `tech_stack.json#desktop_targets`**. Each installer is the deployment artifact for that OS; together they are the v1 release.

### Step B1 — Build all installers

Run `build_command` from `tech_stack.json`. For Electron projects this is typically `npm run build && npm run dist` (electron-builder), which writes installers to `dist/` or `release/`.

The build must produce one installer per entry in `desktop_targets[]`. Common formats:
- macOS: `.dmg` (preferred) or `.pkg`. Universal (Intel + Apple Silicon) bundles preferred.
- Windows: `.msi`, NSIS `.exe`, or `.appx`. x64 minimum; arm64 if the project targets Windows on ARM.
- Linux: `.AppImage`, `.deb`, `.rpm`, or `.snap`.

Capture the build log to `.agents/artifacts/stage-9/build.log` and the exit code to `.agents/artifacts/stage-9/build.exit`.

### Step B2 — Code-sign and notarize (per-OS)

For each `desktop_targets[]` entry, follow the platform's standard signing path:

- **macOS**: sign with the project's Apple Developer ID (`codesign --deep --options=runtime --sign "<Developer ID Application: ...>"` on the `.app` bundle, then re-package the `.dmg`). Notarize via `xcrun notarytool submit ... --wait` and staple with `xcrun stapler staple <installer.dmg>`. Verify with `spctl --assess --type install <installer.dmg>` — must report `accepted`.
- **Windows**: sign with `signtool sign /tr http://timestamp.digicert.com /td sha256 /fd sha256 /a <installer.msi>` (or PowerShell `Set-AuthenticodeSignature`). Verify with `signtool verify /pa <installer.msi>` — must report `Successfully verified`.
- **Linux**: signing is platform-specific (`debsigs` for `.deb`, GPG signature for `.AppImage`/`.snap`). Document the chosen approach in `deployment_config.json`.

If the project does not yet have signing certs configured, **halt** with a clear list of what's missing and what the operator must do (`Apple Developer ID + notarization profile` / `Authenticode certificate from a public CA`). Do not produce unsigned installers and call them deployable.

### Step B3 — Write `deployment_config.json`

```json
{
  "target": "desktop",
  "version": "<from package.json#version>",
  "desktop_targets": [
    {
      "os": "macos",
      "installer_path": "release/MyApp-1.0.0.dmg",
      "installer_size_bytes": 87210432,
      "sha256": "<sha256-of-installer>",
      "signature": {
        "method": "Apple Developer ID + notarization",
        "verified": true,
        "verify_command": "spctl --assess --type install release/MyApp-1.0.0.dmg",
        "verify_output_excerpt": "release/MyApp-1.0.0.dmg: accepted"
      }
    },
    {
      "os": "windows",
      "installer_path": "release/MyApp-1.0.0.msi",
      "installer_size_bytes": 64812032,
      "sha256": "<sha256-of-installer>",
      "signature": {
        "method": "Authenticode SHA256",
        "verified": true,
        "verify_command": "signtool verify /pa release/MyApp-1.0.0.msi",
        "verify_output_excerpt": "Successfully verified: release/MyApp-1.0.0.msi"
      }
    }
  ],
  "release_channel": "github-releases",
  "release_url_pattern": "https://github.com/<owner>/<repo>/releases/tag/v<version>",
  "notes": "Distribution: GitHub Releases. Auto-update via electron-updater feed in package.json."
}
```

### Step B4 — Verify gate

```bash
python .agents/skills/stage-9-deploy/verify/desktop_deploy.py .agents/artifacts/stage-9/deployment_config.json
```

The verifier checks:
- `target == "desktop"` and `desktop_targets[]` is non-empty
- Each `installer_path` exists on disk and `installer_size_bytes` matches
- Each `signature.verified` is `true` (signing was claimed)
- Each `sha256` is a valid 64-char hex string
- `version` matches `package.json#version` (advisory)

Exit non-zero → halt with the failure list.

### Step B5 — Distribute (operator step, not automated)

Stage 9 stops short of pushing the installers to a public release channel. Surface a checklist:
- Upload the signed installers to the release channel listed in `deployment_config.json#release_channel` (typically GitHub Releases — `gh release create v<version> <installer.dmg> <installer.msi> ...`).
- Update the project's website or README with the download links.
- Tag the commit with `git tag v<version>` and push.

The operator (a human) confirms distribution; Stage 9 does not push the release for you.

---

## Outputs

| Artifact | Path |
|---|---|
| Deployment config | `.agents/artifacts/stage-9/deployment_config.json` |
| Build log (desktop) | `.agents/artifacts/stage-9/build.log` |
| Build exit code (desktop) | `.agents/artifacts/stage-9/build.exit` |

## Gate

- **Web:** human confirmation that the deployment URL is accessible.
- **Desktop:** automated — `python .agents/skills/stage-9-deploy/verify/desktop_deploy.py .agents/artifacts/stage-9/deployment_config.json` exits 0.
