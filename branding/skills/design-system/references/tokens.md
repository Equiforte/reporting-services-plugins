# Design Tokens Reference

All values below reference fields in the resolved `brand-config.json`. Read from `.reporting-resolved/brand-config.json` at generation time.

## Color Palette

### Raw colors (`colors.*`)

| Token | Default | Usage |
|-------|---------|-------|
| `primary` | #1B3A5C | Primary brand color — headers, title bars, slide masters, chart primary |
| `accent` | #2E75B6 | Secondary brand color — links, highlights, chart secondary |
| `text` | #2D2D2D | Body text color across all formats |
| `text_secondary` | #666666 | Captions, footnotes, metadata text |
| `surface` | #F7F8FA | Background for cards, alternating table rows, callout boxes |
| `positive` | #1A7A3A | Positive values, growth indicators, success states |
| `warning` | #C67700 | Caution indicators, moderate risk |
| `negative` | #C4261D | Negative values, decline indicators, error states |
| `critical` | #8B0000 | Critical alerts, severe risk |
| `white` | #FFFFFF | White backgrounds, inverted text on dark surfaces |

### Semantic tokens (`semantic.*`)

Derived from `colors` if not explicitly set. Use these for context-specific styling:

| Token | Derived from | Usage |
|-------|-------------|-------|
| `heading_color` | `colors.primary` | All heading text (H1, H2, H3) across formats |
| `body_color` | `colors.text` | Body paragraph text |
| `muted_color` | `colors.text_secondary` | Captions, secondary labels |
| `border_color` | Lightened `text_secondary` | Table borders, dividers, card borders |
| `link_color` | `colors.accent` | Hyperlinks in HTML, PDF |
| `surface_alt` | Lightened `surface` | Alternating backgrounds, nested surfaces |
| `success_bg` | Lightened `positive` | Background for positive callouts |
| `warning_bg` | Lightened `warning` | Background for warning callouts |
| `error_bg` | Lightened `negative` | Background for error callouts |
| `chart_series` | Array of 5 colors | Ordered palette for chart data series |

### Component tokens (`components.*`)

| Token | Default | Usage |
|-------|---------|-------|
| `table_header_bg` | `colors.primary` | Table header row background |
| `table_header_text` | `colors.white` | Table header row text |
| `table_alt_row` | `colors.surface` | Alternating row background |
| `card_radius` | 8px | Border radius on cards, containers |
| `card_shadow` | 0 1px 3px rgba(0,0,0,0.12) | Card drop shadow |
| `callout_border_width` | 3px | Left-border width on callout boxes |
| `footer_height` | 40px | Footer area height (PDF, DOCX, PPTX, HTML) |
| `header_height` | 60px | Header area height |
| `logo_max_height` | 40px | Maximum logo display height |

## Typography

| Token | Default | Usage |
|-------|---------|-------|
| `font_family` | Calibri, sans-serif | Body text, table cells, general content |
| `font_family_heading` | Calibri, sans-serif | Headings (H1-H3), title pages, slide titles |
| `font_family_mono` | Consolas, monospace | Code blocks, data labels, formulas |

### Size scale

| Token | Default (pt) | Usage |
|-------|-------------|-------|
| `font_size_h1` | 28 | Document title, slide title |
| `font_size_h2` | 22 | Section heading |
| `font_size_h3` | 16 | Subsection heading |
| `font_size_body` | 11 | Body text, table cells |
| `font_size_caption` | 9 | Footnotes, source citations, disclaimers |

## Spacing

Base unit: **4px**. Use multiples:

| Multiplier | Value | Usage |
|-----------|-------|-------|
| 1x | 4px | Tight spacing — between icon and label |
| 2x | 8px | Default inner padding |
| 3x | 12px | Between related elements |
| 4x | 16px | Section inner padding |
| 6x | 24px | Between sections |
| 8x | 32px | Major section gaps |
| 12x | 48px | Page-level margins (approximation — actual margins use `layout.*` in points) |

## Number Formatting

Use these Excel-style format strings for all numeric display:

| Token | Format | Example | Usage |
|-------|--------|---------|-------|
| `currency` | $#,##0 | $1,234 | Currency without decimals |
| `currency_decimals` | $#,##0.00 | $1,234.56 | Currency with decimals |
| `percentage` | 0.0% | 8.2% | Percentage values |
| `multiple` | 0.0x | 2.5x | Multiples, ratios |
| `integer` | #,##0 | 1,234 | Integer values with thousands separator |
| `year` | 0 | 2026 | Year values (no thousands separator) |

Negative numbers: use parentheses, e.g., `($1,234)` not `-$1,234`.
