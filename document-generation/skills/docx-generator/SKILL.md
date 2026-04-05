---
name: docx-generator
description: >
  Generates branded Word documents (DOCX). Triggered when the user asks to
  "create a Word document", "generate a DOCX", "write a memo", "create a proposal",
  "DOCX report", "Word file", or references Word/DOCX output for reports,
  memos, proposals, letters, or formal documents.
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - Edit
---

# DOCX Generator

Generate branded Word documents using python-docx. Supports creating new documents, editing existing ones, tracked changes, comments, and table of contents.

## Before generating

### Branding guard

Before generating output, check that `{WORKING_DIR}/.reporting-resolved/brand-config.json` exists. If it does not, tell the user: "The branding plugin is required but has not run. Please install the `branding` plugin and run `/reporting-plugins:brand` first." Do not produce unbranded output.

### Data source priority

If a JSON data file was generated earlier in this session (in `output/text/`), read it as the canonical data source to ensure cross-format parity. If no prior JSON exists, use data from the conversation context directly.

### Read brand config

Read `.reporting-resolved/brand-config.json` for all brand values. Read the logo from `.reporting-resolved/logo.png` (if it exists).

### Install dependencies

```bash
pip install python-docx defusedxml
```

### Office utilities

Office XML utilities are in the branding plugin. Read `_office_scripts_path` from `.reporting-resolved/brand-config.json` to find them:
- `pack.py` / `unpack.py` — extract and repack DOCX XML for low-level editing
- `validate.py` — XSD schema validation + XXE stripping
- `helpers/merge_runs.py` — consolidate fragmented text runs
- `helpers/simplify_redlines.py` — accept all tracked changes

## Output conventions

- **Directory**: `output/docx/`
- **File naming**: `{slug}-{YYYY-MM-DD}-{HHmm}-{xxx}.docx`
- **Slug rules**: kebab-case, alphanumeric and hyphens only.

## Creating documents with python-docx

### Page setup

```python
from docx import Document
from docx.shared import Inches, Pt, Emu

doc = Document()
section = doc.sections[0]

# CRITICAL: Set page size explicitly — python-docx defaults to A4, not US Letter
section.page_width = Emu(12240 * 914)   # 8.5 inches in EMU
section.page_height = Emu(15840 * 914)  # 11 inches in EMU

# Or use DXA (twentieths of a point): 12240 x 15840 for US Letter
# Margins in EMU (1 inch = 914400 EMU, 72pt margin = 914400 EMU)
section.top_margin = Emu(brand["layout"]["margin_top"] * 12700)
section.bottom_margin = Emu(brand["layout"]["margin_bottom"] * 12700)
section.left_margin = Emu(brand["layout"]["margin_left"] * 12700)
section.right_margin = Emu(brand["layout"]["margin_right"] * 12700)
```

### Branded header and footer

**Header**: Add logo (left-aligned) and firm name (right-aligned) to the default header.

```python
from docx.shared import Inches

header = section.header
header_para = header.paragraphs[0]
# Add logo
if logo_exists:
    run = header_para.add_run()
    run.add_picture(".reporting-resolved/logo.png", height=Inches(0.4))
```

**Footer**: Add confidentiality notice (left) and page number (right).

### Styling

- Document title: `font_size_h1`, `semantic.heading_color`, `font_family_heading`, bold
- Section headings (Heading 1): `font_size_h2`, `semantic.heading_color`
- Body text (Normal): `font_size_body`, `colors.text`, `font_family`
- Captions: `font_size_caption`, `semantic.muted_color`
- Hyperlinks: `semantic.link_color`

## Critical constraints

### Never use `\n` for line breaks
Always use Paragraph elements. `\n` in a run creates invalid line breaks in some renderers.

```python
# WRONG
para.add_run("Line 1\nLine 2")

# RIGHT
doc.add_paragraph("Line 1")
doc.add_paragraph("Line 2")
```

### Never use Unicode bullets
Use proper list formatting with numbering definitions, not `•` or `–` characters.

```python
# WRONG
doc.add_paragraph("• Item 1")

# RIGHT
doc.add_paragraph("Item 1", style="List Bullet")
```

### Tables need dual width specification

Both `columnWidths` AND individual cell widths must be set, in DXA units (1 inch = 1440 DXA):

```python
from docx.shared import Inches
from docx.oxml.ns import qn

table = doc.add_table(rows=2, cols=3)
table.autofit = False

# Set table width
table.width = Inches(6.5)

# Set each cell width explicitly
for row in table.rows:
    for i, cell in enumerate(row.cells):
        cell.width = Inches(6.5 / 3)
```

### Tables: header row styling

```python
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn

# Brand-colored header row
for cell in table.rows[0].cells:
    shading = cell._element.get_or_add_tcPr()
    shading_elem = shading.get_or_add_shd()
    # components.table_header_bg without '#'
    shading_elem.set(qn("w:fill"), brand["components"]["table_header_bg"].lstrip("#"))
    for para in cell.paragraphs:
        for run in para.runs:
            run.font.color.rgb = RGBColor.from_string(
                brand["components"]["table_header_text"].lstrip("#")
            )
            run.font.bold = True
```

### Smart quotes in XML

When editing raw DOCX XML (via unpack/pack), use XML entities for smart quotes:
- `&#x2018;` (left single quote ')
- `&#x2019;` (right single quote ')
- `&#x201C;` (left double quote ")
- `&#x201D;` (right double quote ")

## Editing existing documents

### Unpack → edit XML → repack workflow

For changes that python-docx can't handle (complex formatting, custom XML):

```bash
# Read office scripts path from resolved brand config
OFFICE_SCRIPTS=$(python3 -c "import json; print(json.load(open('.reporting-resolved/brand-config.json'))['_office_scripts_path'])")

# Extract
python "$OFFICE_SCRIPTS"/unpack.py input.docx extracted/

# Edit XML files in extracted/word/document.xml
# ...

# Validate
python "$OFFICE_SCRIPTS"/validate.py extracted/word/document.xml --strip-xxe

# Repack
python "$OFFICE_SCRIPTS"/pack.py extracted/ output.docx
```

### Accept tracked changes

```bash
python {PLUGIN_ROOT}/skills/docx-generator/scripts/accept_changes.py input.docx output.docx
```

### Add comments

```bash
python {PLUGIN_ROOT}/skills/docx-generator/scripts/comment.py input.docx output.docx --comment "Review needed" --author "System"
```

## Validation

### Mode: best_effort
- Generate the DOCX. Warn on any issues (missing fonts, etc.) and continue.

### Mode: strict
- Validate the DOCX with `validate.py` after generation.
- Emit `{name}.validation.json` sidecar.
- If validation fails, attempt fix once. If it fails again, report to user.

## Website rendering rule

If `firm.name` was overridden but `firm.website` was NOT explicitly set, do not render `firm.website` in the document.
