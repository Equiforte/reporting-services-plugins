# Reporting Services Plugins

A Claude Code mono-repo plugin for publishing reports. Covers everything related to putting data into a presentation, document, spreadsheet, dashboard, or any other deliverable format.

## Plugins

| Plugin | Formats | Dependencies |
|--------|---------|-------------|
| **branding** (core, required) | — | None |
| **text-generation** | Markdown, HTML, TXT, JSON | None |
| **document-generation** | PDF, DOCX | Python 3.10+, LibreOffice, pandoc, poppler |
| **spreadsheet-generation** | XLSX, CSV | Python 3.10+, LibreOffice |
| **presentation-generation** | PPTX | Node.js 20+, Python 3.10+ |
| **apps-generation** | Dashboard, Report, Comparison, Timeline | Node.js 20+ |

## Quick start

```bash
# Add the marketplace
claude plugin marketplace add {org}/reporting-plugins

# Install core (required)
claude plugin install branding@reporting-plugins

# Install the generators you need
claude plugin install text-generation@reporting-plugins
claude plugin install document-generation@reporting-plugins
claude plugin install spreadsheet-generation@reporting-plugins
claude plugin install presentation-generation@reporting-plugins
claude plugin install apps-generation@reporting-plugins
```

Then just ask:

> "Create a Q1 performance report as a PDF with revenue $12.4M, EBITDA $3.1M, headcount 142"

## Deployment profiles

Not every team needs every format. Install only what you need:

| Profile | Install | Dependencies |
|---------|---------|-------------|
| **text-only** | branding + text-generation | None |
| **documents** | + document-generation + spreadsheet-generation | Python, LibreOffice, pandoc, poppler |
| **presentations** | + presentation-generation | + Node.js |
| **full** | All plugins | Python, Node.js, LibreOffice, pandoc, poppler |

### Install dependencies (macOS)

```bash
brew install python node pandoc poppler
brew install --cask libreoffice
```

### Install Python/Node packages

```bash
pip install -r document-generation/requirements.txt
pip install -r spreadsheet-generation/requirements.txt
cd presentation-generation && npm install && cd ..
cd apps-generation && npm install && cd ..
```

## Branding

Every output is branded consistently. The plugin ships with **Acme Inc** defaults.

### Custom branding

Create `.reporting/brand-config.json` in your project to override any brand values:

```json
{
  "firm": {
    "name": "Your Company",
    "tagline": "Your tagline"
  },
  "colors": {
    "primary": "#003366",
    "accent": "#0077CC"
  }
}
```

Only override what you need — everything else falls back to defaults. See `branding/skills/brand/assets/brand-config.schema.json` for the full schema.

### Brand assets

Place custom assets in `.reporting/`:

```
.reporting/
├── brand-config.json       # Override brand values
├── logo.png                # Primary logo (400x100px recommended)
├── logo-dark.png           # Logo for dark backgrounds
├── icon.png                # Square icon (256x256px)
└── fonts/
    └── heading.woff2       # Custom heading font
```

### Natural language overrides

For quick tweaks, create `.claude/branding.local.md`:

```
Use a warm earth-tone palette.
Company name is "Terra Holdings".
Use serif fonts for headings.
```

Disable with `"nl_overrides": false` in `brand-config.json` for fully reproducible builds.

## Output

All output goes to `output/` in your working directory:

```
output/
├── pdf/          # PDF documents
├── docx/         # Word documents
├── pptx/         # PowerPoint decks
├── xlsx/         # Excel spreadsheets
├── csv/          # CSV exports
├── text/         # Markdown, HTML, TXT, JSON
└── app/          # Interactive React apps
```

## Validation modes

Set `"mode": "strict"` in `brand-config.json` for strict validation:

- Hard-fail on missing dependencies, formula errors, font issues
- Emit `.validation.json` sidecar alongside each artifact
- Auto-correction: agent fixes issues and retries once

Default is `"best_effort"` — warn and continue.

## Multi-format requests

When you request multiple formats, the agent:

1. Resolves branding first
2. Generates a canonical JSON data file (data-first pattern)
3. Generates each format from the same data — ensuring 100% data parity
4. Summarizes all outputs with file paths

## Testing

```bash
# Run all tests
bash _tests/e2e/run_all.sh

# Run by profile
bash _tests/e2e/run_all.sh --profile text-only
bash _tests/e2e/run_all.sh --profile documents
bash _tests/e2e/run_all.sh --profile full

# Run by test number
bash _tests/e2e/run_all.sh --test 10
```

## License

Apache 2.0
