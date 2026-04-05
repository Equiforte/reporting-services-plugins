---
name: pdf-generator
description: >
  Generates branded PDF documents. Triggered when the user asks to "create a PDF",
  "generate a PDF report", "export as PDF", "make a PDF", "build a PDF document",
  "PDF summary", "PDF memo", or references PDF output for reports, memos, proposals,
  or summaries.
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - Edit
---

# PDF Generator

Generate branded PDF documents using Python libraries. Supports creation from scratch, form filling, merge/split, watermarks, and conversion to images.

## Before generating

### Branding guard

Before generating output, check that `{WORKING_DIR}/.reporting-resolved/brand-config.json` exists. If it does not, tell the user: "The branding plugin is required but has not run. Please install the `branding` plugin and run `/reporting-plugins:brand` first." Do not produce unbranded output.

### Data source priority

If a JSON data file was generated earlier in this session (in `output/text/`), read it as the canonical data source to ensure cross-format parity. If no prior JSON exists, use data from the conversation context directly.

### Read brand config

Read `.reporting-resolved/brand-config.json` for all brand values. Read the logo from `.reporting-resolved/logo.png` (if it exists — it may have been suppressed).

### Install dependencies

If not already installed, run:
```bash
pip install reportlab pypdf pdfplumber pypdfium2
```
Or use the plugin's `requirements.txt`:
```bash
pip install -r {PLUGIN_ROOT}/requirements.txt
```

## Output conventions

- **Directory**: `output/pdf/`
- **File naming**: `{slug}-{YYYY-MM-DD}-{HHmm}-{xxx}.pdf`
- **Slug rules**: kebab-case, alphanumeric and hyphens only.

## Library selection

| Task | Library | Notes |
|------|---------|-------|
| Create new PDFs | **reportlab** | Programmatic generation with full layout control |
| Merge, split, rotate pages | **pypdf** | Page-level operations on existing PDFs |
| Extract text and tables | **pdfplumber** | Layout-preserving extraction |
| Render PDF to images | **pypdfium2** | Fast page-to-PNG conversion for QA |

## Creating PDFs with reportlab

### Page setup

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate

doc = SimpleDocTemplate(
    output_path,
    pagesize=letter,
    topMargin=brand["layout"]["margin_top"],
    bottomMargin=brand["layout"]["margin_bottom"],
    leftMargin=brand["layout"]["margin_left"],
    rightMargin=brand["layout"]["margin_right"],
)
```

### Branded header and footer

Every page must include:

**Header**:
- Logo left-aligned (if not suppressed), max height `components.logo_max_height`
- Firm name right-aligned, `font_size_caption`, `semantic.muted_color`
- Height: `components.header_height`

**Footer**:
- `content.confidentiality_notice` left-aligned, `font_size_caption`, `semantic.muted_color`
- Page number right-aligned ("Page X of Y")
- Height: `components.footer_height`

### Styling

- Document title: `font_size_h1`, `semantic.heading_color`, `font_family_heading`, bold
- Section headings: `font_size_h2`, `semantic.heading_color`, `font_family_heading`
- Body text: `font_size_body`, `colors.text`, `font_family`
- Tables: header row `components.table_header_bg` background, `components.table_header_text` text; alternating rows with `components.table_alt_row`
- Numbers right-aligned, formatted per `number_formats.*`

### Critical constraints

- **Subscript/superscript**: Use XML tags `<sub>` and `<super>` in reportlab Paragraph markup. NEVER use Unicode subscript/superscript characters — they render incorrectly in reportlab.
- **Fonts**: Use `font_family` from brand config. If the font is not registered with reportlab, fall back to Helvetica and log a warning.
- **Images**: Always specify width and height. Use `logo_max_height` for the logo.

## Validation

### Mode: best_effort (default)
- Generate the PDF. If any non-critical issue occurs (e.g., font fallback), log a warning and continue.

### Mode: strict
- After generation, verify:
  - PDF is valid (can be opened by pypdf without errors)
  - All brand elements are present (logo if not suppressed, firm name, confidentiality notice)
  - Page count is reasonable
- Emit `{name}.validation.json` sidecar with per-check results.
- If validation fails, attempt to fix once. If it fails a second time, report to the user.

## Form filling

For detailed form-filling workflows (fillable fields vs. annotation-based), see `forms.md`.

## Advanced operations

For merge/split/rotate (pypdf), text extraction (pdfplumber), and image conversion (pypdfium2), see `reference.md`.

## Website rendering rule

If `firm.name` was overridden in the brand config but `firm.website` was NOT explicitly set by the user, do not render `firm.website` anywhere in the PDF. The default Acme URL must never appear alongside a non-Acme firm name.
