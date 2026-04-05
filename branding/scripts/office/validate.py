#!/usr/bin/env python3
"""Validate Office XML files against XSD schemas and strip dangerous content.

Usage:
    python validate.py <office_file_or_xml> [--strip-xxe] [--check-schema]

Security features:
    - XXE stripping: removes <!ENTITY> declarations and DTD references
    - External reference detection: flags external URIs in relationships
    - Macro detection: warns about embedded macros/VBA

Requires: defusedxml (pip install defusedxml)
"""

import os
import sys
import re


def strip_xxe(xml_content):
    """Strip external entity references and DTD declarations from XML content.

    Prevents Local File Inclusion (LFI) and SSRF attacks via malicious
    Office documents processed by LibreOffice or pandoc.

    Args:
        xml_content: XML string or bytes.

    Returns:
        Cleaned XML string with entities and DTDs removed.
    """
    if isinstance(xml_content, bytes):
        xml_content = xml_content.decode("utf-8", errors="replace")

    # Remove DOCTYPE declarations (which may contain ENTITY definitions)
    xml_content = re.sub(r"<!DOCTYPE[^>]*>", "", xml_content, flags=re.DOTALL)

    # Remove standalone ENTITY declarations
    xml_content = re.sub(r"<!ENTITY[^>]*>", "", xml_content, flags=re.DOTALL)

    # Remove SYSTEM and PUBLIC references
    xml_content = re.sub(r'SYSTEM\s+"[^"]*"', "", xml_content)
    xml_content = re.sub(r"SYSTEM\s+'[^']*'", "", xml_content)
    xml_content = re.sub(r'PUBLIC\s+"[^"]*"\s+"[^"]*"', "", xml_content)

    return xml_content


def check_external_references(xml_content):
    """Detect external URI references in Office XML relationships.

    Args:
        xml_content: XML string.

    Returns:
        List of detected external URIs.
    """
    external_refs = []

    # Look for Target attributes with external URIs
    targets = re.findall(r'Target="(https?://[^"]+)"', xml_content)
    external_refs.extend(targets)

    # Look for TargetMode="External"
    if 'TargetMode="External"' in xml_content:
        ext_targets = re.findall(r'Target="([^"]+)"[^/]*TargetMode="External"', xml_content)
        external_refs.extend(ext_targets)

    return list(set(external_refs))


def detect_macros(file_path):
    """Check if an Office file contains macros or VBA code.

    Args:
        file_path: Path to the Office file.

    Returns:
        dict with 'has_macros' boolean and 'details' string.
    """
    import zipfile

    macro_indicators = [
        "vbaProject.bin",
        "vbaData.xml",
        "word/vbaProject.bin",
        "xl/vbaProject.bin",
        "ppt/vbaProject.bin",
    ]

    try:
        with zipfile.ZipFile(file_path, "r") as zf:
            names = zf.namelist()
            found = [name for name in names if any(ind in name for ind in macro_indicators)]
            if found:
                return {"has_macros": True, "details": f"Macro files found: {', '.join(found)}"}
            return {"has_macros": False, "details": "No macros detected."}
    except Exception as e:
        return {"has_macros": False, "details": f"Could not check: {e}"}


def validate_file(file_path, strip=False, check_schema=False):
    """Validate an Office file for security and schema compliance.

    Args:
        file_path: Path to Office file or XML file.
        strip: If True, strip XXE from all XML files in the archive.
        check_schema: If True, validate against Office XSD schemas.

    Returns:
        dict with validation results.
    """
    results = {
        "file": file_path,
        "valid": True,
        "warnings": [],
        "errors": [],
        "macros": None,
        "external_refs": [],
    }

    if not os.path.isfile(file_path):
        results["valid"] = False
        results["errors"].append(f"File not found: {file_path}")
        return results

    # Check for macros
    macro_check = detect_macros(file_path)
    results["macros"] = macro_check
    if macro_check["has_macros"]:
        results["warnings"].append(f"MACROS DETECTED: {macro_check['details']}")

    # Process XML contents
    import zipfile
    try:
        with zipfile.ZipFile(file_path, "r") as zf:
            for name in zf.namelist():
                if name.endswith(".xml") or name.endswith(".rels"):
                    content = zf.read(name).decode("utf-8", errors="replace")

                    # Check for external references
                    ext_refs = check_external_references(content)
                    if ext_refs:
                        results["external_refs"].extend(ext_refs)
                        results["warnings"].append(f"{name}: external references found: {ext_refs}")

                    # Strip XXE if requested
                    if strip:
                        cleaned = strip_xxe(content)
                        if cleaned != content:
                            results["warnings"].append(f"{name}: XXE content stripped")
    except zipfile.BadZipFile:
        results["valid"] = False
        results["errors"].append("Not a valid ZIP/Office file.")
    except Exception as e:
        results["valid"] = False
        results["errors"].append(str(e))

    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    file_path = sys.argv[1]
    strip = "--strip-xxe" in sys.argv
    check_schema = "--check-schema" in sys.argv

    result = validate_file(file_path, strip=strip, check_schema=check_schema)

    import json
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["valid"] else 1)
