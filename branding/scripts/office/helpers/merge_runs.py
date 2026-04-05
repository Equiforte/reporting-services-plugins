#!/usr/bin/env python3
"""Merge adjacent text runs with identical formatting in Office XML.

Consolidates fragmented runs that result from editing or tracked changes,
producing cleaner XML without changing visual output.

Usage:
    python merge_runs.py <xml_file> [--output <output_file>]
"""

import re
import sys


def merge_runs(xml_content):
    """Merge adjacent w:r elements with identical w:rPr formatting.

    Args:
        xml_content: XML string containing Word document body.

    Returns:
        XML string with merged runs.
    """
    # Pattern: two adjacent <w:r> elements where the rPr (run properties) are identical
    # This is a simplified approach — for production, use lxml for proper XML handling
    pattern = r'(<w:r>)\s*(<w:rPr>(.*?)</w:rPr>)\s*<w:t[^>]*>(.*?)</w:t>\s*</w:r>\s*<w:r>\s*<w:rPr>\3</w:rPr>\s*<w:t[^>]*>(.*?)</w:t>\s*(</w:r>)'

    prev = None
    while prev != xml_content:
        prev = xml_content
        xml_content = re.sub(
            pattern,
            lambda m: f'{m.group(1)}{m.group(2)}<w:t xml:space="preserve">{m.group(4)}{m.group(5)}</w:t>{m.group(6)}',
            xml_content,
            flags=re.DOTALL,
        )

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

    result = merge_runs(content)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result)

    print(f"Merged runs in {input_file} -> {output_file}")
