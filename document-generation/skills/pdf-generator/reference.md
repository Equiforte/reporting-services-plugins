# PDF Advanced Operations Reference

## pypdf — Page manipulation

### Merge PDFs

```python
from pypdf import PdfWriter

writer = PdfWriter()
for pdf_path in input_files:
    writer.append(pdf_path)
writer.write(output_path)
```

### Split PDF

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader(input_path)
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    writer.write(f"page_{i+1}.pdf")
```

### Rotate pages

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader(input_path)
writer = PdfWriter()
for page in reader.pages:
    page.rotate(90)  # 90, 180, 270
    writer.add_page(page)
writer.write(output_path)
```

### Add watermark

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader(input_path)
watermark_reader = PdfReader(watermark_path)
watermark_page = watermark_reader.pages[0]

writer = PdfWriter()
for page in reader.pages:
    page.merge_page(watermark_page)
    writer.add_page(page)
writer.write(output_path)
```

## pdfplumber — Text and table extraction

### Extract text (preserving layout)

```python
import pdfplumber

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        # text preserves approximate layout
```

### Extract tables

```python
import pdfplumber

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            # table is a list of lists (rows x columns)
            for row in table:
                print(row)
```

### Extract with settings

```python
# Fine-tune table detection
table_settings = {
    "vertical_strategy": "lines",
    "horizontal_strategy": "lines",
    "snap_tolerance": 3,
}
tables = page.extract_tables(table_settings)
```

## pypdfium2 — PDF to image conversion

### Convert pages to PNG

```python
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument(pdf_path)
for i, page in enumerate(pdf):
    image = page.render(scale=2)  # 2x for high resolution
    pil_image = image.to_pil()
    pil_image.save(f"page_{i+1}.png")
```

### Convert specific page

```python
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument(pdf_path)
page = pdf[0]  # first page
image = page.render(scale=3)  # 3x for very high resolution
pil_image = image.to_pil()
pil_image.save("preview.png")
```

## Performance notes

- **pypdf** is fastest for page-level operations (merge, split, rotate).
- **pdfplumber** is best for structured extraction but slower than command-line tools for bulk text.
- **pypdfium2** is the fastest Python renderer for page-to-image conversion.
- For bulk text extraction (hundreds of pages), consider command-line `pdftotext` (from poppler) instead of pdfplumber.
