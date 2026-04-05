# PPTX Template Editing Workflow

For modifying existing PPTX files at the XML level. Use this when python-pptx or PptxGenJS can't make the needed changes.

## Workflow: unpack → edit → clean → repack

### Step 1: Unpack

```bash
# Read office scripts path from resolved brand config
OFFICE_SCRIPTS=$(python3 -c "import json; print(json.load(open('.reporting-resolved/brand-config.json'))['_office_scripts_path'])")

python "$OFFICE_SCRIPTS"/unpack.py template.pptx extracted/
```

This extracts the PPTX ZIP into a directory:
```
extracted/
├── [Content_Types].xml
├── _rels/
│   └── .rels
├── ppt/
│   ├── presentation.xml
│   ├── slides/
│   │   ├── slide1.xml
│   │   ├── slide2.xml
│   │   └── ...
│   ├── slideMasters/
│   ├── slideLayouts/
│   ├── theme/
│   └── media/
│       ├── image1.png
│       └── ...
└── docProps/
```

### Step 2: Edit XML

Edit slide XML files directly. Common operations:

**Change text content**:
```xml
<!-- In ppt/slides/slide1.xml -->
<a:t>Original Text</a:t>
<!-- Change to: -->
<a:t>New Text</a:t>
```

**Bold all headers**:
Add `<a:rPr b="1"/>` to run properties:
```xml
<a:r>
  <a:rPr b="1" lang="en-US"/>
  <a:t>Header Text</a:t>
</a:r>
```

**Change colors**:
```xml
<!-- Solid fill color -->
<a:solidFill>
  <a:srgbClr val="1B3A5C"/>
</a:solidFill>
```

**Replace images**:
Replace files in `ppt/media/` with new images of the same dimensions.

### Step 3: Clean

Remove orphaned files and invalid references:

```bash
python {PLUGIN_ROOT}/skills/pptx-generator/scripts/clean.py extracted/
```

### Step 4: Validate

```bash
python "$OFFICE_SCRIPTS"/validate.py extracted/ --strip-xxe
```

### Step 5: Repack

```bash
python "$OFFICE_SCRIPTS"/pack.py extracted/ output.pptx
```

## Duplicate slides

To add slides based on existing layouts:

```bash
python {PLUGIN_ROOT}/skills/pptx-generator/scripts/add_slide.py template.pptx --from-slide 2 --output output.pptx
```

## Common gotchas

- **Smart quotes in XML**: Use `&#x201C;` and `&#x201D;` for double quotes, `&#x2018;` and `&#x2019;` for single quotes.
- **Never use Unicode bullets** (`•`): Use PowerPoint's built-in bullet formatting via XML `<a:buChar char="&#8226;"/>`.
- **Namespace prefixes**: PPTX XML uses namespaces extensively. Ensure `a:` (DrawingML), `r:` (relationships), `p:` (PresentationML) prefixes are correct.
- **Relationship IDs**: When adding images or links, ensure the relationship ID (`rId`) in the slide XML matches an entry in `ppt/slides/_rels/slideN.xml.rels`.
