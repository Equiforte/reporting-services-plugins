---
name: xlsx-generator
description: >
  Generates branded Excel spreadsheets with live formulas. Triggered when the user
  asks to "create a spreadsheet", "build a financial model", "generate an Excel file",
  "export as XLSX", "make a workbook", "Excel report", "revenue model", "budget
  spreadsheet", or references Excel/XLSX output for data, models, or analysis.
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - Edit
---

# XLSX Generator

Generate branded Excel spreadsheets using openpyxl. Core philosophy: **always use formulas, never hardcoded calculated values**. Spreadsheets must remain dynamic.

## Before generating

### Branding guard

Before generating output, check that `{WORKING_DIR}/.reporting-resolved/brand-config.json` exists. If it does not, tell the user: "The branding plugin is required but has not run. Please install the `branding` plugin and run `/reporting-plugins:brand` first." Do not produce unbranded output.

### Data source priority

If a JSON data file was generated earlier in this session (in `output/text/`), read it as the canonical data source to ensure cross-format parity. If no prior JSON exists, use data from the conversation context directly. When generating both XLSX and CSV, generate the XLSX first and derive the CSV from the same data to prevent drift.

### Read brand config

Read `.reporting-resolved/brand-config.json` for brand values.

### Install dependencies

```bash
pip install openpyxl pandas
```

## Output conventions

- **Directory**: `output/xlsx/`
- **File naming**: `{slug}-{YYYY-MM-DD}-{HHmm}-{xxx}.xlsx`
- **Slug rules**: kebab-case, alphanumeric and hyphens only.

## Core philosophy: formulas first

Every calculated value MUST use an Excel formula. Never hardcode the result of a calculation.

```python
# WRONG — hardcoded value
ws["C2"] = 6000000  # Year 2 revenue

# RIGHT — formula
ws["C2"] = "=B2*(1+B5)"  # Year 2 = Year 1 * (1 + growth rate)
```

This ensures the spreadsheet remains dynamic — users can change inputs and see results update.

## Color coding standard

Apply these text colors to indicate cell types:

| Cell type | Color (RGB) | Example |
|-----------|-------------|---------|
| Hardcoded inputs | Blue (0, 0, 255) | Revenue assumptions, growth rates |
| Formulas | Black (0, 0, 0) | Calculated totals, derived metrics |
| Cross-sheet links | Green (0, 128, 0) | References to other worksheets |
| External links | Red (255, 0, 0) | References to other workbooks |

Background highlight:
- Yellow background: key assumptions that drive the model

```python
from openpyxl.styles import Font, PatternFill

# Input cell (blue text)
ws["B2"].font = Font(color="0000FF")

# Formula cell (black text, default)
ws["C2"].font = Font(color="000000")

# Key assumption (yellow background)
ws["B5"].fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
```

## Branded formatting

### Header row

```python
from openpyxl.styles import Font, PatternFill, Alignment

header_bg = brand["components"]["table_header_bg"].lstrip("#")
header_text = brand["components"]["table_header_text"].lstrip("#")

for cell in ws[1]:  # First row
    cell.font = Font(
        name=brand["typography"]["font_family"].split(",")[0].strip(),
        bold=True,
        color=header_text,
    )
    cell.fill = PatternFill(start_color=header_bg, end_color=header_bg, fill_type="solid")
    cell.alignment = Alignment(horizontal="center")
```

### Alternating rows

```python
alt_row_color = brand["components"]["table_alt_row"].lstrip("#")

for row_idx in range(2, ws.max_row + 1):
    if row_idx % 2 == 0:
        for cell in ws[row_idx]:
            cell.fill = PatternFill(start_color=alt_row_color, end_color=alt_row_color, fill_type="solid")
```

### Standard formatting

- **Freeze panes at A2** — header row always visible
- **Auto-filter on headers** — enable dropdown filters
- **Column widths**: auto-fit or set reasonable defaults (12-18 characters)
- **Number formats**: use `number_formats.*` from brand config
  - Currency columns: `$#,##0` or `$#,##0.00`
  - Percentage columns: `0.0%`
  - Year columns: text format `0` (prevents "2,026")
  - Integer columns: `#,##0`
- **Font**: `font_family` from brand config (Calibri default)
- **Tab color**: use brand `colors.accent` (without `#`)

```python
# Freeze panes
ws.freeze_panes = "A2"

# Auto-filter
ws.auto_filter.ref = ws.dimensions

# Number format
ws["B2"].number_format = '$#,##0'
ws["C2"].number_format = '0.0%'

# Tab color
ws.sheet_properties.tabColor = brand["colors"]["accent"].lstrip("#")
```

## Validation: formula recalculation

After building the spreadsheet, run `recalc.py` to verify formulas:

```bash
# Read office scripts path from resolved brand config
OFFICE_SCRIPTS=$(python3 -c "import json; print(json.load(open('.reporting-resolved/brand-config.json'))['_office_scripts_path'])")

python "$OFFICE_SCRIPTS/soffice.py" recalc output/xlsx/model.xlsx
```

Then check for formula errors:

```python
import openpyxl

wb = openpyxl.load_workbook("output/xlsx/model.xlsx", data_only=True)
errors = []
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for cell in row:
            if isinstance(cell.value, str) and cell.value.startswith("#"):
                errors.append({
                    "sheet": ws.title,
                    "cell": cell.coordinate,
                    "error": cell.value,
                })

result = {"error_count": len(errors), "error_cells": errors}
```

### Mode: best_effort (default)

If `recalc.py` finds errors, warn the user: "N formula errors detected in cells: ..." and continue. Produce the XLSX anyway.

### Mode: strict

If `recalc.py` finds errors:
1. Emit `{name}.validation.json` sidecar with per-cell error details.
2. Read the sidecar and attempt to fix the formulas (one retry).
3. Re-run `recalc.py` after the fix.
4. If errors persist on the second run, report to the user: "Formula errors could not be auto-corrected — see validation.json."

### Validation sidecar format

```json
{
  "artifact": "revenue-model-2026-04-04-1430-c3a.xlsx",
  "mode": "strict",
  "checks": [
    { "check": "formula_recalc", "status": "fail", "detail": "2 errors: C5=#REF!, D8=#VALUE!" },
    { "check": "font_resolution", "status": "pass", "detail": "Calibri" },
    { "check": "brand_applied", "status": "pass" }
  ],
  "overall": "fail"
}
```

## Common pitfalls

- **Column references**: Column 64 = BL, not BK. Double-check letter math for wide spreadsheets.
- **DataFrame offset**: pandas DataFrame row 5 = Excel row 6 (header row offset). Account for this when mixing pandas and openpyxl.
- **Year formatting**: Always format year columns as text `0`. Without this, `2026` displays as `2,026`.
- **Professional fonts only**: Use Calibri (default) or Arial. No decorative fonts in spreadsheets.
