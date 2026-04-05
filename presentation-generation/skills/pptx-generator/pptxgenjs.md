# PptxGenJS API Reference

Quick reference for the PptxGenJS library used for slide deck creation.

## Installation

```bash
npm install pptxgenjs
```

## Core API

### Create presentation

```javascript
const pptxgen = require("pptxgenjs");
const pres = new pptxgen();

// Set defaults
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 inches (default)
pres.author = "Acme Inc";
pres.title = "Presentation Title";
```

### Add slides

```javascript
const slide = pres.addSlide();
// Optional: specify master slide
const slide2 = pres.addSlide({ masterName: "TITLE_SLIDE" });
```

### Save

```javascript
// To file
pres.writeFile({ fileName: "output.pptx" });

// To buffer (Node.js)
const buffer = await pres.write({ outputType: "nodebuffer" });
```

## Adding content

### Text

```javascript
slide.addText("Hello World", {
  x: 1, y: 1, w: 5, h: 1,       // position and size in inches
  fontSize: 24,                    // in points
  fontFace: "Calibri",
  color: "1B3A5C",                // NO '#' prefix
  bold: true,
  italic: false,
  underline: false,
  align: "left",                  // left, center, right
  valign: "top",                  // top, middle, bottom
  wrap: true,
});
```

### Rich text (multiple formats in one text box)

```javascript
slide.addText([
  { text: "Bold text ", options: { bold: true, fontSize: 14 } },
  { text: "and normal text", options: { fontSize: 14 } },
], { x: 1, y: 1, w: 8, h: 0.5 });
```

### Images

```javascript
slide.addImage({
  path: "logo.png",              // file path
  x: 1, y: 1, w: 3, h: 1,
});

// From base64
slide.addImage({
  data: "data:image/png;base64,...",
  x: 1, y: 1, w: 3, h: 1,
});
```

### Shapes

```javascript
const pptxgen = require("pptxgenjs");

slide.addShape(pptxgen.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.8,
  fill: { color: "1B3A5C" },
});

slide.addShape(pptxgen.shapes.ROUNDED_RECTANGLE, {
  x: 1, y: 2, w: 3, h: 1.5,
  fill: { color: "F7F8FA" },
  rectRadius: 0.1,               // corner radius in inches
});

// Line
slide.addShape(pptxgen.shapes.LINE, {
  x: 0.5, y: 3, w: 9, h: 0,
  line: { color: "D1D5DB", width: 1 },
});
```

### Tables

```javascript
const rows = [
  [
    { text: "Header 1", options: { bold: true, color: "FFFFFF", fill: { color: "1B3A5C" } } },
    { text: "Header 2", options: { bold: true, color: "FFFFFF", fill: { color: "1B3A5C" } } },
  ],
  ["Row 1 Col 1", "Row 1 Col 2"],
  ["Row 2 Col 1", "Row 2 Col 2"],
];

slide.addTable(rows, {
  x: 0.5, y: 1.5, w: 9,
  colW: [4.5, 4.5],
  border: { type: "solid", pt: 0.5, color: "D1D5DB" },
  rowH: 0.4,
  fontSize: 10,
  autoPage: true,
});
```

### Charts

```javascript
const chartData = [
  { name: "Revenue", labels: ["Q1", "Q2", "Q3", "Q4"], values: [12.4, 13.1, 14.2, 15.0] },
];

slide.addChart(pres.charts.BAR, chartData, {
  x: 0.5, y: 1.5, w: 9, h: 4,
  showTitle: true,
  title: "Quarterly Revenue ($M)",
  titleColor: "1B3A5C",
  chartColors: ["1B3A5C", "2E75B6", "1A7A3A", "C67700"],  // from semantic.chart_series
  showValue: true,
  valueFontSize: 8,
});
```

Available chart types: `BAR`, `BAR3D`, `LINE`, `AREA`, `PIE`, `DOUGHNUT`, `SCATTER`, `BUBBLE`.

## Slide background

```javascript
// Solid color
slide.background = { color: "FFFFFF" };

// Image
slide.background = { path: "bg.png" };

// Gradient
slide.background = {
  fill: {
    type: "gradient",
    stops: [
      { position: 0, color: "1B3A5C" },
      { position: 100, color: "2E75B6" },
    ],
  },
};
```

## Slide numbers

```javascript
pres.slideNumber = {
  x: 9.0, y: 7.0, w: 0.5, h: 0.3,
  fontSize: 8, color: "999999",
};
```

## Measurements

All positions and sizes are in **inches**:
- Standard wide slide: 13.33" x 7.5"
- Usable area (with margins): ~0.5" from each edge
- Common text heights: title 1.0", body line 0.4", caption 0.3"
