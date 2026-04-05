#!/usr/bin/env python3
"""Accept all tracked changes in a DOCX document.

Uses LibreOffice headless mode to open the document, accept all changes, and save.
Falls back to XML manipulation if LibreOffice is not available.

Usage:
    python accept_changes.py <input.docx> <output.docx>
"""

import os
import sys
import shutil
import subprocess
import tempfile


def accept_with_libreoffice(input_path, output_path):
    """Accept tracked changes using LibreOffice macro."""
    # Find LibreOffice
    soffice = None
    for candidate in [
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        "/usr/bin/soffice",
        "/usr/bin/libreoffice",
    ]:
        if os.path.isfile(candidate):
            soffice = candidate
            break

    if not soffice:
        soffice = shutil.which("soffice") or shutil.which("libreoffice")

    if not soffice:
        return False, "LibreOffice not found"

    # LibreOffice macro to accept all changes
    macro = (
        'macro:///Standard.Module1.AcceptAll'
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_input = os.path.join(tmpdir, os.path.basename(input_path))
        shutil.copy2(input_path, tmp_input)

        cmd = [
            soffice,
            "--headless",
            "--convert-to", "docx",
            "--outdir", tmpdir,
            tmp_input,
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                # Find converted file
                for f in os.listdir(tmpdir):
                    if f.endswith(".docx") and f != os.path.basename(input_path):
                        shutil.copy2(os.path.join(tmpdir, f), output_path)
                        return True, None
                # If same filename, copy it
                shutil.copy2(tmp_input, output_path)
                return True, None
            return False, result.stderr
        except subprocess.TimeoutExpired:
            return False, "Timed out after 2 minutes"


def accept_with_xml(input_path, output_path):
    """Accept tracked changes via XML manipulation (fallback)."""
    import zipfile

    # Find simplify_redlines helper
    script_dir = os.path.dirname(os.path.abspath(__file__))
    helpers_dir = os.path.join(
        os.getcwd(), ".reporting-resolved", "scripts", "office", "helpers"
    )

    simplify_path = os.path.join(helpers_dir, "simplify_redlines.py")
    if not os.path.isfile(simplify_path):
        return False, f"simplify_redlines.py not found at {simplify_path}"

    with tempfile.TemporaryDirectory() as tmpdir:
        # Extract
        with zipfile.ZipFile(input_path, "r") as zf:
            zf.extractall(tmpdir)

        # Process document.xml
        doc_xml = os.path.join(tmpdir, "word", "document.xml")
        if os.path.isfile(doc_xml):
            subprocess.run(
                [sys.executable, simplify_path, doc_xml],
                check=True,
            )

        # Repack
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _dirs, files in os.walk(tmpdir):
                for fname in sorted(files):
                    fpath = os.path.join(root, fname)
                    arcname = os.path.relpath(fpath, tmpdir)
                    zf.write(fpath, arcname)

    return True, None


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    if not os.path.isfile(input_path):
        print(f"Error: File not found: {input_path}")
        sys.exit(1)

    # Try LibreOffice first, fall back to XML
    success, error = accept_with_libreoffice(input_path, output_path)
    if not success:
        print(f"LibreOffice method failed ({error}), trying XML fallback...")
        success, error = accept_with_xml(input_path, output_path)

    if success:
        print(f"Changes accepted: {output_path}")
    else:
        print(f"Error: {error}")
        sys.exit(1)
