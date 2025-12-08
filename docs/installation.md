# NPM Publishing Guide for Maintainers

This guide provides a focused, end-to-end workflow for publishing `lecoder-cgpu` to the npm registry. For comprehensive installation instructions for users, see the root [`INSTALLATION.md`](../INSTALLATION.md).

## Prerequisites

Before you can publish to npm, ensure you have:

1. **npm Account with Publish Access**
   - Account registered at [npmjs.com](https://www.npmjs.com/)
   - Added as a maintainer to the `lecoder-cgpu` package
   - Verify access: `npm access ls-collaborators lecoder-cgpu`

2. **Two-Factor Authentication (2FA) Enabled**
   - Required for publishing packages
   - Configure at: https://www.npmjs.com/settings/[username]/tfa

3. **Authenticated Locally**
   ```bash
   # Login to npm
   npm login
   
   # Verify you're logged in
   npm whoami
   ```

4. **Clean Working Directory**
   ```bash
   # Ensure all changes are committed
   git status
   
   # No uncommitted changes should appear
   ```

## Enforced Quality Gates

The `lecoder-cgpu` package has a `prepublishOnly` script that automatically runs before every publish:

```json
{
  "scripts": {
    "prepublishOnly": "npm run lint && npm test && npm run build"
  }
}
```

This ensures:
- ✅ **Lint passes**: No TypeScript errors (`npm run lint`)
- ✅ **Tests pass**: All unit, integration, and e2e tests succeed (`npm test`)
- ✅ **Build succeeds**: TypeScript compiles cleanly to `dist/` (`npm run build`)

If any of these checks fail, the publish will abort automatically.

## Recommended Publishing Workflow

### Step 1: Update Version

Bump the version number according to [Semantic Versioning](https://semver.org/):

```bash
# Patch release (0.5.1 → 0.5.2) - Bug fixes
npm version patch

# Minor release (0.5.1 → 0.6.0) - New features, backward compatible
npm version minor

# Major release (0.5.1 → 1.0.0) - Breaking changes
npm version major

# Pre-release (0.5.1 → 0.6.0-beta.0)
npm version preminor --preid=beta
```

The `npm version` command automatically:
- Updates `package.json`
- Creates a git commit
- Creates a git tag

Alternatively, manually edit `package.json` and commit:
```bash
# Edit version in package.json
vim package.json

# Commit the change
git add package.json
git commit -m "chore: bump version to 0.5.2"
```

### Step 2: Update Changelog

Add release notes to `CHANGELOG.md`:

```markdown
## [0.5.2] - 2025-12-08

### Added
- New feature X
- New feature Y

### Fixed
- Bug fix Z

### Changed
- Improvement W
```

Commit the changelog:
```bash
git add CHANGELOG.md
git commit -m "docs: update changelog for v0.5.2"
```

### Step 3: Local Package Verification with `npm pack`

Before publishing, create a local tarball to inspect what will be published:

```bash
# Create tarball (doesn't publish anything)
npm pack
```

This generates a file like `lecoder-cgpu-0.5.2.tgz` in the current directory.

#### Inspect Tarball Contents

**Quick check (first 20 files):**
```bash
tar -tzf lecoder-cgpu-0.5.2.tgz | head -20
```

**Full listing:**
```bash
tar -tzf lecoder-cgpu-0.5.2.tgz | less
```

**Check for specific patterns:**
```bash
# Verify dist/ is included (should show files)
tar -tzf lecoder-cgpu-0.5.2.tgz | grep "package/dist/"

# Verify README, LICENSE, package.json are included
tar -tzf lecoder-cgpu-0.5.2.tgz | grep -E "README|LICENSE|package.json"

# Verify src/ is excluded (should be empty/no output)
tar -tzf lecoder-cgpu-0.5.2.tgz | grep "package/src/"

# Verify tests/ are excluded (should be empty/no output)
tar -tzf lecoder-cgpu-0.5.2.tgz | grep "package/tests/"

# Verify docs/ are excluded (should be empty/no output)
tar -tzf lecoder-cgpu-0.5.2.tgz | grep "package/docs/"
```

#### Tarball Content Checklist

Use this checklist to verify the tarball contents:

**✅ MUST be present:**
- [ ] `package/dist/` - All compiled JavaScript files
- [ ] `package/dist/index.js` - Main entry point
- [ ] `package/dist/**/*.d.ts` - TypeScript type definitions
- [ ] `package/README.md` - User documentation
- [ ] `package/LICENSE` - MIT license file
- [ ] `package/package.json` - Package metadata
- [ ] `package/.npmignore` - Exclusion rules file

**❌ MUST be excluded:**
- [ ] `package/src/` - TypeScript source files
- [ ] `package/tests/` - Test files
- [ ] `package/docs/` - Documentation source
- [ ] `package/examples/` - Example scripts
- [ ] `package/node_modules/` - Dependencies
- [ ] `package/.github/` - GitHub workflows
- [ ] `package/binaries/` - Platform-specific binaries
- [ ] `package/integration-tests/` - Integration tests
- [ ] `package/scripts/` - Build scripts
- [ ] `package/.git/` - Git data
- [ ] `package/*.log` - Log files
- [ ] `package/.env*` - Environment files

#### Clean Up Tarball

After verification, remove the local tarball:
```bash
rm lecoder-cgpu-0.5.2.tgz
```

### Step 4: Dry-Run Publish Test

Test the full publish process without actually publishing:

```bash
npm publish --dry-run
```

This command will:
1. Run the `prepublishOnly` script (lint + test + build)
2. Package the files
3. Show what would be published
4. Display any warnings or errors
5. **NOT** actually publish to npm

Review the output for:
- ✅ All quality gates pass (lint, test, build)
- ✅ File list matches expectations from Step 3
- ✅ Package size is reasonable (< 5MB excluding binaries)
- ✅ No warnings about missing files or bad configuration
- ❌ No unexpected files in the package

**Example output:**
```
npm notice 
npm notice 📦  lecoder-cgpu@0.5.2
npm notice === Tarball Contents === 
npm notice 1.2kB  package.json
npm notice 11.4kB README.md
npm notice 1.1kB  LICENSE
npm notice 145B   dist/index.js
npm notice 89B    dist/index.d.ts
npm notice ... (more dist/ files)
npm notice === Tarball Details === 
npm notice name:          lecoder-cgpu                            
npm notice version:       0.5.2                                   
npm notice filename:      lecoder-cgpu-0.5.2.tgz                  
npm notice package size:  3.2 MB                                  
npm notice unpacked size: 8.1 MB                                  
npm notice shasum:        a1b2c3d4e5f6...                         
npm notice integrity:     sha512-...                             
npm notice total files:   127                                     
npm notice 
+ lecoder-cgpu@0.5.2
```

### Step 5: Publish to NPM

Once all verifications pass, publish the package:

**Standard release (applies `latest` tag):**
```bash
npm publish
```

**Beta/pre-release (applies `beta` tag):**
```bash
npm publish --tag beta
```

Users can then install the beta version with:
```bash
npm install -g lecoder-cgpu@beta
```

**Scoped package (if applicable):**
```bash
npm publish --access public
```

### Step 6: Post-Publish Verification

After publishing, verify the package is available and functional:

#### 1. Check npm Registry

Visit the package page:
```
https://www.npmjs.com/package/lecoder-cgpu
```

Verify:
- [ ] New version number appears
- [ ] README renders correctly
- [ ] License shows as MIT
- [ ] Repository link works
- [ ] Download count is incrementing

#### 2. Test Global Installation

Install the published version globally:
```bash
# Install specific version
npm install -g lecoder-cgpu@0.5.2

# Verify installation
which lecoder-cgpu
# Expected: /usr/local/bin/lecoder-cgpu (or similar)

# Check version
lecoder-cgpu --version
# Expected: 0.5.2

# Display help
lecoder-cgpu --help
# Should show all available commands

# Test authentication status
lecoder-cgpu status
# Should show connection status (may require auth)
```

#### 3. Test in Fresh Environment

Test in a clean environment (e.g., Docker container):
```bash
# Start a fresh Node.js container
docker run -it node:18 bash

# Inside the container
npm install -g lecoder-cgpu@0.5.2
lecoder-cgpu --version
lecoder-cgpu --help
```

#### 4. Test Local Installation

Test as a local dependency in a project:
```bash
# Create test project
mkdir /tmp/test-lecoder-cgpu
cd /tmp/test-lecoder-cgpu
npm init -y

# Install as dependency
npm install lecoder-cgpu@0.5.2

# Verify
node -e "const lc = require('lecoder-cgpu'); console.log('Loaded successfully');"
```

### Step 7: Create Git Tag and Push

If you manually updated the version (didn't use `npm version`), create and push the tag:

```bash
# Create tag
git tag v0.5.2

# Push commits
git push origin main

# Push tag
git push origin v0.5.2
```

### Step 8: Create GitHub Release

1. Go to: https://github.com/aryateja2106/LeCoder-cgpu-CLI/releases/new
2. Select tag: `v0.5.2`
3. Set release title: `v0.5.2`
4. Copy release notes from `CHANGELOG.md`
5. Upload platform-specific binaries from `./binaries/`:
   - `lecoder-cgpu-macos-x64`
   - `lecoder-cgpu-macos-arm64`
   - `lecoder-cgpu-win-x64.exe`
   - `lecoder-cgpu-linux-x64`
   - `lecoder-cgpu-linux-arm64`
   - Checksum files: `checksums-*.txt`
6. Click "Publish release"

## Automated Workflow with `prepare-release.sh`

The project includes a script to automate most preparation steps:

```bash
./scripts/prepare-release.sh 0.5.2
```

This script automatically:
1. Updates `package.json` version
2. Runs tests (`npm test`)
3. Builds TypeScript (`npm run build`)
4. Builds all platform binaries (`npm run pkg:all`)
5. Tests binaries (`npm run pkg:test`)
6. **Creates and verifies npm tarball** (`npm pack` + content checks)
7. Generates checksum files

After running the script:
1. Review and update `CHANGELOG.md`
2. Commit changes: `git add . && git commit -m "chore: release v0.5.2"`
3. Create tag: `git tag v0.5.2`
4. Push: `git push && git push --tags`
5. Run `npm publish --dry-run` to verify
6. Run `npm publish` to publish
7. Create GitHub release with binaries

## Managing Distribution Tags

npm uses tags to manage different release channels.

**View current tags:**
```bash
npm dist-tag ls lecoder-cgpu
```

**Add a tag:**
```bash
# Promote beta to latest
npm dist-tag add lecoder-cgpu@0.5.2 latest

# Add beta tag
npm dist-tag add lecoder-cgpu@0.6.0-beta.1 beta
```

**Remove a tag:**
```bash
npm dist-tag rm lecoder-cgpu beta
```

## Troubleshooting

### Authentication Failed

**Problem:** `npm publish` fails with authentication error.

**Solutions:**
```bash
# Re-login
npm login

# Verify login
npm whoami

# Check 2FA is working
# Visit: https://www.npmjs.com/settings/[username]/tfa
```

### Version Already Exists

**Problem:** `npm ERR! You cannot publish over the previously published versions`

**Solution:** npm doesn't allow overwriting published versions. Bump the version:
```bash
npm version patch
```

### Package Too Large

**Problem:** Warning about package size > 5MB.

**Solutions:**
```bash
# Check what's being included
npm pack
tar -tzf lecoder-cgpu-*.tgz | wc -l
tar -tzf lecoder-cgpu-*.tgz | less

# Update .npmignore to exclude large files
echo "binaries/" >> .npmignore
echo "docs/" >> .npmignore

# Verify exclusions
npm pack
ls -lh lecoder-cgpu-*.tgz
```

### prepublishOnly Script Fails

**Problem:** Publish aborts due to failing quality gates.

**Solutions:**
```bash
# Fix lint errors
npm run lint

# Fix test failures
npm test

# Fix build errors
npm run build

# Review specific error messages in output
```

### Wrong Files in Package

**Problem:** Tarball contains `src/`, `tests/`, or other unwanted files.

**Solution:** Update `.npmignore`:
```bash
# View current .npmignore
cat .npmignore

# Add exclusions
echo "src/" >> .npmignore
echo "tests/" >> .npmignore
echo "docs/" >> .npmignore

# Verify
npm pack
tar -tzf lecoder-cgpu-*.tgz | grep "package/src/"  # Should be empty
```

### Missing Files in Package

**Problem:** Required files (e.g., `dist/`) not in tarball.

**Solution:** `.npmignore` takes precedence over `.gitignore`. Ensure required files aren't excluded:
```bash
# Check .npmignore
cat .npmignore

# Remove overly broad exclusions
# Make sure "dist/" is NOT in .npmignore

# Rebuild and verify
npm run build
npm pack
tar -tzf lecoder-cgpu-*.tgz | grep "package/dist/"  # Should show files
```

## Additional Resources

- **Detailed Checklist**: See [`docs/npm-package-checklist.md`](./npm-package-checklist.md)
- **User Installation Guide**: See root [`INSTALLATION.md`](../INSTALLATION.md)
- **npm Publish Documentation**: https://docs.npmjs.com/cli/v9/commands/npm-publish
- **Semantic Versioning**: https://semver.org/
- **npm dist-tag**: https://docs.npmjs.com/cli/v9/commands/npm-dist-tag

## Quick Reference

```bash
# Complete publishing workflow
npm version patch                      # Bump version
# (Edit CHANGELOG.md)
git add . && git commit -m "chore: release v0.5.2"
npm pack                               # Create tarball
tar -tzf lecoder-cgpu-*.tgz | less    # Inspect contents
rm lecoder-cgpu-*.tgz                 # Clean up
npm publish --dry-run                  # Test publish
npm publish                            # Actually publish
npm view lecoder-cgpu                 # Verify on registry
npm install -g lecoder-cgpu@0.5.2     # Test install
git tag v0.5.2                        # Create tag
git push && git push --tags           # Push to GitHub
# Create GitHub release with binaries
```
