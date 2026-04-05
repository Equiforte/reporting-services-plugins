---
name: jsx-generator
description: >
  Generates self-contained React applications for interactive output. Triggered
  when the user asks to "create a dashboard", "build an interactive report",
  "make a comparison view", "generate a timeline", "create a web app",
  "interactive dashboard", "KPI dashboard", "side-by-side comparison",
  "milestone timeline", or requests any interactive/visual output format.
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - Edit
---

# JSX Generator

Generate self-contained React applications using Vite + TypeScript + Tailwind CSS + shadcn/ui (https://ui.shadcn.com). Apps must work as `file://` — no server required, shareable as a folder.

## Stack

- **UI components**: shadcn/ui — card, table, badge, tabs, sidebar, select, button, dropdown-menu, avatar, breadcrumb, tooltip, collapsible, separator, scroll-area
- **Charts**: shadcn/ui chart component (https://ui.shadcn.com/charts) built on Recharts — area, bar, line, pie, radar charts with brand-themed colors
- **Sidebar**: shadcn/ui sidebar (https://ui.shadcn.com/docs/components/sidebar) — used by default in dashboard and report templates for navigation
- **MCP**: The shadcn MCP server is configured in `apps-generation/.mcp.json` — use it to look up component APIs, props, and examples during builds

See `references/components.md` for the full component reference with chart examples, sidebar patterns, and layout diagrams.

## Before generating

### Branding guard

Before generating output, check that `{WORKING_DIR}/.reporting-resolved/brand-config.json` exists. If it does not, tell the user: "The branding plugin is required but has not run. Please install the `branding` plugin and run `/reporting-plugins:brand` first." Do not produce unbranded output.

### Data source priority

If a JSON data file was generated earlier in this session (in `output/text/`), read it as the canonical data source to ensure cross-format parity. If no prior JSON exists, use data from the conversation context directly.

### Read brand config

Read `.reporting-resolved/brand-config.json` for brand values. Read logo from `.reporting-resolved/logo.png` (if exists).

### Ensure Node.js

Node.js 20+ is required. If not available, report error with install instructions.

## Output conventions

- **Directory**: `output/app/{app-name}/`
- **Naming**: descriptive directory names (not timestamped). Example: `output/app/q1-dashboard/`
- **Re-running**: overwrites the previous version. Apps are iterative artifacts, not archived snapshots.
- **Required contents** (all produced by `build.sh` — do not create manually):
  - `dist/` — **built app, ready to open via `file://`** ← this is the deliverable
  - `dist/index.html` — entry point the user opens in their browser
  - `dist/assets/*.js` — bundled JavaScript
  - `src/` — source code for rebuilds
  - `package.json` — dependencies for `npm install && npm run build`
  - `vite.config.ts` — Vite configuration
  - `tsconfig.json`, `tsconfig.app.json` — TypeScript config
  - `components.json` — shadcn/ui config
  - `data.json` — the data used to generate the app

**An output directory without `dist/index.html` is not a valid deliverable.** Raw `.jsx` or `.tsx` files alone cannot be opened in a browser.

## Template selection

Select template based on intent keywords in the user's request:

| Template | Trigger keywords | Layout |
|----------|-----------------|--------|
| **dashboard** | "dashboard", "KPIs", "metrics", "monitor", "overview" | Header + KPI cards grid + chart sections + data table |
| **report** | "report", "memo", "analysis", "brief", "summary" | Sidebar TOC + scrollable sections + figures |
| **comparison** | "compare", "benchmark", "vs", "side-by-side", "tier" | Split panes + delta highlights + radar/bar charts |
| **timeline** | "timeline", "milestones", "audit trail", "history", "roadmap" | Vertical timeline + expandable detail cards |

If ambiguous, default to **dashboard** for data-heavy requests or **report** for narrative-heavy requests.

## Build flow — MANDATORY

**CRITICAL**: Every invocation of this skill MUST produce a fully built Vite application by running `scripts/build.sh`. NEVER write raw `.jsx`, `.tsx`, or `.js` files directly to `output/app/`. Writing source files without building them is not a valid output — the user cannot open raw JSX in a browser.

**NEVER skip the build step.** Even if the JSX is correct, unbuilt source files are useless to the user. The build produces `dist/index.html` which is the actual deliverable.

The plugin ships with a **pre-initialized template base** (`_base/base.tar.gz`) — a fully scaffolded Vite + React + shadcn project. This avoids the 2-5 minute cold-start of `npm create vite` + `npx shadcn init`.

### Step-by-step procedure

Follow these steps in exact order. Do not skip any step.

#### 1. Prepare data

Write the app's data to a JSON file (e.g., `data.json`) in the working directory. This file will be injected into the app by the build script.

#### 2. Write source files

Write any custom React components (App.tsx, pages, etc.) to a temporary location. The build script will copy the selected template first, then custom source files override the template.

#### 3. Run build.sh

Execute the build script. This is the **mandatory** step that produces the final app:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/jsx-generator/scripts/build.sh \
  --template dashboard \
  --data $(pwd)/data.json \
  --brand $(pwd)/.reporting-resolved/brand-config.json \
  --logo $(pwd)/.reporting-resolved/logo.png \
  --output $(pwd)/output/app/my-dashboard \
  --plugin-dir ${CLAUDE_PLUGIN_ROOT}/skills/jsx-generator
```

**IMPORTANT**: Use absolute paths (`$(pwd)/...`) for `--output`, `--data`, `--brand`, and `--logo`. Relative paths will resolve incorrectly because the script changes directories internally.

The build script performs these steps automatically:
1. Extracts `_base/base.tar.gz` into a temp working directory
2. Copies the selected template (dashboard/report/comparison/timeline) into `src/`
3. Injects `data.json` into `public/`
4. Maps brand colors to Tailwind CSS custom properties, copies logo to `public/`
5. Sets `base: './'` in `vite.config.ts` (critical for `file://` access)
6. Runs `npm run build` → produces `dist/`
7. Runs `scripts/verify-self-contained.sh` on `dist/`
8. Copies `dist/`, `src/`, `package.json`, `vite.config.ts`, `tsconfig.json` to the output path

Typical build time with pre-initialized base: ~20 seconds.

#### 4. Validate output — REQUIRED

After `build.sh` completes, verify the output directory contains the required structure:

```bash
# All of these must exist — if any is missing, the build failed
test -f output/app/my-dashboard/dist/index.html || echo "FAIL: no dist/index.html"
test -d output/app/my-dashboard/dist/assets || echo "FAIL: no dist/assets/"
ls output/app/my-dashboard/dist/assets/*.js >/dev/null 2>&1 || echo "FAIL: no JS bundle"
test -f output/app/my-dashboard/package.json || echo "FAIL: no package.json"
test -d output/app/my-dashboard/src || echo "FAIL: no src/"
```

If validation fails, diagnose the build error and retry. Do not deliver an output directory that lacks `dist/index.html`.

#### 5. Report to user

Confirm the output path and list the key files:
- `dist/index.html` — open this in a browser (works via `file://`)
- `src/` — source code for future modification
- `data.json` — the data powering the app

## Self-containment rules

Enforced by `scripts/verify-self-contained.sh`. ALL must pass:

- **All data in `data.json`** — fetched with relative `./data.json`, no API calls
- **All fonts bundled locally** as woff2 — no Google Fonts CDN, no external font URLs
- **No root-absolute paths** — everything `./` relative. Vite `base: './'` is critical.
- **No React Router** — hash-based navigation only (`#section-name`)
- **Zero external network requests** at runtime — no CDN, no analytics, no external images
- **Required files in dist/**: `index.html`, `assets/` directory

## Branding integration

Map brand tokens to Tailwind CSS custom properties:

```css
/* In tailwind config or global CSS */
:root {
  --brand-primary: {colors.primary};
  --brand-accent: {colors.accent};
  --brand-text: {colors.text};
  --brand-surface: {colors.surface};
  --brand-heading: {semantic.heading_color};
  --brand-positive: {colors.positive};
  --brand-negative: {colors.negative};
  --brand-border: {semantic.border_color};
  --brand-card-radius: {components.card_radius};
  --brand-card-shadow: {components.card_shadow};
}
```

- Logo in header area (from `.reporting-resolved/logo.png`)
- Firm name in page title (`<title>`) and footer
- Confidentiality notice in footer
- shadcn/ui component theming via CSS custom properties

## Data contract

Each template defines a JSON schema in `references/data-shapes.md`. Prepare `data.json` matching the chosen template's schema.

### Provenance

Include `meta.sources` in `data.json` for provenance tracking:

```json
{
  "meta": {
    "title": "Dashboard Title",
    "generated_at": "2026-04-04T14:30:00Z",
    "confidential": true,
    "sources": ["source-1", "source-2"]
  },
  "data": { ... }
}
```

## Rebuilding the template base

When dependencies need updating (new shadcn components, Vite version bump):

```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/jsx-generator/scripts/rebuild-base.sh
```

This recreates `_base/base.tar.gz` with fresh `node_modules`, updated shadcn components, and latest Vite config.
