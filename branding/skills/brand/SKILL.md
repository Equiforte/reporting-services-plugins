---
name: brand
description: >
  Resolves branding configuration for report output. Triggered when the user
  asks to "generate a report", "create a PDF", "build a dashboard", "make a
  presentation", "export as Excel", "create a slide deck", or any output-generation
  request. Also triggered when the user asks to "set up branding", "configure
  brand colors", "apply brand", or "resolve branding".
---

# Brand Resolution

Resolve branding configuration before any output generation. This skill runs first in every generation request — no generator should produce output without resolved branding.

## Resolution Flow

Execute these steps in order:

### Step 1: Read defaults

Read the default brand configuration from `${CLAUDE_PLUGIN_ROOT}/skills/brand/assets/brand-config.json`. This is the baseline — Acme Inc defaults with all 8 sections populated.

### Step 2: Deep-merge JSON overrides

Check if `{WORKING_DIR}/.reporting/brand-config.json` exists. If it does:

1. Parse it as JSON. If parsing fails, **stop entirely** — report the specific error (file path, line number, syntax issue), offer to fix it, and do NOT proceed with generation.
2. Deep-merge it onto the defaults. Only fields explicitly set in the override replace defaults. Nested objects are merged recursively (e.g., setting `colors.primary` does not erase `colors.accent`).
3. Note which fields were overridden for the resolution log.

Track which fields in the `firm` section were explicitly set by the user — this matters for logo suppression and website rendering rules.

### Step 3: Apply natural-language overrides

Check the resolved config for `"nl_overrides": false`. If false, skip this step entirely and log: "NL overrides disabled (nl_overrides: false)."

Otherwise, check if `{WORKING_DIR}/.claude/branding.local.md` exists. If it does:

1. Read the file content as natural-language instructions.
2. Interpret each instruction into concrete brand-config values.
3. **Precedence rule**: NL overrides may only set fields that were NOT explicitly set in the JSON override. JSON always wins.
4. Log each NL interpretation: what the instruction said, what field it mapped to, what value was chosen.

Examples of NL interpretation:
- "Use a warm earth-tone palette" → interpret as specific hex values for `colors.primary`, `colors.accent`, etc.
- "Company name is Terra Holdings" → set `firm.name` to "Terra Holdings"
- "Use serif fonts for headings" → set `typography.font_family_heading` to "Georgia, serif"

### Step 4: Derive semantic and component tokens

This step runs AFTER NL overrides so that any NL color changes are reflected in derived tokens.

For any field in the `semantic` section that is not explicitly set (by defaults, JSON, or NL), derive it from the final resolved `colors`:

| Semantic token | Derived from |
|---------------|-------------|
| `heading_color` | `colors.primary` |
| `body_color` | `colors.text` |
| `muted_color` | `colors.text_secondary` |
| `border_color` | Lighten `colors.text_secondary` by 40% → approximate `#D1D5DB` |
| `link_color` | `colors.accent` |
| `surface_alt` | Lighten `colors.surface` by 30% |
| `success_bg` | Lighten `colors.positive` to 90% lightness |
| `warning_bg` | Lighten `colors.warning` to 90% lightness |
| `error_bg` | Lighten `colors.negative` to 90% lightness |
| `chart_series` | `[colors.primary, colors.accent, colors.positive, colors.warning, colors.negative]` |

For any field in the `components` section that is not explicitly set:

| Component token | Derived from |
|----------------|-------------|
| `table_header_bg` | `colors.primary` |
| `table_header_text` | `colors.white` |
| `table_alt_row` | `colors.surface` |

Other component tokens (`card_radius`, `card_shadow`, `callout_border_width`, `footer_height`, `header_height`, `logo_max_height`) keep their defaults if not overridden.

### Step 5: Resolve assets

Check for asset overrides in `{WORKING_DIR}/.reporting/`:

