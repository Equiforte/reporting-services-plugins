#!/usr/bin/env python3
"""Headless LibreOffice operations for document conversion and formula recalculation.

Usage:
    python soffice.py convert <input_file> <output_format> [--outdir <dir>]
    python soffice.py recalc <xlsx_file> [--outdir <dir>]

Supports macOS (Darwin) and Linux. Automatically locates the LibreOffice binary.
"""

import subprocess
import sys
import os
import platform
import shutil


def find_soffice():
    """Locate the LibreOffice binary."""
    if platform.system() == "Darwin":
        candidates = [
            "/Applications/LibreOffice.app/Contents/MacOS/soffice",
            os.path.expanduser("~/Applications/LibreOffice.app/Contents/MacOS/soffice"),
        ]
    else:
        candidates = [
            "/usr/bin/soffice",
            "/usr/bin/libreoffice",
            "/usr/local/bin/soffice",
        ]

    for path in candidates:
        if os.path.isfile(path):
            return path

    # Fallback: check PATH
    which = shutil.which("soffice") or shutil.which("libreoffice")
    if which:
        return which

    return None


def convert(input_file, output_format, outdir=None):
    """Convert a file using LibreOffice headless mode.

    Args:
        input_file: Path to input file (e.g., document.docx)
        output_format: Target format (e.g., pdf, png, html)
        outdir: Output directory (default: same as input)

    Returns:
        dict with 'success', 'output_path', and 'error' keys.
    """
    soffice = find_soffice()
    if not soffice:
        return {"success": False, "output_path": None, "error": "LibreOffice not found. Install with: brew install --cask libreoffice"}

    if outdir is None:
        outdir = os.path.dirname(os.path.abspath(input_file))

    cmd = [
        soffice,
        "--headless",
        "--convert-to", output_format,
        "--outdir", outdir,
        input_file,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            base = os.path.splitext(os.path.basename(input_file))[0]
            output_path = os.path.join(outdir, f"{base}.{output_format}")
            return {"success": True, "output_path": output_path, "error": None}
        else:
            return {"success": False, "output_path": None, "error": result.stderr.strip()}
    except subprocess.TimeoutExpired:
        return {"success": False, "output_path": None, "error": "LibreOffice conversion timed out after 5 minutes."}
    except Exception as e:
        return {"success": False, "output_path": None, "error": str(e)}


def recalc(xlsx_file, outdir=None):
    """Recalculate formulas in an XLSX file using LibreOffice.

    Opens the file, triggers recalculation, and saves. Returns error detection results.

    Args:
        xlsx_file: Path to XLSX file.
        outdir: Output directory for the recalculated file.

    Returns:
        dict with 'success', 'output_path', and 'error' keys.
    """
    soffice = find_soffice()
    if not soffice:
        return {"success": False, "output_path": None, "error": "LibreOffice not found. Install with: brew install --cask libreoffice"}

    if outdir is None:
        outdir = os.path.dirname(os.path.abspath(xlsx_file))

    # LibreOffice macro to recalculate and save
    cmd = [
        soffice,
        "--headless",
        "--calc",
        "--convert-to", "xlsx",
        "--outdir", outdir,
        xlsx_file,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            return {"success": True, "output_path": xlsx_file, "error": None}
        else:
            return {"success": False, "output_path": None, "error": result.stderr.strip()}
    except subprocess.TimeoutExpired:
        return {"success": False, "output_path": None, "error": "LibreOffice recalculation timed out after 5 minutes."}
    except Exception as e:
        return {"success": False, "output_path": None, "error": str(e)}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    action = sys.argv[1]
    input_file = sys.argv[2]

    outdir = None
    if "--outdir" in sys.argv:
        outdir = sys.argv[sys.argv.index("--outdir") + 1]

    if action == "convert":
        if len(sys.argv) < 4:
            print("Usage: python soffice.py convert <input_file> <output_format>")
            sys.exit(1)
        output_format = sys.argv[3]
        result = convert(input_file, output_format, outdir)
    elif action == "recalc":
        result = recalc(input_file, outdir)
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

    import json
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)
