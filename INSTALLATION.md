# Installation Guide

Complete step-by-step instructions for installing LeCoder cGPU CLI on all platforms.

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
  - [Method 1: Pre-built Binaries (Recommended)](#method-1-pre-built-binaries-recommended)
  - [Method 2: npm](#method-2-npm-requires-nodejs)
  - [Method 3: Build from Source](#method-3-build-from-source)
- [Platform-Specific Binary Instructions](#platform-specific-binary-instructions)
  - [macOS](#macos)
  - [Linux](#linux)
  - [Windows](#windows)
- [Verify Installation](#verify-installation)
- [Initial Setup](#initial-setup)
- [Updating](#updating)
- [Uninstalling](#uninstalling)
- [Troubleshooting](#troubleshooting)

---

## System Requirements

### For Binaries (No Node.js Required)
- **Memory**: 512 MB RAM
- **Storage**: ~80 MB per binary
- **Platforms**: 
  - ✅ macOS 10.15+ (Catalina and later)
  - ✅ Linux with glibc 2.17+ (Ubuntu 18.04+, Debian 10+, RHEL 8+, etc.)
  - ✅ Windows 10/11
- **Network**: Internet connection for Colab API

### For npm Installation
- **Node.js**: 18.0.0 or higher
- **npm**: 9.0.0 or higher
- **Memory**: 512 MB RAM
- **Storage**: 50 MB free space

### Google Account Requirements
- A Google account (free or paid)
- For best experience: Google Colab Pro or Pro+ subscription (optional)

---

## Installation Methods

## Method 1: Pre-built Binaries (Recommended)

Download the latest binary for your platform from [GitHub Releases](https://github.com/aryateja2106/LeCoder-cgpu-CLI/releases).

### macOS

**Intel (x64):**
```bash
# Download
curl -L -o lecoder-cgpu https://github.com/aryateja2106/LeCoder-cgpu-CLI/releases/latest/download/lecoder-cgpu-macos-x64

# Make executable
chmod +x lecoder-cgpu

# Move to PATH
sudo mv lecoder-cgpu /usr/local/bin/

# Verify
lecoder-cgpu --version
```

**Apple Silicon (arm64):**
```bash
# Download
curl -L -o lecoder-cgpu https://github.com/aryateja2106/LeCoder-cgpu-CLI/releases/latest/download/lecoder-cgpu-macos-arm64

# Make executable
chmod +x lecoder-cgpu

# Move to PATH
sudo mv lecoder-cgpu /usr/local/bin/

# Verify
lecoder-cgpu --version
```

### Linux

**x64:**
```bash
# Download
curl -L -o lecoder-cgpu https://github.com/aryateja2106/LeCoder-cgpu-CLI/releases/latest/download/lecoder-cgpu-linux-x64

# Make executable
chmod +x lecoder-cgpu

# Move to PATH
sudo mv lecoder-cgpu /usr/local/bin/

# Verify
lecoder-cgpu --version
```

**ARM64 (Raspberry Pi, AWS Graviton):**
```bash
# Download
curl -L -o lecoder-cgpu https://github.com/aryateja2106/LeCoder-cgpu-CLI/releases/latest/download/lecoder-cgpu-linux-arm64

# Make executable
chmod +x lecoder-cgpu

# Move to PATH
sudo mv lecoder-cgpu /usr/local/bin/

# Verify
lecoder-cgpu --version
```

### Windows

**x64:**
```powershell
# Download using PowerShell
Invoke-WebRequest -Uri "https://github.com/aryateja2106/LeCoder-cgpu-CLI/releases/latest/download/lecoder-cgpu-win-x64.exe" -OutFile "lecoder-cgpu.exe"

# Move to a directory in PATH (e.g., C:\Program Files\LeCoder)
# Or add current directory to PATH

# Verify
.\lecoder-cgpu.exe --version
```

### Verify Checksums

Download the checksum file for your platform and verify:

```bash
# macOS/Linux
sha256sum -c checksums-<platform>.txt

# Windows (PowerShell)
Get-FileHash lecoder-cgpu-win-x64.exe -Algorithm SHA256
```

---

## Method 2: npm (Requires Node.js)

```bash
npm install -g lecoder-cgpu
```

---

## Method 3: Build from Source

```bash
# Clone the repository
git clone https://github.com/aryateja2106/LeCoder-cgpu-CLI.git
cd LeCoder-cgpu-CLI

# Install dependencies and build
npm install
npm run build

# Link globally
npm link

# Verify
lecoder-cgpu --version
```

### Building Binaries (For Maintainers)

To build standalone binaries for distribution:

```bash
# Build all platforms
npm run pkg:all

# Or build specific platforms
npm run pkg:macos    # macOS x64 and arm64
npm run pkg:windows  # Windows x64
npm run pkg:linux    # Linux x64 and arm64

# Test generated binaries
npm run pkg:test
```

**Binary Naming Convention:**

Binaries are generated with platform-specific names:
- macOS: `lecoder-cgpu-macos-x64`, `lecoder-cgpu-macos-arm64`
- Windows: `lecoder-cgpu-win-x64.exe`
- Linux: `lecoder-cgpu-linux-x64`, `lecoder-cgpu-linux-arm64`

This naming is enforced via the `--output` flag in `pkg:*` scripts and must match what the test script (`scripts/test-binaries.js`) and CI workflow expect. If you modify the naming scheme, update all three locations accordingly.

### Publishing to NPM (Maintainers Only)

This section covers the complete workflow for publishing `lecoder-cgpu` to the npm registry.

#### Prerequisites

- npm account with publish access to the `lecoder-cgpu` package
- Two-factor authentication (2FA) enabled on your npm account
- Logged in via `npm login` (verify with `npm whoami`)
- All code changes committed and pushed to the repository

#### Pre-Publish Checklist

Before publishing, ensure:

- [ ] Version bumped in `package.json` (via `npm version` or manual edit)
- [ ] `CHANGELOG.md` updated with release notes for the new version
- [ ] All tests passing: `npm test`
- [ ] Build successful: `npm run build`
- [ ] Binaries built and tested: `npm run pkg:all && npm run pkg:test`
- [ ] `.npmignore` verified (no sensitive files will be published)

#### Local Package Verification

Before publishing to npm, verify the package contents locally using `npm pack`:

```bash
# Create a tarball of the package
npm pack

# Inspect the tarball contents
tar -tzf lecoder-cgpu-<version>.tgz | head -20

# Or view full contents
tar -tzf lecoder-cgpu-<version>.tgz | less
```

**Expected contents:**
- `package/dist/` - Compiled JavaScript and type definitions
- `package/package.json` - Package metadata
- `package/README.md` - Documentation
- `package/LICENSE` - License file
- `package/.npmignore` - Exclusion rules

**Should NOT contain:**
- `package/src/` - TypeScript source files
- `package/tests/` - Test files
- `package/node_modules/` - Dependencies
- `package/.github/` - GitHub workflows
- `package/docs/` - Documentation source files
- `package/examples/` - Example scripts

If you see unexpected files, update `.npmignore` and re-run `npm pack`.

#### Dry-Run Publish Test

Test the publish process without actually publishing:

```bash
npm publish --dry-run
```

This command will:
- Run the `prepublishOnly` script (lint + test + build)
- Show what would be published
- Display warnings or errors
- List all files that would be included

Review the output carefully for:
- Unexpected files in the file list
- Warning messages about package size or dependencies
- Errors in the prepublishOnly checks

#### Publishing to NPM

Once all checks pass, publish the package:

**Standard Release (Latest Tag):**
```bash
npm publish
```

This publishes the package and automatically tags it as `latest`, making it the default version installed via `npm install -g lecoder-cgpu`.

**Beta/Pre-Release:**
```bash
npm publish --tag beta
```

This publishes the package under the `beta` tag. Users must explicitly install it via:
```bash
npm install -g lecoder-cgpu@beta
```

**Scoped Package (Public Access):**
If publishing a scoped package (e.g., `@org/lecoder-cgpu`), add the `--access` flag:
```bash
npm publish --access public
```

#### Post-Publish Verification

After publishing, verify the package is available and working:

1. **Check npm registry:**
   - Visit: `https://www.npmjs.com/package/lecoder-cgpu`
   - Verify the new version appears
   - Check that README and metadata are correct

2. **Test global installation:**
   ```bash
   # Install the published version
   npm install -g lecoder-cgpu@<version>
   
   # Verify CLI works
   lecoder-cgpu --version
   lecoder-cgpu --help
   
   # Test basic command
   lecoder-cgpu status
   ```

3. **Test in a fresh environment:**
   ```bash
   # Create a test directory
   mkdir /tmp/test-lecoder-cgpu
   cd /tmp/test-lecoder-cgpu
   
   # Install and test
   npm install -g lecoder-cgpu@<version>
   lecoder-cgpu --version
   ```

#### Managing Distribution Tags

npm uses tags to manage different release channels:

**View current tags:**
```bash
npm dist-tag ls lecoder-cgpu
```

**Add a tag to a specific version:**
```bash
# Promote a beta version to latest
npm dist-tag add lecoder-cgpu@0.5.2 latest

# Add a beta tag
npm dist-tag add lecoder-cgpu@0.6.0-beta.1 beta
```

**Remove a tag:**
```bash
npm dist-tag rm lecoder-cgpu beta
```

**Note:** The `latest` tag is automatically applied when you run `npm publish` without `--tag`.

#### Troubleshooting

**"Package size too large" warning:**
- Check `.npmignore` - ensure unnecessary files are excluded
- Remove large binary files, documentation, or examples
- Run `npm pack` and inspect tarball size: `ls -lh lecoder-cgpu-*.tgz`
- Target size should be < 5MB (excluding platform binaries)

**"Authentication failed" error:**
- Run `npm login` and re-authenticate
- Verify 2FA is enabled and working
- Check you have publish permissions: `npm access ls-collaborators lecoder-cgpu`

**"Version already exists" error:**
- npm does not allow overwriting published versions
- Bump the version: `npm version patch` (or `minor`/`major`)
- Cannot unpublish versions older than 24 hours
- If immediate fix needed, publish a patch version

**"prepublishOnly script failed" error:**
- Fix lint errors: `npm run lint`
- Fix failing tests: `npm test`
- Fix build errors: `npm run build`
- Review error output for specific issues

**Package contains wrong files:**
- Update `.npmignore` to exclude unwanted files
- Re-run `npm pack` to verify
- Use `tar -tzf lecoder-cgpu-*.tgz` to inspect
- Remember: `.npmignore` takes precedence over `.gitignore`

**Installation fails for users:**
- Check `package.json` dependencies are correct
- Verify `engines` field specifies correct Node.js version
- Test installation in a clean environment
- Check npm registry status: `https://status.npmjs.org/`

#### Complete Publishing Workflow

For a full release (npm + binaries + GitHub release), follow this sequence:

```bash
# 1. Prepare the release
./scripts/prepare-release.sh 0.5.2

# 2. Review and update CHANGELOG.md
# (manual step)

# 3. Commit release changes
git add .
git commit -m "chore: release v0.5.2"

# 4. Verify npm package locally
npm pack
tar -tzf lecoder-cgpu-0.5.2.tgz | less
rm lecoder-cgpu-0.5.2.tgz

# 5. Dry-run publish
npm publish --dry-run

# 6. Publish to npm
npm publish

# 7. Verify on npm
npm view lecoder-cgpu
npm install -g lecoder-cgpu@0.5.2
lecoder-cgpu --version

# 8. Create and push Git tag
git tag v0.5.2
git push origin main
git push origin v0.5.2

# 9. Create GitHub release
# - Go to https://github.com/aryateja2106/LeCoder-cgpu-CLI/releases/new
# - Select tag v0.5.2
# - Add release notes from CHANGELOG.md
# - Upload binaries from ./binaries/
# - Upload checksum files
# - Publish release
```

See `docs/npm-package-checklist.md` for a detailed verification checklist.

---

## Platform-Specific Binary Instructions

### macOS

#### Prerequisites

**Install Node.js:**

Using Homebrew (recommended):
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Node.js
brew install node@20

# Verify installation
node --version  # Should show v20.x.x
npm --version   # Should show 10.x.x
```

Using official installer:
1. Download from [nodejs.org](https://nodejs.org/)
2. Install the `.pkg` file
3. Restart terminal

#### Install LeCoder cGPU

```bash
# Clone repository
git clone https://github.com/aryateja2106/LeCoder-cgpu-CLI.git
cd LeCoder-cgpu-CLI

# Install and build
npm install
npm run build

# Create global link
sudo npm link

# Verify
lecoder-cgpu --version
```

#### macOS-Specific Notes

- **Apple Silicon (M1/M2/M3)**: Fully supported, native ARM64 builds
- **Permissions**: May need to allow terminal access in System Preferences → Privacy & Security
- **Gatekeeper**: First run might require "Allow" in security settings

---

### Linux

#### Ubuntu/Debian

**Install Node.js:**

```bash
# Update package list
sudo apt update

# Install Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Verify
node --version
npm --version
```

**Install LeCoder cGPU:**

```bash
# Clone repository
git clone https://github.com/aryateja2106/LeCoder-cgpu-CLI.git
cd LeCoder-cgpu-CLI

# Install dependencies
npm install

# Build
npm run build

# Link globally
sudo npm link

# Verify
lecoder-cgpu --version
```

#### Fedora/RHEL/CentOS

**Install Node.js:**

```bash
# Install Node.js 20.x
sudo dnf module enable nodejs:20
sudo dnf install nodejs

# Or using NodeSource repository
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
sudo dnf install nodejs
```

**Install LeCoder cGPU:** (same as Ubuntu above)

#### Arch Linux

```bash
# Install Node.js
sudo pacman -S nodejs npm

# Follow standard installation steps
git clone https://github.com/aryateja2106/LeCoder-cgpu-CLI.git
cd LeCoder-cgpu-CLI
npm install
npm run build
sudo npm link
```

---

### Windows

#### Using WSL2 (Recommended)

WSL2 provides the best experience on Windows.

**1. Install WSL2:**

```powershell
# In PowerShell (Admin)
wsl --install
```

Restart your computer.

**2. Install Ubuntu from Microsoft Store**

**3. Inside WSL2 Ubuntu:**

```bash
# Update system
sudo apt update && sudo apt upgrade

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install LeCoder cGPU
git clone https://github.com/aryateja2106/LeCoder-cgpu-CLI.git
cd LeCoder-cgpu-CLI
npm install
npm run build
sudo npm link

# Verify
lecoder-cgpu --version
```

#### Native Windows (Not Recommended)

If you must use native Windows:

**1. Install Node.js:**
- Download from [nodejs.org](https://nodejs.org/)
- Install the Windows Installer (`.msi`)
- Restart PowerShell/Command Prompt

**2. Install Git:**
- Download from [git-scm.com](https://git-scm.com/)

**3. Install LeCoder cGPU:**

```powershell
# In PowerShell
git clone https://github.com/aryateja2106/LeCoder-cgpu-CLI.git
cd LeCoder-cgpu-CLI
npm install
npm run build
npm link

# Verify
lecoder-cgpu --version
```

**Known Issues on Native Windows:**
- Interactive terminal mode may have display issues
- Path handling differences
- Better to use WSL2

---

## Install from Source

### For Development or Latest Features

```bash
# Clone the repository
git clone https://github.com/aryateja2106/LeCoder-cgpu-CLI.git
cd LeCoder-cgpu-CLI

# Checkout specific version (optional)
git checkout v0.5.0

# Install dependencies
npm install

# Build TypeScript
npm run build

# Run tests (optional)
npm test

# Link globally for CLI access
npm link

# Or run without linking
node dist/src/index.js --help
```

### Development Mode

For contributors and developers:

```bash
# Clone and install
git clone https://github.com/aryateja2106/LeCoder-cgpu-CLI.git
cd LeCoder-cgpu-CLI
npm install

# Watch mode (auto-rebuild on changes)
npm run build -- --watch

# In another terminal, link
npm link

# Make changes and test immediately
lecoder-cgpu --version
```

---

## Verify Installation

After installation, verify everything works:

### 1. Check Version

```bash
lecoder-cgpu --version
# Should output: lecoder-cgpu v0.5.0 (or current version)
```

### 2. Check Help

```bash
lecoder-cgpu --help
# Should show all available commands
```

### 3. Check Node.js

```bash
node --version  # Should be v18.0.0 or higher
npm --version   # Should be 9.0.0 or higher
```

### 4. Test Authentication (Optional)

```bash
lecoder-cgpu status
# Will guide you through OAuth if not authenticated
```

---

## Initial Setup

### First-Time Configuration

1. **Authenticate with Google:**

```bash
lecoder-cgpu connect
```

This will:
- Open your browser for Google OAuth
- Request Colab and Drive permissions
- Save credentials locally
- Create and connect to a runtime

2. **Verify Connection:**

```bash
lecoder-cgpu status
# Should show: ✓ Authenticated as your-email@gmail.com
```

3. **Test GPU Access:**

```bash
lecoder-cgpu run "nvidia-smi"
# Should show GPU information
```

### Configuration Files

LeCoder cGPU stores configuration in:

- **macOS/Linux**: `~/.config/lecoder-cgpu/`
- **Windows**: `%APPDATA%/lecoder-cgpu/`

Structure:
```
~/.config/lecoder-cgpu/
├── credentials/
│   └── session.json        # OAuth credentials
└── state/
    └── history.jsonl       # Execution history
```

---

## Updating

### Update npm Installation (When Published)

```bash
npm update -g lecoder-cgpu
```

### Update from Source

```bash
cd LeCoder-cgpu-CLI

# Pull latest changes
git pull origin main

# Reinstall dependencies
npm install

# Rebuild
npm run build

# Relink if needed
npm link
```

### Check for Updates

```bash
lecoder-cgpu --version
# Compare with latest release on GitHub
```

---

## Uninstalling

### Remove Global Package

```bash
# If installed via npm
npm uninstall -g lecoder-cgpu

# If linked from source
cd LeCoder-cgpu-CLI
npm unlink
```

### Remove Configuration

```bash
# macOS/Linux
rm -rf ~/.config/lecoder-cgpu

# Windows
rmdir /s %APPDATA%\lecoder-cgpu
```

### Remove Source

```bash
# Delete cloned repository
rm -rf LeCoder-cgpu-CLI
```

---

## Troubleshooting

### Installation Issues

#### "npm: command not found"
- Node.js not installed or not in PATH
- Solution: Install Node.js from [nodejs.org](https://nodejs.org/)

#### "Permission denied" during npm link
- Missing sudo privileges
- Solution: Use `sudo npm link` (Linux/macOS)

#### Build errors during "npm install"
- Incompatible Node.js version
- Solution: Install Node.js 18+ (see platform instructions)

#### "Cannot find module" errors
- Dependencies not installed properly
- Solution: Delete `node_modules` and run `npm install` again

```bash
rm -rf node_modules
npm install
```

### Runtime Issues

#### "Authentication failed"
- Google OAuth flow interrupted
- Solution: Clear credentials and re-authenticate

```bash
rm -rf ~/.config/lecoder-cgpu/credentials
lecoder-cgpu connect
```

#### "Cannot connect to runtime"
- Colab API issues or quota limits
- Solution: Check Colab status, wait and retry

#### Command hangs
- Network issues or runtime unresponsive
- Solution: Enable verbose mode

```bash
lecoder-cgpu --verbose run "your command"
```

### Getting Help

If installation fails:

1. Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
2. Search [GitHub Issues](https://github.com/aryateja2106/LeCoder-cgpu-CLI/issues)
3. Open a new issue with:
   - Operating system and version
   - Node.js version (`node --version`)
   - npm version (`npm --version`)
   - Full error output
   - Steps you've tried

---

## Next Steps

After successful installation:

1. ✅ Read the [Quick Start](./README.md#quick-start) guide
2. ✅ Explore [common use cases](./README.md#common-use-cases)
3. ✅ Check the [full command reference](./README.md#commands-reference)
4. ✅ Join [GitHub Discussions](https://github.com/aryateja2106/LeCoder-cgpu-CLI/discussions)

---

**Need Help?** Open an issue or discussion on GitHub!
