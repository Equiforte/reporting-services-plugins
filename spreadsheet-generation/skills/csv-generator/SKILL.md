---
name: csv-generator
description: >
  Generates CSV data export files. Triggered when the user asks to "export as CSV",
  "create a CSV file", "comma-separated values", "CSV export", "CSV dump",
  "download as CSV", or requests CSV output for tabular data.
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
---

# CSV Generator

Generate clean CSV data exports with proper encoding and formatting.

## Before generating

### Branding guard

Before generating output, check that `{WORKING_DIR}/.reporting-resolved/brand-config.json` exists. If it does not, tell the user: "The branding plugin is required but has not run. Please install the `branding` plugin and run `/reporting-plugins:brand` first." Do not produce unbranded output.

### Data source priority

If a JSON data file was generated earlier in this session (in `output/text/`), read it as the canonical data source to ensure cross-format parity. If no prior JSON exists, use data from the conversation context directly.

**When both XLSX and CSV are requested**: The XLSX must be generated FIRST. Derive the CSV from the same in-memory data used for the XLSX to prevent drift. Do not independently reconstruct the data from conversation context.

### Read brand config

Read `.reporting-resolved/brand-config.json` for number formatting rules and date format.

## Output conventions

- **Directory**: `output/csv/`
- **File naming**: `{slug}-{YYYY-MM-DD}-{HHmm}-{xxx}.csv`
- **Slug rules**: kebab-case, alphanumeric and hyphens only.

## CSV formatting rules

### Encoding

- **UTF-8 with BOM** (Byte Order Mark): `\xEF\xBB\xBF` at the start of the file. This ensures Excel opens the file with correct encoding.

```python
with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(headers)
    writer.writerows(data)
```

### Structure

- **Header row required** — first row must contain column names.
- **Quote minimal** — only quote fields that contain commas, newlines, or quotes.
- **Consistent columns** — every row must have the same number of fields.
- **No trailing commas** — no empty fields at end of rows.

### Data formatting

- **Numbers**: raw numeric values without formatting (e.g., `12400000` not `$12,400,000`). Formatting is the consumer's responsibility.
- **Dates**: ISO 8601 format (`2026-04-04`) for machine readability. If the user specifically requests formatted dates, use `content.date_format` from brand config.
- **Percentages**: decimal form (e.g., `0.082` not `8.2%`) for raw data. If the user requests formatted output, use `8.2%`.
- **Empty values**: empty string (two consecutive commas `,,`), not `null` or `N/A`.
- **Boolean**: `true` / `false` (lowercase).

### Column naming

- Use clear, descriptive column names.
- Use underscores or spaces (not camelCase): `revenue_q1` or `Revenue Q1`.
- Include units in column names where relevant: `revenue_usd`, `growth_pct`.
