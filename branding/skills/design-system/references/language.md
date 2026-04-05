# Language & Terminology Reference

Standard terminology, disclaimers, and labeling conventions for all output formats.

## Confidence Labels

Use these consistently when expressing certainty about data or projections:

| Level | Label | Color | Usage |
|-------|-------|-------|-------|
| High | "High confidence" | `colors.positive` | Verified data, historical actuals, confirmed facts |
| Medium | "Moderate confidence" | `colors.warning` | Estimates, forecasts with reasonable basis |
| Low | "Low confidence" | `colors.negative` | Projections with significant uncertainty, early-stage estimates |

Display as a colored badge or inline label: `[High confidence]` with background from the corresponding semantic `*_bg` token.

## Disclaimers

### Confidentiality notice

Use `content.confidentiality_notice` in headers/footers of all documents.
Default: "CONFIDENTIAL — For internal use only."

### General disclaimer

Use `content.disclaimer` on cover pages or document endings.
Default: "This document is for informational purposes only and does not constitute professional advice."

### As-of date

Every document should state when data was current:
- Format: "Data as of {date}" using `content.date_format`
- Position: below the title or in the document metadata
- Style: `font_size_caption`, `semantic.muted_color`, italic

## Source Citations

When referencing data sources:
- Format: "Source: {source name}, {date}" 
- Position: below the relevant table, chart, or figure
- Style: `font_size_caption`, `semantic.muted_color`, italic
- In `meta.sources`: include all sources as an array for provenance tracking

Example: *Source: Internal sales database, April 2026*

## Terminology Conventions

### Numbers
- Use `number_formats.*` tokens for all numeric display
- Negative values in parentheses: ($1,234) not -$1,234
- Large numbers: use abbreviations in KPI cards (e.g., $12.4M, $3.1B) but full values in tables
- Always include units in headers, not repeated per cell

### Dates
- Use `content.date_format` for all dates
- Default: "MMMM D, YYYY" (e.g., "April 4, 2026")
- In tables: shorter format acceptable (e.g., "Apr 4, 2026" or "2026-04-04")

### Percentages
- Always include the % sign
- One decimal place by default (8.2%, not 8%)
- Delta indicators: prefix with + for positive ("+8.2%"), no prefix for negative ("−3.1%")
- Use `colors.positive` for positive deltas, `colors.negative` for negative

### Currency
- Default to USD ($) unless context specifies otherwise
- Use `number_formats.currency` for integer amounts, `number_formats.currency_decimals` for precise amounts
- State currency in headers for tables with monetary values

## Tone

- **Factual and neutral**: state findings without editorializing
- **Precise**: use exact numbers from data, not approximations
- **Professional**: formal register, no contractions, no colloquialisms
- **Active voice**: prefer "Revenue grew 8.2%" over "An 8.2% growth in revenue was observed"
