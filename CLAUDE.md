# Reporting Services Plugins — Development Guide

## Repository structure

This is a Claude Code mono-repo plugin. Each subdirectory is an independently installable plugin registered in `.claude-plugin/marketplace.json`.

- `branding/` — Core plugin (required). Branding, design system, office utilities, orchestration.
- `document-generation/` — PDF and DOCX generators.
- `presentation-generation/` — PPTX generator.
- `spreadsheet-generation/` — XLSX and CSV generators.
- `text-generation/` — Markdown, HTML, TXT, and JSON generators.
- `apps-generation/` — Interactive React app generator (dashboard, report, comparison, timeline). Has shadcn MCP in `.mcp.json`.
- `_tests/` — Test suite (brand resolution, schema validation, office utilities, build scripts).

## Key architecture

- **`.reporting-resolved/`** is the bridge between plugins. The `brand` skill writes resolved config, assets, and office scripts there. All generators read from it. Never read from another plugin's `{PLUGIN_ROOT}` directly.
- **Skills only, no commands.** Skills trigger contextually via `description` frontmatter and can be invoked explicitly via `/reporting-plugins:skill-name`.
- **Output goes to `output/{format}/`** in the working directory. File naming: `{slug}-{YYYY-MM-DD}-{HHmm}-{xxx}.{ext}`.
- **Orchestration skill** coordinates multi-format requests: brand first, data-first JSON, sequential generators, validate, summarize.

## Orchestration flow

```
1. RESOLVE BRAND     → .reporting-resolved/
2. DATA-FIRST        → output/text/{data}.json (if multi-format)
3. GENERATE          → each generator sequentially
4. VALIDATE          → per-generator (mode-dependent)
5. SELF-CORRECT      → one retry in strict mode
6. SUMMARIZE         → file list with status
```

- Brand failure → stop entirely, offer to fix.
- Generator failure → continue with remaining, report partial success.
- Strict validation failure → retry once, then report to user.

## Adding a new generator plugin

1. Create `{name}/.claude-plugin/plugin.json` with name, version, description, author.
2. Create `{name}/skills/{generator}/SKILL.md` with:
   - `description` frontmatter with trigger phrases
   - Branding guard: check `.reporting-resolved/brand-config.json` exists
   - Data source priority: read from prior JSON if available
   - Slug sanitization: kebab-case, alphanumeric + hyphens only
3. Add `requirements.txt` (Python) or `package.json` (Node.js).
4. Register in `.claude-plugin/marketplace.json`.
5. Read brand from `.reporting-resolved/`, not from `branding/` directly.
6. Write output to `output/{format}/`.
7. Add tests to `_tests/`.

## Brand config

Default: `branding/skills/brand/assets/brand-config.json` (Acme Inc).
Schema: `branding/skills/brand/assets/brand-config.schema.json`.
User override: `{WORKING_DIR}/.reporting/brand-config.json` (deep-merged).
NL override: `{WORKING_DIR}/.claude/branding.local.md` (disabled with `nl_overrides: false`).

### Token derivation order

1. Defaults
2. JSON merge
3. NL overrides (if enabled)
4. Derive semantic + component tokens from final colors
5. Resolve assets (logo suppression if firm.name overridden without custom logo)
6. Write `.reporting-resolved/` (full delete + recreate)

## Design system

- `branding/skills/design-system/references/tokens.md` — color, typography, spacing, number formats
- `branding/skills/design-system/references/components.md` — table, KPI, chart, header, callout patterns
- `branding/skills/design-system/references/language.md` — terminology, confidence labels, disclaimers

## Office utilities

Live in `branding/scripts/office/`. Generators find them via `_office_scripts_path` in `.reporting-resolved/brand-config.json`:

- `soffice.py` — headless LibreOffice (convert, recalc)
- `pack.py` / `unpack.py` — Office ZIP manipulation
- `validate.py` — XSD validation + XXE stripping
- `helpers/` — merge_runs.py, simplify_redlines.py

## Apps generation

Stack: Vite + React + TypeScript + Tailwind CSS + shadcn/ui + Recharts.
Components: card, table, badge, tabs, chart, sidebar, select, button, dropdown-menu, avatar, breadcrumb, tooltip, collapsible, separator, scroll-area.
MCP: shadcn MCP server configured in `apps-generation/.mcp.json`.
Templates: dashboard (sidebar + KPIs + charts + tables), report (sidebar TOC + sections), comparison (cards grid + radar), timeline (vertical + collapsible).
Pre-initialized base: `_base/base.tar.gz` — rebuild with `scripts/rebuild-base.sh`.

## Testing

```bash
# All tests
bash _tests/run_all.sh

# By profile
bash _tests/run_all.sh --profile text-only     # brand + schema only
bash _tests/run_all.sh --profile documents      # + office utilities
bash _tests/run_all.sh --profile full           # + build scripts
```

Test types:
- `brand-resolution/` — JSON merge, token derivation, override logic
- `schema-validation/` — brand-config.json vs schema
- `office-utilities/` — pack/unpack roundtrip, XXE stripping, security
- `build-scripts/` — verify-self-contained.sh with good/bad inputs
- `fixtures/` — test data (globex override, strict mode, invalid JSON)
