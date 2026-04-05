#!/usr/bin/env python3
"""Add comments to a DOCX document.

Adds a comment to the document body or to a specific paragraph.

Usage:
    python comment.py <input.docx> <output.docx> --comment "Comment text" [--author "Name"] [--paragraph N]

Options:
    --comment    Comment text to add (required)
    --author     Comment author name (default: "System")
    --paragraph  0-based paragraph index to attach comment to (default: 0, first paragraph)
"""

import os
import sys
import zipfile
import tempfile
import re
from datetime import datetime


def add_comment(input_path, output_path, comment_text, author="System", paragraph_idx=0):
    """Add a comment to a DOCX file via XML manipulation.

    Args:
        input_path: Path to input DOCX.
        output_path: Path for output DOCX.
        comment_text: The comment text.
        author: Comment author name.
        paragraph_idx: 0-based index of the paragraph to attach the comment to.

    Returns:
        tuple of (success: bool, error: str or None)
    """
    if not os.path.isfile(input_path):
        return False, f"File not found: {input_path}"

    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    comment_id = "1"  # Simple — for multiple comments, increment

    # Smart quote handling for XML
    comment_text = comment_text.replace("'", "\u2019").replace('"', "\u201C")
    # Escape XML entities
    comment_text = (
        comment_text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        # Extract
        with zipfile.ZipFile(input_path, "r") as zf:
            zf.extractall(tmpdir)

        # Create or update comments.xml
        comments_path = os.path.join(tmpdir, "word", "comments.xml")
        comments_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:comments xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <w:comment w:id="{comment_id}" w:author="{author}" w:date="{now}">
    <w:p>
      <w:r>
        <w:t>{comment_text}</w:t>
      </w:r>
    </w:p>
  </w:comment>
</w:comments>"""

        with open(comments_path, "w", encoding="utf-8") as f:
            f.write(comments_xml)

        # Add comment reference to the target paragraph in document.xml
        doc_path = os.path.join(tmpdir, "word", "document.xml")
        if os.path.isfile(doc_path):
            with open(doc_path, "r", encoding="utf-8") as f:
                doc_content = f.read()

            # Find the Nth <w:p> element and wrap its content with comment markers
            paragraphs = list(re.finditer(r"<w:p[ >]", doc_content))
            if paragraph_idx < len(paragraphs):
                pos = paragraphs[paragraph_idx].start()
                # Find the end of this paragraph's opening tag content
                # Insert comment range start after <w:p...>
                p_end = doc_content.index(">", pos) + 1
                comment_start = f'<w:commentRangeStart w:id="{comment_id}"/>'
                comment_end_tag = f'<w:commentRangeEnd w:id="{comment_id}"/><w:r><w:rPr/><w:commentReference w:id="{comment_id}"/></w:r>'

                # Find </w:p> for this paragraph
                close_pos = doc_content.index("</w:p>", pos)

                doc_content = (
                    doc_content[:p_end]
                    + comment_start
                    + doc_content[p_end:close_pos]
                    + comment_end_tag
                    + doc_content[close_pos:]
                )

                with open(doc_path, "w", encoding="utf-8") as f:
                    f.write(doc_content)

        # Ensure comments.xml is referenced in [Content_Types].xml
        ct_path = os.path.join(tmpdir, "[Content_Types].xml")
        if os.path.isfile(ct_path):
            with open(ct_path, "r", encoding="utf-8") as f:
                ct_content = f.read()
            if "comments.xml" not in ct_content:
                ct_content = ct_content.replace(
                    "</Types>",
                    '  <Override PartName="/word/comments.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"/>\n</Types>',
                )
                with open(ct_path, "w", encoding="utf-8") as f:
                    f.write(ct_content)

        # Repack
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _dirs, files in os.walk(tmpdir):
                for fname in sorted(files):
                    fpath = os.path.join(root, fname)
                    arcname = os.path.relpath(fpath, tmpdir)
                    zf.write(fpath, arcname)

    return True, None


if __name__ == "__main__":
    if len(sys.argv) < 5 or "--comment" not in sys.argv:
        print(__doc__)
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    comment_text = sys.argv[sys.argv.index("--comment") + 1]
    author = "System"
    paragraph_idx = 0

    if "--author" in sys.argv:
        author = sys.argv[sys.argv.index("--author") + 1]
    if "--paragraph" in sys.argv:
        paragraph_idx = int(sys.argv[sys.argv.index("--paragraph") + 1])

    success, error = add_comment(input_path, output_path, comment_text, author, paragraph_idx)

    if success:
        print(f"Comment added to paragraph {paragraph_idx}: {output_path}")
    else:
        print(f"Error: {error}")
        sys.exit(1)
