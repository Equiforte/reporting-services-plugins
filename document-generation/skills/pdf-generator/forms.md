# PDF Form Filling Workflow

Two approaches for filling PDF forms, depending on the form type.

## Approach A: Fillable fields (preferred)

Use when the PDF has native form fields (AcroForm or XFA).

### Step 1: Detect form type

```python
from pypdf import PdfReader

reader = PdfReader(pdf_path)
fields = reader.get_fields()

if fields:
    print(f"Found {len(fields)} fillable fields")
    for name, field in fields.items():
        print(f"  {name}: type={field.get('/FT')}, value={field.get('/V')}")
else:
    print("No fillable fields — use Approach B")
```

### Step 2: Fill fields

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader(pdf_path)
writer = PdfWriter()
writer.append(reader)

writer.update_page_form_field_values(
    writer.pages[0],
    {
        "field_name_1": "value_1",
        "field_name_2": "value_2",
    }
)

writer.write(output_path)
```

### Step 3: Flatten (optional)

To make filled fields non-editable:

```python
for page in writer.pages:
    for annot in page.get("/Annots", []):
        annot.get_object().update({"/Ff": 1})  # Read-only flag
```

## Approach B: Annotation-based (fallback)

Use when the PDF has visual form areas but no native fields (e.g., scanned forms, designed layouts).

### Step 1: Convert to image for coordinate mapping

```python
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument(pdf_path)
page = pdf[0]
image = page.render(scale=2)
pil_image = image.to_pil()
pil_image.save("form_preview.png")
```

### Step 2: Identify coordinates

Read the preview image to identify where text should be placed. Note coordinates in PDF points (1 point = 1/72 inch). The PDF coordinate system has origin at bottom-left.

### Step 3: Add text annotations

```python
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from pypdf import PdfReader, PdfWriter

# Create overlay with text
c = canvas.Canvas("overlay.pdf", pagesize=letter)
c.setFont("Helvetica", 10)
c.drawString(x_pt, y_pt, "Field value")
c.save()

# Merge overlay onto original
original = PdfReader(pdf_path)
overlay = PdfReader("overlay.pdf")

writer = PdfWriter()
for i, page in enumerate(original.pages):
    if i < len(overlay.pages):
        page.merge_page(overlay.pages[i])
    writer.add_page(page)

writer.write(output_path)
```

### Step 4: Validate

Convert the filled PDF to an image and visually verify text placement:

```python
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument(output_path)
page = pdf[0]
image = page.render(scale=2)
pil_image = image.to_pil()
pil_image.save("filled_preview.png")
```

Compare with the original preview to verify alignment.

## Coordinate tips

- PDF coordinates: origin at **bottom-left**, Y increases upward.
- Image coordinates: origin at **top-left**, Y increases downward.
- To convert image Y to PDF Y: `pdf_y = page_height - (image_y / scale)`
- Always validate bounding boxes before filling — off-by-one errors are common.
- Use `pdfplumber` to extract text positions from existing forms as coordinate references.
