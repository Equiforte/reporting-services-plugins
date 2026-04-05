#!/usr/bin/env bash
set -euo pipefail

# Rebuild the pre-initialized template base (base.tar.gz).
# Run this when dependencies need updating (new shadcn components, Vite version bump).
#
# Usage:
#   bash rebuild-base.sh [--output /path/to/_base/base.tar.gz]
#
# Requires: Node.js 20+

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT="${PLUGIN_DIR}/_base/base.tar.gz"

while [[ $# -gt 0 ]]; do
  case $1 in
    --output) OUTPUT="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

WORK_DIR=$(mktemp -d)
trap "rm -rf $WORK_DIR" EXIT

echo "=== Scaffolding Vite + React + TypeScript ==="
cd "$WORK_DIR"
npm create vite@latest app -- --template react-ts
cd app

echo "=== Installing dependencies ==="
npm install

echo "=== Installing Tailwind CSS ==="
npm install -D tailwindcss @tailwindcss/vite

echo "=== Initializing shadcn/ui ==="
npx shadcn@latest init -y

echo "=== Installing Recharts (required for shadcn/ui charts) ==="
npm install recharts

echo "=== Installing shadcn/ui components ==="
# Core UI components
COMPONENTS="card table badge tabs separator scroll-area collapsible tooltip"
# Charts — built on Recharts (https://ui.shadcn.com/charts)
COMPONENTS="$COMPONENTS chart"
# Sidebar block (https://ui.shadcn.com/docs/components/sidebar)
COMPONENTS="$COMPONENTS sidebar"
# Additional interactive components
COMPONENTS="$COMPONENTS select button dropdown-menu avatar breadcrumb"

for comp in $COMPONENTS; do
  echo "  Adding $comp..."
  npx shadcn@latest add "$comp" -y 2>/dev/null || echo "  Warning: $comp may not be available"
done

echo "=== Configuring Vite base ==="
# Ensure base: './' for self-containment
if grep -q "defineConfig" vite.config.ts; then
  sed -i.bak "s|defineConfig({|defineConfig({ base: './',|" vite.config.ts
  rm -f vite.config.ts.bak
fi

echo "=== Creating minimal index.css ==="
cat > src/index.css << 'CSSEOF'
@import "tailwindcss";

/* Brand variables injected by build.sh */
CSSEOF

echo "=== Creating placeholder App.tsx ==="
cat > src/App.tsx << 'TSXEOF'
// Template content will be copied here by build.sh
export default function App() {
  return <div>Template placeholder — replaced during build</div>
}
TSXEOF

echo "=== Creating public/data.json placeholder ==="
mkdir -p public
echo '{"meta":{"title":"Placeholder"},"data":{}}' > public/data.json

echo "=== Archiving base ==="
cd "$WORK_DIR"
mkdir -p "$(dirname "$OUTPUT")"
tar czf "$OUTPUT" -C "$WORK_DIR" app/

echo ""
echo "Base template archived: $OUTPUT"
echo "Size: $(du -h "$OUTPUT" | cut -f1)"
echo ""
echo "Includes: Vite + React + TS + Tailwind + Recharts + shadcn/ui ($COMPONENTS)"
