#!/usr/bin/env node

/**
 * Inject data.json into a React app's public directory.
 *
 * Validates the JSON structure, ensures required fields exist,
 * and writes to the target path.
 *
 * Usage:
 *   node inject-data.js <source.json> <target_path>
 *
 * The source JSON must have a top-level "meta" object.
 */

const fs = require("fs");
const path = require("path");

const [, , sourcePath, targetPath] = process.argv;

if (!sourcePath || !targetPath) {
  console.error("Usage: node inject-data.js <source.json> <target_path>");
  process.exit(1);
}

// Read and validate source
let data;
try {
  const raw = fs.readFileSync(sourcePath, "utf8");
  data = JSON.parse(raw);
} catch (err) {
  console.error(`Error reading ${sourcePath}: ${err.message}`);
  process.exit(1);
}

// Validate structure
if (!data.meta) {
  console.error('Error: data.json must have a top-level "meta" object');
  process.exit(1);
}

if (!data.meta.title) {
  console.warn('Warning: data.json meta.title is missing');
}

// Ensure target directory exists
const targetDir = path.dirname(targetPath);
fs.mkdirSync(targetDir, { recursive: true });

// Write with pretty formatting
fs.writeFileSync(targetPath, JSON.stringify(data, null, 2), "utf8");

console.log(`Data injected: ${targetPath} (${Object.keys(data).length} top-level keys)`);
