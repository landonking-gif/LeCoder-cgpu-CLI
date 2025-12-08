#!/usr/bin/env node
import { execSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const binariesDir = path.resolve(__dirname, '..', 'binaries');

// Platform-specific binary names
const binaries = [
  { name: 'lecoder-cgpu-macos-x64', platform: 'darwin', arch: 'x64' },
  { name: 'lecoder-cgpu-macos-arm64', platform: 'darwin', arch: 'arm64' },
  { name: 'lecoder-cgpu-win-x64.exe', platform: 'win32', arch: 'x64' },
  { name: 'lecoder-cgpu-linux-x64', platform: 'linux', arch: 'x64' },
  { name: 'lecoder-cgpu-linux-arm64', platform: 'linux', arch: 'arm64' },
];

console.log('🧪 Testing binaries...\n');

for (const binary of binaries) {
  const binaryPath = path.join(binariesDir, binary.name);
  
  // Check if binary exists
  if (!fs.existsSync(binaryPath)) {
    console.log(`⚠️  ${binary.name}: Not found (skipped)`);
    continue;
  }

  // Check file size (should be > 40MB with bundled Node.js)
  const stats = fs.statSync(binaryPath);
  const sizeMB = (stats.size / 1024 / 1024).toFixed(2);
  
  if (stats.size < 40 * 1024 * 1024) {
    console.log(`❌ ${binary.name}: Too small (${sizeMB}MB) - likely incomplete`);
    continue;
  }

  // Test version command (only on matching platform)
  if (process.platform === binary.platform && process.arch === binary.arch) {
    try {
      const output = execSync(`"${binaryPath}" --version`, { encoding: 'utf-8' });
      console.log(`✅ ${binary.name}: ${sizeMB}MB - Version: ${output.trim()}`);
    } catch (err) {
      console.log(`❌ ${binary.name}: ${sizeMB}MB - Failed to execute`);
    }
  } else {
    console.log(`✅ ${binary.name}: ${sizeMB}MB - Built successfully (cross-platform, not tested)`);
  }
}

console.log('\n✨ Binary testing complete!');
