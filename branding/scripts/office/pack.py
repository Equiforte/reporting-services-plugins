#!/usr/bin/env python3
"""Repack an extracted Office XML directory into a ZIP-based Office file (.docx, .xlsx, .pptx).

Usage:
    python pack.py <extracted_dir> <output_file>

The extracted directory should contain the standard Office XML structure
([Content_Types].xml, _rels/, word/|xl/|ppt/, etc.) as produced by unpack.py.
"""

import os
import sys
import zipfile


def pack(extracted_dir, output_file):
    """Repack an extracted directory into an Office ZIP file.

    Args:
        extracted_dir: Path to the directory containing extracted Office XML.
        output_file: Path for the output Office file.

    Returns:
        dict with 'success' and 'error' keys.
    """
    if not os.path.isdir(extracted_dir):
        return {"success": False, "error": f"Directory not found: {extracted_dir}"}

    try:
        with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _dirs, files in os.walk(extracted_dir):
                for filename in sorted(files):
                    filepath = os.path.join(root, filename)
                    arcname = os.path.relpath(filepath, extracted_dir)
                    zf.write(filepath, arcname)

        return {"success": True, "error": None}
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    result = pack(sys.argv[1], sys.argv[2])

    import json
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)
