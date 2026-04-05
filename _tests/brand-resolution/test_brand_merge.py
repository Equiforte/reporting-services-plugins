#!/usr/bin/env python3
"""Test brand resolution: JSON merge, token derivation, override precedence.

Tests the deterministic parts of brand resolution:
- Default config loads correctly
- JSON overrides deep-merge onto defaults
- Semantic tokens derive from resolved colors
- Component tokens derive from resolved colors
- Partial overrides only change specified fields
- nl_overrides: false is respected
- Logo suppression when firm.name overridden without custom logo
- firm.website suppression when firm.name overridden without explicit website

Run: python -m pytest _tests/brand-resolution/test_brand_merge.py -v
"""

import json
import os
import copy

# Path to default brand config
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "branding", "skills", "brand", "assets")
DEFAULT_CONFIG_PATH = os.path.join(ASSETS_DIR, "brand-config.json")


def load_defaults():
    with open(DEFAULT_CONFIG_PATH) as f:
        return json.load(f)


def deep_merge(base, override):
    """Deep merge override onto base. Returns new dict."""
    result = copy.deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def derive_semantic_tokens(config):
    """Derive semantic tokens from colors (for fields not explicitly set)."""
    colors = config.get("colors", {})
    semantic = config.get("semantic", {})

    defaults = {
        "heading_color": colors.get("primary"),
        "body_color": colors.get("text"),
        "muted_color": colors.get("text_secondary"),
        "link_color": colors.get("accent"),
        "chart_series": [
            colors.get("primary"),
            colors.get("accent"),
            colors.get("positive"),
            colors.get("warning"),
            colors.get("negative"),
        ],
    }

    for key, default_val in defaults.items():
        if key not in semantic:
            semantic[key] = default_val

    config["semantic"] = semantic
    return config


def derive_component_tokens(config):
    """Derive component tokens from colors (for fields not explicitly set)."""
    colors = config.get("colors", {})
    components = config.get("components", {})

    defaults = {
        "table_header_bg": colors.get("primary"),
        "table_header_text": colors.get("white"),
        "table_alt_row": colors.get("surface"),
    }

    for key, default_val in defaults.items():
        if key not in components:
            components[key] = default_val

    config["components"] = components
    return config


# ── Tests ──────────────────────────────────────────────────


def test_defaults_load():
    """Default brand-config.json loads and has all 8 sections."""
    config = load_defaults()
    expected_sections = ["firm", "colors", "semantic", "components", "typography", "number_formats", "layout", "content"]
    for section in expected_sections:
        assert section in config, f"Missing section: {section}"


def test_defaults_firm():
    config = load_defaults()
    assert config["firm"]["name"] == "Acme Inc"
    assert config["firm"]["tagline"] == "Building the future"


def test_defaults_colors():
    config = load_defaults()
    assert config["colors"]["primary"] == "#1B3A5C"
    assert config["colors"]["accent"] == "#2E75B6"


def test_partial_override_firm():
    """Overriding firm.name doesn't erase firm.tagline."""
    base = load_defaults()
    override = {"firm": {"name": "Globex Corp"}}
    result = deep_merge(base, override)

    assert result["firm"]["name"] == "Globex Corp"
    assert result["firm"]["tagline"] == "Building the future"  # preserved


def test_partial_override_colors():
    """Overriding colors.primary doesn't erase colors.accent."""
    base = load_defaults()
    override = {"colors": {"primary": "#003366"}}
    result = deep_merge(base, override)

    assert result["colors"]["primary"] == "#003366"
    assert result["colors"]["accent"] == "#2E75B6"  # preserved


def test_semantic_derivation_from_overridden_colors():
    """Semantic tokens should derive from the OVERRIDDEN colors, not defaults."""
    base = load_defaults()
    override = {"colors": {"primary": "#FF0000"}}
    result = deep_merge(base, override)

    # Clear semantic so derivation runs fresh
    result.pop("semantic", None)
    result = derive_semantic_tokens(result)

    assert result["semantic"]["heading_color"] == "#FF0000"
    assert result["semantic"]["chart_series"][0] == "#FF0000"


