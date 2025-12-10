# NPM Package Publishing Checklist

This document provides a comprehensive checklist for publishing the `lecoder-cgpu` package to npm, ensuring quality, security, and consistency across releases.

## ✅ Package Published Successfully

**Version**: 0.5.1  
**Published**: December 8, 2025  
**Package URL**: https://www.npmjs.com/package/lecoder-cgpu  
**Status**: Live and production-ready

### Post-Publication Updates Completed

- ✅ README.md updated with npm badges and installation instructions
- ✅ Main project README updated with npm package link
- ✅ INSTALLATION.md reorganized with npm as primary method
- ✅ LECODER_CGPU_GUIDE.md updated with npm instructions
- ✅ Created GETTING_STARTED.md quick start guide
- ✅ All documentation reflects published package status

---

## Pre-Publish Verification

Complete all checks in this table before publishing:

| Check | Command | Expected Result | Status |
|-------|---------|-----------------|--------|
| **Version updated** | `grep version package.json` | Matches target release version | ☐ |
| **Changelog updated** | `grep "## \[${VERSION}\]" CHANGELOG.md` | Entry exists for new version | ☐ |
| **Tests pass** | `npm test` | All tests green, no failures | ☐ |
| **Build succeeds** | `npm run build` | No errors, `dist/` populated with .js and .d.ts files | ☐ |
| **Lint passes** | `npm run lint` | No TypeScript errors or warnings | ☐ |
| **Binaries built** | `npm run pkg:all` | All platform binaries created in `binaries/` | ☐ |
| **Binaries tested** | `npm run pkg:test` | All binary smoke tests pass | ☐ |
| **Package size** | `npm pack --dry-run` | Total size < 5MB (excluding binaries) | ☐ |
| **Required files included** | `npm pack && tar -tzf lecoder-cgpu-*.tgz` | Contains `package/dist/`, `package/README.md`, `package/LICENSE`, `package/package.json` | ☐ |
| **Source files excluded** | `tar -tzf lecoder-cgpu-*.tgz \| grep -E "src\|tests"` | No matches (returns exit code 1) | ☐ |
| **prepublishOnly hook** | `npm publish --dry-run` | Runs lint → test → build successfully | ☐ |

## Package Content Verification

### Required Files Checklist

Verify these files are present in the npm package tarball:

- [ ] `package/dist/index.js` - Main entry point (compiled)
- [ ] `package/dist/index.d.ts` - TypeScript declarations for main entry
- [ ] `package/dist/config.js` - Configuration module (compiled)
- [ ] `package/dist/config.d.ts` - TypeScript declarations for config
- [ ] `package/dist/**/*.js` - All compiled modules
- [ ] `package/dist/**/*.d.ts` - All TypeScript type definitions
- [ ] `package/package.json` - Package metadata
- [ ] `package/README.md` - User-facing documentation
- [ ] `package/LICENSE` - MIT license file
- [ ] `package/.npmignore` - Exclusion rules

### Excluded Files Checklist

Verify these files/directories are **NOT** in the package:

- [ ] `package/src/` - TypeScript source files
- [ ] `package/tests/` - Test files and test utilities
- [ ] `package/node_modules/` - Dependencies
- [ ] `package/.github/` - GitHub workflows and templates
- [ ] `package/docs/` - Documentation source files
- [ ] `package/examples/` - Example scripts
- [ ] `package/binaries/` - Platform-specific binaries
- [ ] `package/integration-tests/` - Integration test suite
- [ ] `package/scripts/` - Build and development scripts
- [ ] `package/.git/` - Git repository data
- [ ] `package/.env*` - Environment files
- [ ] `package/*.log` - Log files
- [ ] `package/.vscode/` - Editor configuration

### Manual Inspection

```bash
# Create tarball
npm pack

# List all contents
tar -tzf lecoder-cgpu-<version>.tgz

# Check for specific patterns
echo "Checking for source files (should be empty):"
tar -tzf lecoder-cgpu-<version>.tgz | grep "package/src/"

echo "Checking for test files (should be empty):"
tar -tzf lecoder-cgpu-<version>.tgz | grep "package/tests/"

echo "Checking for node_modules (should be empty):"
tar -tzf lecoder-cgpu-<version>.tgz | grep "package/node_modules/"

echo "Verifying dist/ contents (should show files):"
tar -tzf lecoder-cgpu-<version>.tgz | grep "package/dist/"

# Clean up
rm lecoder-cgpu-<version>.tgz
```

## Publishing Steps

### 1. Dry-Run Publish

- [ ] Run: `npm publish --dry-run`
- [ ] Review file list in output
- [ ] Check for warnings about package size
- [ ] Verify no sensitive files listed
- [ ] Confirm version number is correct

