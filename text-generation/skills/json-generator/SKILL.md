---
name: json-generator
description: >
  Generates structured JSON data files with metadata. Triggered when the user asks
  to "export as JSON", "create a JSON file", "structured data export", "data dump",
  "export data", or requests JSON output. Also triggered automatically as the
  data-first step when multiple output formats are requested from the same data.
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
---

# JSON Generator

Generate structured JSON data files with metadata and provenance tracking. This skill serves two purposes:

1. **Standalone data export** — when the user explicitly asks for JSON output.
2. **Data-first canonical source** — when multiple formats are requested from the same data, this skill runs first to produce a single source of truth that other generators reference.

## Before generating

### Branding guard

Before generating output, check that `{WORKING_DIR}/.reporting-resolved/brand-config.json` exists. If it does not, tell the user: "The branding plugin is required but has not run. Please install the `branding` plugin and run `/reporting-plugins:brand` first." Do not produce unbranded output.

### Read brand config

Read `.reporting-resolved/brand-config.json` for firm name, date format, and confidentiality settings.

## Output conventions

- **Directory**: `output/text/`
- **File naming**: `{slug}-{YYYY-MM-DD}-{HHmm}-{xxx}.json`
- **Slug rules**: kebab-case, alphanumeric and hyphens only.

## JSON structure

Every JSON file must follow this structure:

```json
{
  "meta": {
    "title": "Document Title",
    "generated_at": "2026-04-04T14:30:00Z",
    "firm": "Acme Inc",
    "confidential": true,
    "sources": ["source-1", "source-2"]
  },
  "data": {
    // payload here
  }
}
```

### `meta` section (required)

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Document title |
| `generated_at` | string (ISO 8601) | Timestamp of generation |
| `firm` | string | Firm name from resolved brand config |
| `confidential` | boolean | True unless user explicitly says otherwise |
| `sources` | string[] | Data sources used (for provenance tracking) |

### `data` section (required)

The payload structure depends on the content. Common patterns:

**KPI data**:
```json
{
  "data": {
    "kpis": [
      { "label": "Revenue", "value": 12400000, "formatted": "$12.4M", "delta": "+8.2%", "trend": "up" }
    ]
  }
}
```

**Tabular data**:
```json
{
  "data": {
    "tables": [
      {
        "name": "Revenue by Quarter",
        "columns": ["Quarter", "Revenue", "Growth"],
        "rows": [
          ["Q1 2026", "$12.4M", "+8.2%"]
        ]
      }
    ]
  }
}
```

**Mixed content** (for data-first multi-format):
```json
{
  "data": {
    "kpis": [...],
    "tables": [...],
    "charts": [...],
    "sections": [
      { "heading": "Executive Summary", "content": "..." }
    ]
  }
}
```

## Formatting rules

- Pretty-printed with 2-space indent.
- Use `null` for missing values, not empty strings.
- Numeric values as numbers (not strings) in the `data` section. Include a `formatted` field alongside for display purposes.
- Dates as ISO 8601 strings.
- Arrays for ordered collections, objects for named properties.

## Data-first usage

When this skill runs as part of a multi-format request:

1. Structure the JSON to include ALL data that subsequent generators will need (KPIs, tables, charts, narrative sections).
2. Use the `formatted` field alongside raw values so generators can use either.
3. Write the file to `output/text/` before any other generator runs.
4. Subsequent generators (PDF, XLSX, dashboard) should read this file as their canonical data source.