def test_component_derivation_from_overridden_colors():
    """Component tokens should derive from overridden colors."""
    base = load_defaults()
    override = {"colors": {"primary": "#FF0000"}}
    result = deep_merge(base, override)

    result.pop("components", None)
    result = derive_component_tokens(result)

    assert result["components"]["table_header_bg"] == "#FF0000"


def test_explicit_semantic_not_overwritten_by_derivation():
    """Explicitly set semantic tokens should NOT be overwritten by derivation."""
    base = load_defaults()
    override = {
        "colors": {"primary": "#FF0000"},
        "semantic": {"heading_color": "#00FF00"},
    }
    result = deep_merge(base, override)
    result = derive_semantic_tokens(result)

    # heading_color was explicitly set to green — should NOT derive from red primary
    assert result["semantic"]["heading_color"] == "#00FF00"


def test_nl_overrides_false_flag():
    """nl_overrides: false should be preserved through merge."""
    base = load_defaults()
    override = {"nl_overrides": False}
    result = deep_merge(base, override)

    assert result["nl_overrides"] is False


def test_mode_strict_flag():
    """mode: strict should be preserved through merge."""
    base = load_defaults()
    override = {"mode": "strict"}
    result = deep_merge(base, override)

    assert result["mode"] == "strict"


def test_website_suppression_logic():
    """When firm.name is overridden but firm.website is NOT, website should be suppressed."""
    base = load_defaults()
    override = {"firm": {"name": "Globex Corp"}}
    result = deep_merge(base, override)

    # The override only sets firm.name, not firm.website
    # The brand skill should detect this and suppress website in output
    # We test the detection logic: was website explicitly in the override?
    assert "website" not in override.get("firm", {}), "website was not explicitly set"
    assert result["firm"]["website"] == "https://www.acme-inc.com", "default still present in merged config"
    # The brand skill must check the override keys, not the merged result


def test_logo_suppression_logic():
    """When firm.name is overridden, logo should be suppressed if no custom logo exists."""
    override = {"firm": {"name": "Globex Corp"}}

    # Simulate: check if .reporting/logo.png exists
    custom_logo_exists = False  # no custom logo

    firm_name_overridden = "name" in override.get("firm", {})
    should_suppress_logo = firm_name_overridden and not custom_logo_exists

    assert should_suppress_logo is True


def test_full_override_scenario():
    """Full Globex Corp override scenario from the spec."""
    base = load_defaults()
    override = {
        "firm": {"name": "Globex Corp", "tagline": "Science. Industry. Results."},
        "colors": {"primary": "#003366", "accent": "#0077CC"},
    }
    result = deep_merge(base, override)

    # Clear semantic/components for fresh derivation
    for key in ["semantic", "components"]:
        result.pop(key, None)
    result = derive_semantic_tokens(result)
    result = derive_component_tokens(result)

    # Firm
    assert result["firm"]["name"] == "Globex Corp"
    assert result["firm"]["tagline"] == "Science. Industry. Results."
    assert result["firm"]["website"] == "https://www.acme-inc.com"  # default preserved

    # Colors
    assert result["colors"]["primary"] == "#003366"
    assert result["colors"]["accent"] == "#0077CC"
    assert result["colors"]["text"] == "#2D2D2D"  # default

    # Derived tokens
    assert result["semantic"]["heading_color"] == "#003366"
    assert result["semantic"]["link_color"] == "#0077CC"
    assert result["components"]["table_header_bg"] == "#003366"

    # Untouched sections
    assert result["typography"]["font_family"] == "Calibri, sans-serif"
    assert result["layout"]["page_size"] == "letter"
    assert result["number_formats"]["currency"] == "$#,##0"


if __name__ == "__main__":
    import sys
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    passed = 0
    failed = 0
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
