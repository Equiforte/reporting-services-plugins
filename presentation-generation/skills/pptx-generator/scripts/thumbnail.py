#!/usr/bin/env python3
"""Generate a thumbnail grid of slides from a PPTX file.

Converts each slide to an image and creates a contact sheet for visual QA.

Usage:
    python thumbnail.py <input.pptx> [--output <output.png>] [--cols 3] [--width 300]

Requires: LibreOffice (for PPTX to image conversion) or python-pptx + Pillow.
"""

import os
import sys
import subprocess
import shutil
import tempfile


def generate_thumbnails(pptx_path, output_path=None, cols=3, thumb_width=300):
    """Generate a thumbnail grid from a PPTX file.

    Args:
        pptx_path: Path to the PPTX file.
        output_path: Path for the output grid image (default: {input}_thumbnails.png).
        cols: Number of columns in the grid.
        thumb_width: Width of each thumbnail in pixels.

    Returns:
        dict with 'success', 'output_path', 'slide_count', and 'error'.
    """
    if not os.path.isfile(pptx_path):
        return {"success": False, "output_path": None, "slide_count": 0, "error": f"File not found: {pptx_path}"}

    if output_path is None:
        base = os.path.splitext(pptx_path)[0]
        output_path = f"{base}_thumbnails.png"

    # Try LibreOffice conversion first
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        # Check macOS path
        mac_path = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
        if os.path.isfile(mac_path):
            soffice = mac_path

    if not soffice:
        return {"success": False, "output_path": None, "slide_count": 0, "error": "LibreOffice not found. Required for thumbnail generation."}

    with tempfile.TemporaryDirectory() as tmpdir:
        # Convert PPTX to images
        cmd = [soffice, "--headless", "--convert-to", "png", "--outdir", tmpdir, pptx_path]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        except subprocess.TimeoutExpired:
            return {"success": False, "output_path": None, "slide_count": 0, "error": "Conversion timed out"}

        # Find generated images
        images = sorted([
            os.path.join(tmpdir, f) for f in os.listdir(tmpdir)
            if f.lower().endswith(".png")
        ])

        if not images:
            return {"success": False, "output_path": None, "slide_count": 0, "error": "No images generated from conversion"}

        # Try to create grid with Pillow
        try:
            from PIL import Image

            thumbs = []
            for img_path in images:
                img = Image.open(img_path)
                ratio = thumb_width / img.width
                thumb_height = int(img.height * ratio)
                thumb = img.resize((thumb_width, thumb_height), Image.LANCZOS)
                thumbs.append(thumb)

            if not thumbs:
                return {"success": False, "output_path": None, "slide_count": 0, "error": "No thumbnails created"}

            rows = (len(thumbs) + cols - 1) // cols
            thumb_h = thumbs[0].height
            padding = 10

            grid_w = cols * thumb_width + (cols + 1) * padding
            grid_h = rows * thumb_h + (rows + 1) * padding

            grid = Image.new("RGB", (grid_w, grid_h), "white")

            for i, thumb in enumerate(thumbs):
                row = i // cols
                col = i % cols
                x = padding + col * (thumb_width + padding)
                y = padding + row * (thumb_h + padding)
                grid.paste(thumb, (x, y))

            grid.save(output_path)

            return {"success": True, "output_path": output_path, "slide_count": len(thumbs), "error": None}

        except ImportError:
            # Pillow not available — just report the individual images
            return {
                "success": True,
                "output_path": tmpdir,
                "slide_count": len(images),
                "error": "Pillow not installed — individual slide images in temp dir. Install with: pip install Pillow",
            }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    pptx_path = sys.argv[1]
    output_path = None
    cols = 3
    thumb_width = 300

    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--output":
            output_path = args[i + 1]
            i += 2
        elif args[i] == "--cols":
            cols = int(args[i + 1])
            i += 2
        elif args[i] == "--width":
            thumb_width = int(args[i + 1])
            i += 2
        else:
            i += 1

    result = generate_thumbnails(pptx_path, output_path, cols, thumb_width)

    import json
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)
