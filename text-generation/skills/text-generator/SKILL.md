---
name: text-generator
description: >
  Generates branded text-based output files. Triggered when the user asks to
  "create a Markdown report", "generate an HTML page", "export as HTML",
  "write a summary", "create a text file", "generate a one-pager",
  "export as Markdown", or requests any Markdown, HTML, or plain-text output.
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - Edit
---

# Text Generator

Generate branded Markdown, HTML, and plain-text output files.

## Before generating

### Branding guard

Before generating output, check that `{WORKING_DIR}/.reporting-resolved/brand-config.json` exists. If it does not, tell the user: "The branding plugin is required but has not run. Please install the `branding` plugin and run `/reporting-plugins:brand` first." Do not produce unbranded output.

### Data source priority

If a JSON data file was generated earlier in this session (in `output/text/`), read it as the canonical data source to ensure cross-format parity. If no prior JSON exists, use data from the conversation context directly.

### Read brand config

Read `.reporting-resolved/brand-config.json` for all brand values. Use the design-system references for component patterns and language guidelines.

## Output conventions

- **Directory**: `output/text/`
- **File naming**: `{slug}-{YYYY-MM-DD}-{HHmm}-{xxx}.{ext}`
- **Slug rules**: kebab-case, alphanumeric and hyphens only. Strip or replace slashes, spaces, special characters, and non-ASCII.
- **Provenance**: include `meta.sources` where format supports it.

## Format: Markdown

File extension: `.md`

### Structure

Every Markdown file must begin with YAML frontmatter:

```yaml
---
title: "Report Title"
date: "April 4, 2026"
confidential: true
author: "Acme Inc"
sources:
  - "source-name"
---
```

- Use the firm name from brand config for `author`.
- Use `content.date_format` for the date.
- Set `confidential: true` unless the user explicitly says otherwise.

### Formatting rules

- Use GFM (GitHub Flavored Markdown) tables for tabular data.
- Use fenced code blocks with language hints for any code.
- Use `##` for section headings, `###` for subsections.
- Right-align numeric columns in tables using GFM alignment syntax (`:---:`, `---:`).
- Format numbers using `number_formats.*` tokens (e.g., `$12.4M`, `8.2%`).
- Include the confidentiality notice from `content.confidentiality_notice` at the top of the document, below the frontmatter, as an italic line.
- Include source citations at the end of the document.

## Format: HTML

File extension: `.html`

### Self-containment rules

The HTML file must be completely self-contained — a single `.html` file that opens in any browser without a server:

- **All CSS inline** in a `<style>` block in `<head>`. No external stylesheets.
- **No external resources** — no CDN links, no Google Fonts, no external images.
- **Logo as base64 data URI** — read the logo from `.reporting-resolved/logo.png`, convert to base64, embed as `<img src="data:image/png;base64,...">`. If logo was suppressed (no file exists), omit the logo element.
- **No `<script>` tags** — HTML output is static, no JavaScript.
- **Responsive layout** — use CSS that works on desktop and mobile.

### Branding in CSS

Map brand tokens to CSS:

```css
:root {
  --primary: {colors.primary};
  --accent: {colors.accent};
  --text: {colors.text};
  --text-secondary: {colors.text_secondary};
  --surface: {colors.surface};
  --heading: {semantic.heading_color};
  --border: {semantic.border_color};
}
```

- Headings: `color: var(--heading)`, `font-family: {typography.font_family_heading}`
- Body text: `color: var(--text)`, `font-family: {typography.font_family}`
- Tables: header row `background: var(--primary)`, `color: white`; alternating rows with `var(--surface)`
- Callout boxes: `border-left: {components.callout_border_width} solid var(--accent)`, `background: var(--surface)`

### Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{document title} — {firm.name}</title>
  <style>/* all CSS here */</style>
</head>
<body>
  <header><!-- logo (base64) + firm name --></header>
  <main><!-- content --></main>
  <footer><!-- confidentiality notice + date --></footer>
</body>
</html>
```

## Format: Plain text (TXT)

File extension: `.txt`

### Formatting rules

- Use fixed-width tables with spaces and dashes for alignment.
- Use `=====` or `-----` for section separators.
- Use UPPERCASE for section headings.
- Right-align numbers in table columns.
- Include confidentiality notice as the first line.
- Include firm name and date in the header area.
- Wrap lines at 80 characters.
- No special characters — ASCII only.
