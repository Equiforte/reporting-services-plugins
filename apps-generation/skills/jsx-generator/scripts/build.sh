#!/usr/bin/env bash
set -euo pipefail

# Build a self-contained React app from a pre-initialized template base.
#
# Usage:
#   bash build.sh \
#     --template dashboard \
#     --data /path/to/data.json \
#     --brand /path/to/brand-config.json \
#     --logo /path/to/logo.png \
#     --output output/app/my-dashboard \
#     --plugin-dir /path/to/jsx-generator
#
# Requires: Node.js 20+

TEMPLATE=""
DATA_FILE=""
BRAND_FILE=""
LOGO_FILE=""
OUTPUT_DIR=""
PLUGIN_DIR=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --template) TEMPLATE="$2"; shift 2 ;;
    --data) DATA_FILE="$2"; shift 2 ;;
    --brand) BRAND_FILE="$2"; shift 2 ;;
    --logo) LOGO_FILE="$2"; shift 2 ;;
    --output) OUTPUT_DIR="$2"; shift 2 ;;
    --plugin-dir) PLUGIN_DIR="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# Validate required args
if [[ -z "$TEMPLATE" || -z "$DATA_FILE" || -z "$BRAND_FILE" || -z "$OUTPUT_DIR" || -z "$PLUGIN_DIR" ]]; then
  echo "Error: --template, --data, --brand, --output, and --plugin-dir are required"
  exit 1
fi

# Validate template exists
TEMPLATE_DIR="$PLUGIN_DIR/templates/$TEMPLATE"
if [[ ! -d "$TEMPLATE_DIR" ]]; then
  echo "Error: Template not found: $TEMPLATE_DIR"
  echo "Available templates: $(ls "$PLUGIN_DIR/templates/" 2>/dev/null || echo 'none')"
  exit 1
fi

# Validate base tarball exists
BASE_TAR="$PLUGIN_DIR/_base/base.tar.gz"
if [[ ! -f "$BASE_TAR" ]]; then
  echo "Error: Pre-initialized base not found: $BASE_TAR"
  echo "Run: bash $PLUGIN_DIR/scripts/rebuild-base.sh"
  exit 1
fi

WORK_DIR=$(mktemp -d)
trap "rm -rf $WORK_DIR" EXIT

echo "=== Step 1: Untar pre-initialized base ==="
tar xzf "$BASE_TAR" -C "$WORK_DIR"
# If base was archived with an app/ subdirectory, flatten it
if [[ -d "$WORK_DIR/app" && ! -f "$WORK_DIR/package.json" ]]; then
  mv "$WORK_DIR/app"/* "$WORK_DIR/app"/.[!.]* "$WORK_DIR/" 2>/dev/null || true
  rmdir "$WORK_DIR/app" 2>/dev/null || true
fi

echo "=== Step 2: Copy template into src/ ==="
cp -r "$TEMPLATE_DIR"/* "$WORK_DIR/src/" 2>/dev/null || true

echo "=== Step 3: Inject data.json ==="
node "$PLUGIN_DIR/scripts/inject-data.js" "$DATA_FILE" "$WORK_DIR/public/data.json"

echo "=== Step 4: Apply brand overrides ==="
# Read brand colors and write to CSS custom properties
node -e "
const brand = JSON.parse(require('fs').readFileSync('$BRAND_FILE', 'utf8'));
const css = \`
:root {
  --brand-primary: \${brand.colors?.primary || '#1B3A5C'};
  --brand-accent: \${brand.colors?.accent || '#2E75B6'};
  --brand-text: \${brand.colors?.text || '#2D2D2D'};
  --brand-text-secondary: \${brand.colors?.text_secondary || '#666666'};
  --brand-surface: \${brand.colors?.surface || '#F7F8FA'};
  --brand-positive: \${brand.colors?.positive || '#1A7A3A'};
  --brand-warning: \${brand.colors?.warning || '#C67700'};
  --brand-negative: \${brand.colors?.negative || '#C4261D'};
  --brand-heading: \${brand.semantic?.heading_color || brand.colors?.primary || '#1B3A5C'};
  --brand-border: \${brand.semantic?.border_color || '#D1D5DB'};
  --brand-card-radius: \${brand.components?.card_radius || '8px'};
  --brand-card-shadow: \${brand.components?.card_shadow || '0 1px 3px rgba(0,0,0,0.12)'};
}
\`;
const indexCss = '$WORK_DIR/src/index.css';
const existing = require('fs').readFileSync(indexCss, 'utf8');
require('fs').writeFileSync(indexCss, css + '\n' + existing);
console.log('Brand CSS variables injected');
"

# Copy logo if provided
if [[ -n "$LOGO_FILE" && -f "$LOGO_FILE" ]]; then
  cp "$LOGO_FILE" "$WORK_DIR/public/logo.png"
  echo "Logo copied to public/"
fi

# Write brand manifest for the app to read
cp "$BRAND_FILE" "$WORK_DIR/public/brand.json"

echo "=== Step 5: Write Vite config ==="
cat > "$WORK_DIR/vite.config.ts" << 'VITEEOF'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

export default defineConfig({
  base: './',
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    rollupOptions: {
      onwarn(warning, warn) {
        // Suppress unresolved import warnings for optional deps
        if (warning.message?.includes('tslib')) return
        warn(warning)
      },
    },
  },
})
VITEEOF

echo "=== Step 5b: Install any missing transitive deps ==="
cd "$WORK_DIR"
npm install tslib 2>/dev/null || true

echo "=== Step 6: Build with Vite ==="
npm run build

echo "=== Step 7: Verify self-containment ==="
bash "$PLUGIN_DIR/scripts/verify-self-contained.sh" "$WORK_DIR/dist"

echo "=== Step 8: Copy to output ==="
mkdir -p "$OUTPUT_DIR"
rm -rf "$OUTPUT_DIR/dist" "$OUTPUT_DIR/src"
cp -r "$WORK_DIR/dist" "$OUTPUT_DIR/dist"
cp -r "$WORK_DIR/src" "$OUTPUT_DIR/src"
cp "$WORK_DIR/public/data.json" "$OUTPUT_DIR/" 2>/dev/null || true
cp "$WORK_DIR/package.json" "$OUTPUT_DIR/" 2>/dev/null || true
cp "$WORK_DIR/vite.config.ts" "$OUTPUT_DIR/" 2>/dev/null || true
cp "$WORK_DIR/tsconfig.json" "$OUTPUT_DIR/" 2>/dev/null || true
cp "$WORK_DIR/tsconfig.app.json" "$OUTPUT_DIR/" 2>/dev/null || true
cp "$WORK_DIR/components.json" "$OUTPUT_DIR/" 2>/dev/null || true

echo ""
echo "Build complete: $OUTPUT_DIR/dist/index.html"
echo "Open in browser: file://$(cd "$OUTPUT_DIR/dist" && pwd)/index.html"