### 2. Actual Publish

Choose the appropriate command:

**Standard Release (Latest):**
```bash
npm publish
```
- [ ] Command executed without errors
- [ ] npm registry confirmation received

**Beta Release:**
```bash
npm publish --tag beta
```
- [ ] Command executed without errors
- [ ] Beta tag applied successfully

**Scoped Package (If Applicable):**
```bash
npm publish --access public
```
- [ ] Package published as public
- [ ] Accessible without authentication

## Post-Publish Verification

### npm Registry Checks

- [ ] Package visible at `https://www.npmjs.com/package/lecoder-cgpu`
- [ ] New version number displayed correctly
- [ ] README rendered properly on package page
- [ ] Download count increasing
- [ ] License displayed correctly (MIT)
- [ ] Repository link works
- [ ] Keywords visible and relevant

### Installation Tests

**Global Installation:**
```bash
# Install published version
npm install -g lecoder-cgpu@<version>

# Verify installation
which lecoder-cgpu        # Should show path to binary
lecoder-cgpu --version    # Should show correct version
lecoder-cgpu --help       # Should display help text
```

- [ ] Global install succeeds
- [ ] CLI executable found in PATH
- [ ] Version matches published version
- [ ] Help text displays correctly

**Local Installation:**
```bash
# Create test project
mkdir /tmp/test-lecoder-cgpu
cd /tmp/test-lecoder-cgpu
npm init -y

# Install as dependency
npm install lecoder-cgpu@<version>

# Verify
node -e "const lc = require('lecoder-cgpu'); console.log('Loaded successfully');"
```

- [ ] Local install succeeds
- [ ] Package loads without errors
- [ ] TypeScript types available (if applicable)

**Fresh Environment Test:**
```bash
# In a new terminal or Docker container
docker run -it node:18 bash

# Inside container
npm install -g lecoder-cgpu@<version>
lecoder-cgpu --version
lecoder-cgpu --help
```

- [ ] Install works in clean environment
- [ ] No unexpected dependencies required
- [ ] CLI executable works and shows help

> **⚠️ Docker OAuth Limitation:** The OAuth flow requires a loopback server on `127.0.0.1` to receive the callback. Inside Docker containers, this won't work because the browser runs on the host but the callback server runs inside the container.
>
> **For container/CI environments, copy BOTH config.json and session.json:**
>
> ```bash
> # Get config path (macOS uses ~/Library/Preferences/, Linux uses ~/.config/)
> CONFIG_DIR=~/Library/Preferences/lecoder-cgpu  # macOS
> # CONFIG_DIR=~/.config/lecoder-cgpu            # Linux
>
> # Full Docker test with authentication:
> CONFIG_JSON=$(cat $CONFIG_DIR/config.json)
> SESSION_JSON=$(cat $CONFIG_DIR/state/session.json)
>
> docker run --rm node:18 bash -c "
>   npm install -g lecoder-cgpu@<version> &&
>   mkdir -p ~/.config/lecoder-cgpu/state &&
>   echo '$CONFIG_JSON' > ~/.config/lecoder-cgpu/config.json &&
>   echo '$SESSION_JSON' > ~/.config/lecoder-cgpu/state/session.json &&
>   chmod 600 ~/.config/lecoder-cgpu/state/session.json &&
>   lecoder-cgpu status --json
> "
> ```

### Functional Tests

Test core commands to ensure the published package works:

- [ ] `lecoder-cgpu status` - Shows connection status
- [ ] `lecoder-cgpu connect` - Initiates OAuth flow (or shows auth prompt)
- [ ] `lecoder-cgpu sessions list` - Lists available sessions (after auth)
- [ ] `lecoder-cgpu auth-export --json` - Exports session token for containers/CI
- [ ] `lecoder-cgpu auth-import` - Imports session token (test with `--help`)
- [ ] `lecoder-cgpu --help` - Displays full help text

### OAuth Setup Verification (5-Step Wizard)

The first run of `lecoder-cgpu status` triggers the OAuth credential setup wizard. Verify each step works correctly:

| Step | Task | URL | Verification |
|------|------|-----|--------------|
| 1 | Create Google Cloud project | https://console.cloud.google.com/ | Project visible in project selector |
| 2 | Create Desktop OAuth client | https://console.cloud.google.com/auth/clients | Client ID and secret displayed |
| 3 | Add test user | https://console.cloud.google.com/auth/audience | Your email listed under Test Users |
| 4 | Enable Google Drive API | https://console.cloud.google.com/apis/library/drive.googleapis.com | API shows as "Enabled" |
| 5 | Paste credentials | N/A | Credentials saved to `~/.config/lecoder-cgpu/config.json` |

