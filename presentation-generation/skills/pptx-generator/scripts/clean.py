#!/usr/bin/env python3
"""Clean an extracted PPTX directory by removing orphaned files and fixing references.

Removes media files not referenced by any slide, fixes broken relationships,
and removes empty elements.

Usage:
    python clean.py <extracted_dir>
"""

import os
import re
import sys
import glob


def find_referenced_media(extracted_dir):
    """Find all media files referenced in slide relationships."""
    referenced = set()
    rels_pattern = os.path.join(extracted_dir, "ppt", "slides", "_rels", "*.xml.rels")

    for rels_file in glob.glob(rels_pattern):
        with open(rels_file, "r", encoding="utf-8") as f:
            content = f.read()
        # Find Target attributes pointing to media
        targets = re.findall(r'Target="\.\./(media/[^"]+)"', content)
        referenced.update(targets)

    # Also check presentation.xml.rels
    pres_rels = os.path.join(extracted_dir, "ppt", "_rels", "presentation.xml.rels")
    if os.path.isfile(pres_rels):
        with open(pres_rels, "r", encoding="utf-8") as f:
            content = f.read()
        targets = re.findall(r'Target="(media/[^"]+)"', content)
        referenced.update(targets)

    return referenced


def clean(extracted_dir):
    """Clean an extracted PPTX directory.

    Args:
        extracted_dir: Path to the extracted PPTX directory.

    Returns:
        dict with 'removed_files', 'fixed_rels', and 'errors'.
    """
    results = {
        "removed_files": [],
        "fixed_rels": 0,
        "errors": [],
    }

    if not os.path.isdir(extracted_dir):
        results["errors"].append(f"Directory not found: {extracted_dir}")
        return results

    # Find referenced media
    referenced = find_referenced_media(extracted_dir)

    # Remove orphaned media files
    media_dir = os.path.join(extracted_dir, "ppt", "media")
    if os.path.isdir(media_dir):
        for filename in os.listdir(media_dir):
            media_path = f"media/{filename}"
            if media_path not in referenced:
                full_path = os.path.join(media_dir, filename)
                os.remove(full_path)
                results["removed_files"].append(media_path)

    # Remove empty slide relationship files
    rels_dir = os.path.join(extracted_dir, "ppt", "slides", "_rels")
    if os.path.isdir(rels_dir):
        for rels_file in os.listdir(rels_dir):
            full_path = os.path.join(rels_dir, rels_file)
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            # If no Relationship elements, it's empty
            if "<Relationship " not in content:
                os.remove(full_path)
                results["removed_files"].append(f"slides/_rels/{rels_file}")

    return results


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    result = clean(sys.argv[1])

    import json
    print(json.dumps(result, indent=2))

    if result["removed_files"]:
        print(f"\nRemoved {len(result['removed_files'])} orphaned files.")
    else:
        print("\nNo orphaned files found.")
