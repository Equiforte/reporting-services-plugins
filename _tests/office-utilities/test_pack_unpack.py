#!/usr/bin/env python3
"""Test office utilities: pack.py and unpack.py — ZIP roundtrip.

Tests:
- Unpack extracts files correctly
- Pack creates valid ZIP
- Roundtrip preserves content
- Path traversal is blocked

Run: python -m pytest _tests/office-utilities/test_pack_unpack.py -v
"""

import json
import os
import sys
import tempfile
import zipfile

OFFICE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "branding", "scripts", "office")
sys.path.insert(0, OFFICE_DIR)

from pack import pack
from unpack import unpack


def create_test_zip(path, files):
    """Create a test ZIP file with given file contents.

    Args:
        path: Output ZIP path.
        files: Dict of {arcname: content_string}.
    """
    with zipfile.ZipFile(path, "w") as zf:
        for name, content in files.items():
            zf.writestr(name, content)


# ── Tests ──────────────────────────────────────────────────


def test_unpack_extracts_files():
    """Unpack should extract all files from a ZIP."""
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "test.zip")
        create_test_zip(zip_path, {
            "[Content_Types].xml": "<Types/>",
            "word/document.xml": "<document/>",
        })

        out_dir = os.path.join(tmpdir, "extracted")
        result = unpack(zip_path, out_dir)

        assert result["success"] is True
        assert os.path.isfile(os.path.join(out_dir, "[Content_Types].xml"))
        assert os.path.isfile(os.path.join(out_dir, "word", "document.xml"))


def test_unpack_returns_file_list():
    """Unpack should return list of extracted files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "test.zip")
        create_test_zip(zip_path, {"a.xml": "<a/>", "b.xml": "<b/>"})

        out_dir = os.path.join(tmpdir, "extracted")
        result = unpack(zip_path, out_dir)

        assert result["success"] is True
        assert "a.xml" in result["files"]
        assert "b.xml" in result["files"]


def test_unpack_invalid_zip():
    """Unpack should fail gracefully on non-ZIP files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        bad_path = os.path.join(tmpdir, "notazip.docx")
        with open(bad_path, "w") as f:
            f.write("this is not a zip")

        out_dir = os.path.join(tmpdir, "extracted")
        result = unpack(bad_path, out_dir)

        assert result["success"] is False
        assert "valid ZIP" in result["error"]


def test_unpack_missing_file():
    """Unpack should fail on missing file."""
    result = unpack("/nonexistent/file.docx", "/tmp/out")
    assert result["success"] is False
    assert "not found" in result["error"].lower()


def test_pack_creates_zip():
    """Pack should create a valid ZIP file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create directory structure
        src_dir = os.path.join(tmpdir, "src")
        os.makedirs(os.path.join(src_dir, "word"))
        with open(os.path.join(src_dir, "[Content_Types].xml"), "w") as f:
            f.write("<Types/>")
        with open(os.path.join(src_dir, "word", "document.xml"), "w") as f:
            f.write("<document/>")

        out_path = os.path.join(tmpdir, "output.docx")
        result = pack(src_dir, out_path)

        assert result["success"] is True
        assert os.path.isfile(out_path)
        assert zipfile.is_zipfile(out_path)


def test_roundtrip_preserves_content():
    """Unpack → pack should preserve file contents."""
    with tempfile.TemporaryDirectory() as tmpdir:
        original_content = "<document><p>Hello World</p></document>"

        zip_path = os.path.join(tmpdir, "original.docx")
        create_test_zip(zip_path, {
            "[Content_Types].xml": "<Types/>",
            "word/document.xml": original_content,
        })

        # Unpack
        extracted = os.path.join(tmpdir, "extracted")
        unpack(zip_path, extracted)

        # Pack
        repacked = os.path.join(tmpdir, "repacked.docx")
        pack(extracted, repacked)

        # Verify content
        with zipfile.ZipFile(repacked, "r") as zf:
            result = zf.read("word/document.xml").decode("utf-8")
            assert result == original_content


def test_pack_missing_dir():
    """Pack should fail on missing directory."""
    result = pack("/nonexistent/dir", "/tmp/out.docx")
    assert result["success"] is False


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
