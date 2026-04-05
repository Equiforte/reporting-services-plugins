# Office XML Schemas

This directory contains Microsoft Office XSD schema definitions for validation.

## Required schemas (ISO-IEC 29500 / ECMA-376)

Download from the ECMA International website or extract from an Office installation:

- `wml.xsd` — WordprocessingML (DOCX)
- `sml.xsd` — SpreadsheetML (XLSX)
- `pml.xsd` — PresentationML (PPTX)
- `dml-main.xsd` — DrawingML
- `shared-commonSimpleTypes.xsd` — Common types
- `opc-relationships.xsd` — OPC relationships
- `vml-main.xsd` — VML (legacy shapes)

## Usage

These schemas are used by `validate.py --check-schema` to verify that
generated Office files conform to the Office Open XML specification.
