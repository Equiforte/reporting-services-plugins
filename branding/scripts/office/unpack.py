#!/usr/bin/env python3
"""Extract an Office ZIP file (.docx, .xlsx, .pptx) into a directory for XML editing.

Usage:
    python unpack.py <office_file> <output_dir>

Extracts the ZIP contents preserving the Office XML structure.
After editing XML files, use pack.py to reassemble.
"""

import os
import sys
import zipfile


def unpack(office_file, output_dir):
    """Extract an Office file into a directory.

    Args:
        office_file: Path to the Office file (.docx, .xlsx, .pptx).
        output_dir: Directory to extract into (created if needed).

    Returns:
        dict with 'success', 'files' (list of extracted paths), and 'error' keys.
    """
    if not os.path.isfile(office_file):
        return {"success": False, "files": [], "error": f"File not found: {office_file}"}

    try:
        os.makedirs(output_dir, exist_ok=True)

        with zipfile.ZipFile(office_file, "r") as zf:
            # Security: check for path traversal
            for member in zf.namelist():
                target = os.path.realpath(os.path.join(output_dir, member))
                if not target.startswith(os.path.realpath(output_dir)):
                    return {"success": False, "files": [], "error": f"Path traversal detected: {member}"}

            zf.extractall(output_dir)
            return {"success": True, "files": zf.namelist(), "error": None}
    except zipfile.BadZipFile:
        return {"success": False, "files": [], "error": f"Not a valid ZIP/Office file: {office_file}"}
    except Exception as e:
        return {"success": False, "files": [], "error": str(e)}


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    result = unpack(sys.argv[1], sys.argv[2])

    import json
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)
