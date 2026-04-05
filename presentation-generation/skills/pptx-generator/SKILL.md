---
name: pptx-generator
description: >
  Generates branded PowerPoint slide decks. Triggered when the user asks to
  "create a deck", "build a presentation", "make slides", "generate a PPTX",
  "board deck", "pitch deck", "quarterly review deck", "slide presentation",
  "executive presentation", or references PPTX/PowerPoint output.
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - Edit
---

# PPTX Generator

Generate branded slide decks using PptxGenJS (Node.js) for creation and python-pptx for reading/editing. Every deck must have visual variety — no text-only slides, no consecutive same-layout slides.

## Before generating

### Branding guard

Before generating output, check that `{WORKING_DIR}/.reporting-resolved/brand-config.json` exists. If it does not, tell the user: "The branding plugin is required but has not run. Please install the `branding` plugin and run `/reporting-plugins:brand` first." Do not produce unbranded output.

### Data source priority

If a JSON data file was generated earlier in this session (in `output/text/`), read it as the canonical data source to ensure cross-format parity. If no prior JSON exists, use data from the conversation context directly.

### Read brand config

Read `.reporting-resolved/brand-config.json` for all brand values. Read logo from `.reporting-resolved/logo.png` (if it exists).

### Install dependencies

```bash
npm install pptxgenjs    # Creation
pip install python-pptx  # Reading/editing
```

## Output conventions

- **Directory**: `output/pptx/`
- **File naming**: `{slug}-{YYYY-MM-DD}-{HHmm}-{xxx}.pptx`
- **Slug rules**: kebab-case, alphanumeric and hyphens only.

## Creating decks with PptxGenJS

### Setup

```javascript
const pptxgen = require("pptxgenjs");
const pres = new pptxgen();

// Brand colors (NO '#' prefix — PptxGenJS uses bare hex)
const PRIMARY = brand.colors.primary.replace("#", "");
const ACCENT = brand.colors.accent.replace("#", "");
const WHITE = "FFFFFF";
const TEXT = brand.colors.text.replace("#", "");
```

### Critical constraints

1. **No `#` prefix on hex colors.** PptxGenJS uses bare hex strings: `"1B3A5C"` not `"#1B3A5C"`.

2. **Never reuse option objects.** PptxGenJS mutates options in-place. Always create fresh objects:
   ```javascript
   // WRONG
   const opts = { x: 0.5, y: 0.5, w: 9, h: 0.5, color: PRIMARY };
   slide1.addText("Title 1", opts);
   slide2.addText("Title 2", opts); // opts was mutated!

   // RIGHT
   slide1.addText("Title 1", { x: 0.5, y: 0.5, w: 9, h: 0.5, color: PRIMARY });
   slide2.addText("Title 2", { x: 0.5, y: 0.5, w: 9, h: 0.5, color: PRIMARY });
   ```

3. **Rounded rectangles**: Use `pptxgen.shapes.ROUNDED_RECTANGLE`, not `RECTANGLE` with `rectRadius`.

## Slide layout patterns

Every deck must use at least 3 different layouts. Never use the same layout for consecutive slides.

### Title slide

```javascript
const slide = pres.addSlide();
slide.background = { color: WHITE };

// Logo (if not suppressed)
if (logoPath) {
  slide.addImage({ path: logoPath, x: 3.5, y: 1.0, h: 0.6 });
}

// Firm name
slide.addText(brand.firm.name, {
  x: 0.5, y: 2.0, w: 9, h: 0.5,
  fontSize: 14, color: ACCENT, align: "center",
});

// Title
slide.addText(title, {
  x: 0.5, y: 2.8, w: 9, h: 1.0,
  fontSize: 36, color: PRIMARY, bold: true, align: "center",
  fontFace: brand.typography.font_family_heading.split(",")[0].trim(),
});

// Date
slide.addText(date, {
  x: 0.5, y: 4.5, w: 9, h: 0.4,
  fontSize: 12, color: TEXT, align: "center",
});
```

### Section divider

Primary color background, white text, centered:

```javascript
const slide = pres.addSlide();
slide.background = { color: PRIMARY };
slide.addText(sectionTitle, {
  x: 0.5, y: 2.5, w: 9, h: 1.5,
  fontSize: 32, color: WHITE, bold: true, align: "center",
});
```

### Content slide with title bar

```javascript
const slide = pres.addSlide();

// Title bar
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.8, fill: { color: PRIMARY },
});
slide.addText(slideTitle, {
  x: 0.5, y: 0.1, w: 9, h: 0.6,
  fontSize: 20, color: WHITE, bold: true,
});

// Body content below title bar
// ... add text, tables, charts, shapes
```

### KPI dashboard (3-4 cards per row)

```javascript
const kpis = [
  { label: "Revenue", value: "$12.4M", delta: "+8.2%" },
  // ...
];

const cardWidth = 2.1;
const cardHeight = 1.2;
const startX = 0.5;
const startY = 1.2;

kpis.forEach((kpi, i) => {
  const x = startX + (i % 4) * (cardWidth + 0.2);
  const y = startY + Math.floor(i / 4) * (cardHeight + 0.2);

  // Card background
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w: cardWidth, h: cardHeight,
    fill: { color: "F7F8FA" },
    rectRadius: 0.1,
  });

  // Value
  slide.addText(kpi.value, {
    x, y: y + 0.15, w: cardWidth, h: 0.5,
    fontSize: 24, bold: true, color: PRIMARY, align: "center",
  });

  // Label
  slide.addText(kpi.label, {
    x, y: y + 0.65, w: cardWidth, h: 0.3,
    fontSize: 10, color: "666666", align: "center",
  });
});
```

### Table slide

```javascript
slide.addTable(rows, {
  x: 0.5, y: 1.2, w: 9,
  colW: [3, 2, 2, 2],
  border: { type: "solid", pt: 0.5, color: "D1D5DB" },
  rowH: 0.4,
  autoPage: true,
  headerRow: true,
  headerRowColor: PRIMARY,
  headerFontColor: WHITE,
  altRowColor: "F7F8FA",
});
```

### Two-column layout

Split slide into two equal columns for side-by-side content (text + image, two lists, etc.).

### Chart slide

Use PptxGenJS chart capabilities with `semantic.chart_series` colors.

## Footer on all slides

Add to every slide (except title slide):

```javascript
// Confidentiality + slide number
slide.addText(brand.content.confidentiality_notice, {
  x: 0.5, y: 7.0, w: 7, h: 0.3,
  fontSize: 7, color: "999999",
});
slide.addText(`${slideNumber}`, {
  x: 8.5, y: 7.0, w: 1, h: 0.3,
  fontSize: 7, color: "999999", align: "right",
});
```

## Timeline content

Timeline visuals within a slide deck (e.g., "market expansion timeline" as part of a board deck) are handled by THIS skill. Only route to `jsx-generator` when the user wants a standalone interactive timeline app.

## Editing existing decks

For template-based editing (unpack XML, modify, repack), see `editing.md`.

## QA process

After generating, convert the first few slides to images for visual inspection:

```bash
# Read office scripts path from resolved brand config
OFFICE_SCRIPTS=$(python3 -c "import json; print(json.load(open('.reporting-resolved/brand-config.json'))['_office_scripts_path'])")

python "$OFFICE_SCRIPTS/soffice.py" convert output.pptx png
```

Or use the thumbnail script:

```bash
python {PLUGIN_ROOT}/skills/pptx-generator/scripts/thumbnail.py output.pptx
```

Run at least one QA cycle: generate → thumbnail → inspect → fix any issues.
