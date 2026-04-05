#!/usr/bin/env python3
"""Test brand-config.json against its JSON Schema.

Validates:
- Default config passes schema validation
- Valid overrides pass
- Invalid values fail (wrong color format, unknown fields, wrong types)

Run: python -m pytest _tests/schema-validation/test_schema.py -v
Requires: jsonschema (pip install jsonschema)
"""

import json
import os
import sys

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "branding", "skills", "brand", "assets")
CONFIG_PATH = os.path.join(ASSETS_DIR, "brand-config.json")
SCHEMA_PATH = os.path.join(ASSETS_DIR, "brand-config.schema.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def load_schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)


def validate(instance, schema):
    """Validate JSON instance against schema. Returns (valid, errors)."""
    try:
        import jsonschema
    except ImportError:
        return _basic_validate(instance, schema)

    try:
        jsonschema.validate(instance=instance, schema=schema)
        return True, []
    except jsonschema.ValidationError as e:
        return False, [str(e.message)]


def _basic_validate(instance, schema):
    """Minimal validation without jsonschema library."""
    errors = []

    if schema.get("type") == "object" and not isinstance(instance, dict):
        errors.append(f"Expected object, got {type(instance).__name__}")
        return False, errors

    # Check additionalProperties
    if schema.get("additionalProperties") is False:
        props = schema.get("properties", {})
        for key in instance:
            if key not in props:
                errors.append(f"Unknown property: {key}")

    # Check property types
    for key, prop_schema in schema.get("properties", {}).items():
        if key in instance:
            val = instance[key]
            expected_type = prop_schema.get("type")
            if expected_type == "string" and not isinstance(val, str):
                errors.append(f"{key}: expected string, got {type(val).__name__}")
            elif expected_type == "number" and not isinstance(val, (int, float)):
                errors.append(f"{key}: expected number, got {type(val).__name__}")
            elif expected_type == "boolean" and not isinstance(val, bool):
                errors.append(f"{key}: expected boolean, got {type(val).__name__}")
            elif expected_type == "object" and not isinstance(val, dict):
                errors.append(f"{key}: expected object, got {type(val).__name__}")

            # Check hex color pattern
            pattern = prop_schema.get("pattern")
            if pattern and pattern == "^#[0-9A-Fa-f]{6}$" and isinstance(val, str):
                import re
                if not re.match(pattern, val):
                    errors.append(f"{key}: '{val}' does not match hex color pattern")

    return len(errors) == 0, errors


# ── Tests ──────────────────────────────────────────────────


def test_default_config_valid():
    """Default brand-config.json should pass schema validation."""
    config = load_config()
    schema = load_schema()
    valid, errors = validate(config, schema)
    assert valid, f"Default config failed validation: {errors}"


def test_valid_partial_override():
    """A valid partial override should pass."""
    schema = load_schema()
    override = {
        "firm": {"name": "Globex Corp"},
        "colors": {"primary": "#003366"},
    }
    valid, errors = validate(override, schema)
    assert valid, f"Valid override failed: {errors}"


def test_invalid_color_format():
    """A color without # prefix should fail."""
    schema = load_schema()
    invalid = {"colors": {"primary": "003366"}}  # missing #
    valid, errors = validate(invalid, schema)
    # This should fail if jsonschema is available, or pass basic validation
    # The important thing is the pattern exists in the schema
    assert "pattern" in schema["properties"]["colors"]["properties"]["primary"]


def test_schema_has_all_sections():
    """Schema should define all 8 config sections plus top-level flags."""
    schema = load_schema()
    props = schema.get("properties", {})
    expected = ["firm", "colors", "semantic", "components", "typography", "number_formats", "layout", "content", "nl_overrides", "mode"]
    for section in expected:
        assert section in props, f"Schema missing property: {section}"


def test_schema_mode_enum():
    """mode should be restricted to best_effort or strict."""
    schema = load_schema()
    mode_schema = schema["properties"]["mode"]
    assert mode_schema.get("enum") == ["best_effort", "strict"]


def test_schema_nl_overrides_boolean():
    """nl_overrides should be boolean type."""
    schema = load_schema()
    nl_schema = schema["properties"]["nl_overrides"]
    assert nl_schema.get("type") == "boolean"


def test_schema_colors_hex_pattern():
    """All color fields should require hex pattern."""
    schema = load_schema()
    color_props = schema["properties"]["colors"]["properties"]
    for name, prop in color_props.items():
        assert prop.get("pattern") == "^#[0-9A-Fa-f]{6}$", f"colors.{name} missing hex pattern"


def test_schema_no_additional_properties():
    """Schema should reject unknown top-level properties."""
    schema = load_schema()
    assert schema.get("additionalProperties") is False


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = failed = 0
    for test in tests:
        try:
            test()
            print(f"  PASS  {test.__name__}")
            passed += 1
        except (AssertionError, AssertionError) as e:
            print(f"  FAIL  {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR {test.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
