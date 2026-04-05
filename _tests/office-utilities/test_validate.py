#!/usr/bin/env python3
"""Test office utility: validate.py — XXE stripping and security checks.

Tests:
- XXE entity stripping
- DTD declaration removal
- External reference detection
- SYSTEM/PUBLIC reference removal
- Clean XML passes through unchanged

Run: python -m pytest _tests/office-utilities/test_validate.py -v
"""

import os
import sys

# Add office scripts to path
OFFICE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "branding", "scripts", "office")
sys.path.insert(0, OFFICE_DIR)

from validate import strip_xxe, check_external_references


# ── XXE stripping tests ────────────────────────────────────


def test_strip_entity_declaration():
    """<!ENTITY> declarations should be removed."""
    xml = '<?xml version="1.0"?><!ENTITY xxe SYSTEM "file:///etc/passwd"><root>&xxe;</root>'
    result = strip_xxe(xml)
    assert "<!ENTITY" not in result
    assert "file:///etc/passwd" not in result


def test_strip_doctype():
    """<!DOCTYPE> with entities should be removed."""
    xml = '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><root/>'
    result = strip_xxe(xml)
    assert "<!DOCTYPE" not in result
    assert "<!ENTITY" not in result


def test_strip_system_reference():
    """SYSTEM references should be removed."""
    xml = '<root SYSTEM "http://evil.com/dtd"/>'
    result = strip_xxe(xml)
    assert "http://evil.com" not in result


def test_strip_public_reference():
    """PUBLIC references should be removed."""
    xml = '<root PUBLIC "-//W3C//DTD XHTML 1.0//EN" "http://evil.com/xhtml1.dtd"/>'
    result = strip_xxe(xml)
    assert "http://evil.com" not in result


def test_clean_xml_unchanged():
    """Clean XML without entities should pass through with minimal changes."""
    xml = '<?xml version="1.0"?><root><child attr="value">text</child></root>'
    result = strip_xxe(xml)
    assert "<root>" in result
    assert "<child" in result
    assert "text" in result


def test_strip_xxe_bytes_input():
    """Should handle bytes input."""
    xml = b'<?xml version="1.0"?><!ENTITY xxe SYSTEM "file:///etc/passwd"><root/>'
    result = strip_xxe(xml)
    assert isinstance(result, str)
    assert "<!ENTITY" not in result


def test_strip_multiple_entities():
    """Multiple entity declarations should all be removed."""
    xml = '<!ENTITY a SYSTEM "file:///a"><!ENTITY b SYSTEM "file:///b"><root/>'
    result = strip_xxe(xml)
    assert result.count("<!ENTITY") == 0


# ── External reference detection tests ─────────────────────


def test_detect_external_target():
    """HTTP targets in relationships should be detected."""
    xml = '<Relationships><Relationship Target="https://evil.com/data" Type="link"/></Relationships>'
    refs = check_external_references(xml)
    assert "https://evil.com/data" in refs


def test_detect_external_target_mode():
    """TargetMode=External should be detected."""
    xml = '<Relationship Target="payload.xml" TargetMode="External"/>'
    refs = check_external_references(xml)
    assert len(refs) > 0


def test_no_external_refs_in_clean_xml():
    """Clean internal relationships should return empty."""
    xml = '<Relationships><Relationship Target="slides/slide1.xml" Type="slide"/></Relationships>'
    refs = check_external_references(xml)
    assert len(refs) == 0


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = failed = 0
    for test in tests:
        try:
            test()
            print(f"  PASS  {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR {test.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
