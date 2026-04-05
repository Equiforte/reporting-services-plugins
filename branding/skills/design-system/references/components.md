# Component Patterns Reference

Reusable visual patterns for all output formats. All colors, fonts, and spacing reference tokens from `tokens.md` — never hardcode values.

## Tables

**Standard data table**:
- Header row: `components.table_header_bg` background, `components.table_header_text` text, `font_family` bold
- Body rows: alternating `colors.white` and `components.table_alt_row`
- Text alignment: left for text columns, right for numeric columns
- Number formatting: use `number_formats.*` tokens (currency right-aligned, percentages right-aligned)
- Border: 1px `semantic.border_color` between rows
- Freeze panes at row 2 (XLSX), auto-filter on headers (XLSX)

**Financial table** (spreadsheets):
- Same as standard, plus color coding:
  - Blue text (0,0,255): hardcoded inputs
  - Black text (0,0,0): formulas
  - Green text (0,128,0): cross-sheet links
  - Red text (255,0,0): external links
  - Yellow background: key assumptions

## KPI Cards

Layout: 3-4 cards per row, equal width.

Each card contains:
- **Value**: `font_size_h1`, `semantic.heading_color`, bold
- **Label**: `font_size_body`, `semantic.muted_color`
- **Delta** (optional): `colors.positive` for positive, `colors.negative` for negative, with arrow indicator
- **Card styling**: `components.card_radius` border radius, `components.card_shadow` shadow, `colors.white` background, 16px inner padding

## Charts

- Data series use `semantic.chart_series` palette in order
- Background: `colors.white`
- Grid lines: `semantic.border_color` at 50% opacity
- Axis labels: `font_size_caption`, `semantic.muted_color`
- Chart title: `font_size_h3`, `semantic.heading_color`
- Source citation: below chart, `font_size_caption`, `semantic.muted_color`, italic
- Always label axes with units

## Section Headers

- Left border: 3px solid `semantic.heading_color`
- Text: `font_size_h2`, `semantic.heading_color`, `font_family_heading`
- Bottom margin: 12px (3x spacing)
- In PPTX: use a colored title bar (`colors.primary` background, `colors.white` text)

## Callout Boxes

- Background: `colors.surface`
- Left border: `components.callout_border_width` solid `colors.accent`
- Text: `font_size_body`, `colors.text`
- Inner padding: 16px (4x spacing)
- Border radius: `components.card_radius`

Variants by severity:
- **Info**: left border `colors.accent`, background `colors.surface`
- **Success**: left border `colors.positive`, background `semantic.success_bg`
- **Warning**: left border `colors.warning`, background `semantic.warning_bg`
- **Error**: left border `colors.negative`, background `semantic.error_bg`

## Page Layout (PDF, DOCX)

- Page size: `layout.page_size` (letter = 8.5x11in, a4 = 210x297mm)
- Margins: `layout.margin_top`, `margin_bottom`, `margin_left`, `margin_right` (in points, 72pt = 1 inch)
- Header: logo (if not suppressed) left-aligned, firm name right-aligned, `components.header_height`
- Footer: `content.confidentiality_notice` left-aligned, page number right-aligned, `components.footer_height`
- Confidentiality: `font_size_caption`, `semantic.muted_color`

## Slide Layout (PPTX)

- Title slide: logo centered, firm name below, title large (`font_size_h1`), subtitle below, date at bottom
- Section divider: `colors.primary` background, `colors.white` text, centered
- Content slide: title bar at top (`colors.primary` bg), body below
- Footer on all slides: firm name, confidentiality notice, slide number
- Vary layouts: two-column, icon-row, grid, KPI cards — never consecutive same-layout slides
