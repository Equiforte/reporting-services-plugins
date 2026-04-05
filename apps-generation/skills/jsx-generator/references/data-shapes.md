# Data Shapes Reference

JSON schema for each template's `data.json`. The `meta` section is common to all templates.

## Common: `meta` section

```json
{
  "meta": {
    "title": "string (required)",
    "generated_at": "string (ISO 8601, required)",
    "confidential": "boolean (default: true)",
    "firm": "string (from brand config)",
    "sources": ["string[]"]
  }
}
```

## Dashboard template

```json
{
  "meta": { ... },
  "kpis": [
    {
      "label": "string — metric name",
      "value": "string — formatted display value (e.g., '$12.4M')",
      "raw_value": "number — numeric value for calculations",
      "delta": "string — change indicator (e.g., '+8.2%')",
      "trend": "'up' | 'down' | 'flat'",
      "unit": "string — optional unit label"
    }
  ],
  "charts": [
    {
      "type": "'bar' | 'line' | 'area' | 'pie' | 'doughnut'",
      "title": "string",
      "labels": ["string[] — x-axis labels"],
      "datasets": [
        {
          "name": "string — series name",
          "values": ["number[] — data points"]
        }
      ]
    }
  ],
  "tables": [
    {
      "title": "string",
      "columns": [
        {
          "key": "string — field name",
          "label": "string — display header",
          "align": "'left' | 'right' | 'center'",
          "format": "string — optional format type ('currency', 'percentage', 'integer')"
        }
      ],
      "rows": [
        { "field_key": "value", ... }
      ]
    }
  ]
}
```

## Report template

```json
{
  "meta": { ... },
  "sections": [
    {
      "id": "string — for hash navigation (#section-id)",
      "heading": "string — section title",
      "level": "number — 1 for H1, 2 for H2, 3 for H3",
      "content": "string — markdown or plain text content",
      "figures": [
        {
          "type": "'table' | 'chart' | 'kpi-row'",
          "data": "object — matches the table/chart/kpi schema above"
        }
      ]
    }
  ]
}
```

## Comparison template

```json
{
  "meta": { ... },
  "comparison": {
    "title": "string — comparison title",
    "items": [
      {
        "name": "string — item name (e.g., 'Starter', 'Pro', 'Enterprise')",
        "subtitle": "string — optional subtitle (e.g., '$29/mo')",
        "highlighted": "boolean — visual emphasis (e.g., recommended tier)",
        "attributes": {
          "attribute_key": {
            "value": "string — display value",
            "raw_value": "number | string — for sorting/comparison",
            "better": "'higher' | 'lower' | null — comparison direction"
          }
        }
      }
    ],
    "attribute_labels": {
      "attribute_key": "string — display label for the attribute"
    }
  }
}
```

## Timeline template

```json
{
  "meta": { ... },
  "timeline": {
    "title": "string — timeline title",
    "events": [
      {
        "date": "string — display date",
        "iso_date": "string — ISO 8601 for sorting",
        "title": "string — event title",
        "description": "string — event details",
        "status": "'completed' | 'in-progress' | 'upcoming' | 'blocked'",
        "tags": ["string[] — category labels"],
        "details": {
          "key": "value — expandable detail fields"
        }
      }
    ]
  }
}
```