**Post-Setup Auth Flow:**
- [ ] OAuth URL opens in browser (or displays URL for manual opening)
- [ ] Google consent screen shows correct scopes (Colaboratory, Drive)
- [ ] Callback to `127.0.0.1:<port>/callback` succeeds
- [ ] Session stored in `~/.config/lecoder-cgpu/state/session.json`
- [ ] Subsequent `lecoder-cgpu status` works without re-auth

## Distribution Tag Management

### Verify Current Tags

```bash
npm dist-tag ls lecoder-cgpu
```

Expected output:
```
latest: <version>
beta: <beta-version> (if applicable)
```

- [ ] `latest` tag points to stable version
- [ ] `beta` tag correct (if beta releases exist)
- [ ] No unexpected tags

### Update Tags (If Needed)

**Promote Beta to Latest:**
```bash
npm dist-tag add lecoder-cgpu@<version> latest
```

**Add Beta Tag:**
```bash
npm dist-tag add lecoder-cgpu@<version> beta
```

**Remove Tag:**
```bash
npm dist-tag rm lecoder-cgpu beta
```

## Rollback Procedures

If issues are discovered after publishing:

### Option 1: Deprecate Version

```bash
npm deprecate lecoder-cgpu@<version> "Reason for deprecation"
```

- [ ] Deprecation message set
- [ ] Users warned on install
- [ ] Alternative version recommended

### Option 2: Publish Patch Fix

**Cannot unpublish versions older than 24 hours**, so publish a fix:

```bash
# Bump to patch version
npm version patch

# Fix the issue in code
# ... make changes ...

# Publish patch
npm publish
```

- [ ] Patch version published
- [ ] Original version deprecated
- [ ] Users notified of fix

### Option 3: Unpublish (Within 24 Hours Only)

**Use with extreme caution** - only for critical security issues within 24 hours of publish:

```bash
npm unpublish lecoder-cgpu@<version>
```

- [ ] Version unpublished
- [ ] Fixed version published immediately
- [ ] Communication sent to users (if needed)

## Post-Release Tasks

### Documentation

- [ ] Update installation instructions if needed
- [ ] Add release notes to GitHub
- [ ] Update CHANGELOG.md with final date
- [ ] Announce on relevant channels

### Git Repository

- [ ] Create Git tag: `git tag v<version>`
- [ ] Push tag: `git push origin v<version>`
- [ ] Push commits: `git push origin main`
- [ ] Create GitHub release with binaries

### Monitoring

- [ ] Watch npm download stats
- [ ] Monitor GitHub issues for install problems
- [ ] Check for error reports
- [ ] Verify no security vulnerabilities reported

## Troubleshooting

### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| **Authentication failed** | Not logged in or 2FA issue | Run `npm login`, verify 2FA codes |
| **Version already exists** | Version not bumped | Bump version with `npm version patch/minor/major` |
| **Package too large** | Unnecessary files included | Update `.npmignore`, verify with `npm pack` |
| **prepublishOnly fails** | Code issues | Fix lint/test/build errors shown in output |
| **Missing files in package** | `.npmignore` too aggressive | Adjust `.npmignore`, ensure required files included |
| **Type definitions missing** | Build incomplete | Run `npm run build`, verify `dist/*.d.ts` files exist |
| **Install fails for users** | Dependency issue or Node version | Check `package.json` dependencies and `engines` field |
| **CLI not executable** | `bin` field incorrect | Verify `package.json` `bin` field points to correct entry point |

## Automation Recommendations

Consider automating the publishing process with:

- **GitHub Actions**: Publish on tag push
- **Semantic Release**: Automatic version bumping and changelog
- **Changesets**: Multi-package versioning (if workspace grows)

Example GitHub Action workflow:
```yaml
name: Publish to npm
on:
  push:
    tags:
      - 'v*'
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
          registry-url: 'https://registry.npmjs.org'
      - run: npm ci
      - run: npm test
      - run: npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

## Checklist Summary

Before marking the release complete, ensure:

- [ ] All pre-publish checks passed
- [ ] Package published successfully
- [ ] Installation tested in multiple environments
- [ ] Functional tests passed
- [ ] Git tag created and pushed
- [ ] GitHub release published with binaries
- [ ] Documentation updated
- [ ] No critical issues reported within 24 hours

## References

- [npm publish documentation](https://docs.npmjs.com/cli/v9/commands/npm-publish)
- [npm dist-tag documentation](https://docs.npmjs.com/cli/v9/commands/npm-dist-tag)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [INSTALLATION.md - Publishing Guide](../INSTALLATION.md#publishing-to-npm-maintainers-only)
