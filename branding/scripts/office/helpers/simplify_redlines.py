#!/usr/bin/env python3
"""Simplify tracked changes (redlines) in Office XML documents.

Accepts all tracked insertions and removes all tracked deletions,
producing a clean document without revision marks.

Usage:
    python simplify_redlines.py <xml_file> [--output <output_file>]
"""

import re
import sys


def simplify_redlines(xml_content):
    """Accept all insertions and remove all deletions from tracked changes.

    Args:
        xml_content: XML string containing Word document body with tracked changes.

    Returns:
        XML string with tracked changes resolved.
    """
    # Accept insertions: unwrap <w:ins> elements, keeping their content
    xml_content = re.sub(r'<w:ins\b[^>]*>(.*?)</w:ins>', r'\1', xml_content, flags=re.DOTALL)

    # Remove deletions: remove <w:del> elements and their content entirely
    xml_content = re.sub(r'<w:del\b[^>]*>.*?</w:del>', '', xml_content, flags=re.DOTALL)

    # Remove revision properties
    xml_content = re.sub(r'<w:rPr>.*?<w:rPrChange\b[^>]*>.*?</w:rPrChange>.*?</w:rPr>',
                         lambda m: re.sub(r'<w:rPrChange\b[^>]*>.*?</w:rPrChange>', '', m.group(0), flags=re.DOTALL),
                         xml_content, flags=re.DOTALL)

    return xml_content


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = input_file
    if "--output" in sys.argv:
        output_file = sys.argv[sys.argv.index("--output") + 1]

    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    result = simplify_redlines(content)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result)

    print(f"Simplified redlines in {input_file} -> {output_file}")