| Asset | Override path | Default |
|-------|-------------|---------|
| Primary logo | `.reporting/logo.png` | `${CLAUDE_PLUGIN_ROOT}/skills/brand/assets/logo.png` |
| Dark logo | `.reporting/logo-dark.png` | `${CLAUDE_PLUGIN_ROOT}/skills/brand/assets/logo-dark.png` |
| Icon | `.reporting/icon.png` | `${CLAUDE_PLUGIN_ROOT}/skills/brand/assets/icon.png` |
| Watermark | `.reporting/watermark.png` | `${CLAUDE_PLUGIN_ROOT}/skills/brand/assets/watermark.png` |
| Custom fonts | `.reporting/fonts/*.woff2` | None (use system fonts from typography config) |

**Logo suppression rule**: If `firm.name` was overridden (via JSON or NL) but no custom `logo.png` exists in `.reporting/`, do NOT copy the default Acme logo. An overridden firm name with a mismatched logo is worse than no logo. Log: "Logo suppressed — firm.name overridden but no custom logo provided."

**Website rendering rule**: If `firm.name` was overridden but `firm.website` was NOT explicitly set in the user's JSON override, do not render `firm.website` in any output. The default Acme URL must never appear alongside a non-Acme firm name.

### Step 6: Write .reporting-resolved/

**Delete `{WORKING_DIR}/.reporting-resolved/` entirely if it exists.** Never merge incrementally with a prior run — full replacement prevents stale values from persisting.

Then create `.reporting-resolved/` and write:

1. **`brand-config.json`** — the fully resolved configuration with all 8 sections + top-level flags. Include an `_office_scripts_path` field set to the absolute path of `${CLAUDE_PLUGIN_ROOT}/scripts/office/` — this tells generators where to find the office utilities without copying them.
2. **`brand-resolution-log.md`** — audit trail documenting:
   - Which defaults were used
   - Which JSON fields were overridden (list each field and new value)
   - Which NL instructions were interpreted (original text → field → value)
   - Whether NL overrides were disabled
   - Whether logo was suppressed and why
   - Timestamp of resolution
3. **Asset files** — resolved `logo.png`, `logo-dark.png`, `icon.png`, `watermark.png` (or note which were suppressed).

Note: office scripts (`soffice.py`, `pack.py`, `unpack.py`, `validate.py`, `helpers/`) are NOT copied. They are static files that live in the branding plugin at `${CLAUDE_PLUGIN_ROOT}/scripts/office/`. Generators find them via the `_office_scripts_path` field in the resolved `brand-config.json`.

### Step 7: Confirm

Report to the user what was resolved:
- Firm name and branding source (defaults / JSON override / NL override)
- Whether strict mode or NL-disable is active
- Number of assets resolved
- Path to `.reporting-resolved/`

---

## Output Conventions

All generators must follow these output rules. Include this section's rules when instructing generators.

### Directory structure

All output goes to `{WORKING_DIR}/output/` with subdirectories per format:

| Format | Output path |
|--------|-----------|
| PDF | `output/pdf/` |
| DOCX | `output/docx/` |
| PPTX | `output/pptx/` |
| XLSX | `output/xlsx/` |
| CSV | `output/csv/` |
| Markdown, HTML, TXT, JSON | `output/text/` |
| Interactive apps | `output/app/{app-name}/` |

### File naming

Pattern: `{slug}-{YYYY-MM-DD}-{HHmm}-{xxx}.{ext}`

- **slug**: Kebab-case, alphanumeric and hyphens only. Strip or replace slashes, spaces, special characters, and non-ASCII. Example: `q1-performance-report`.
- **YYYY-MM-DD**: Date of generation.
- **HHmm**: 24-hour time of generation (hours and minutes).
- **xxx**: 3-character random hex suffix to prevent same-minute collisions.
- **ext**: Format-appropriate extension.

Example: `quarterly-review-2026-04-04-1430-a8f.pdf`

**Exception**: Interactive apps use descriptive directory names without timestamps (`output/app/q1-dashboard/`). Re-running overwrites the previous version.

### Provenance

Each generated file should include a `meta.sources` section (where the format supports it) listing the data sources used during generation.
