#!/bin/bash
set -e

VERSION=$1

if [ -z "$VERSION" ]; then
  echo "Usage: ./scripts/prepare-release.sh <version>"
  echo "Example: ./scripts/prepare-release.sh 0.5.0"
  exit 1
fi

echo "🚀 Preparing release v$VERSION..."

# Update package.json version
echo "📝 Updating package.json version..."
npm version "$VERSION" --no-git-tag-version

# Run tests
echo "🧪 Running tests..."
npm test

# Build TypeScript
echo "🔨 Building TypeScript..."
npm run build

# Build all binaries
echo "📦 Building binaries for all platforms..."
npm run pkg:all

# Test binaries
echo "🧪 Testing binaries..."
npm run pkg:test

# Test npm package
echo "📦 Testing npm package..."
npm pack
TARBALL="lecoder-cgpu-$VERSION.tgz"

echo "📋 Verifying package contents..."
tar -tzf "$TARBALL" | grep -E "^package/(dist|README|LICENSE|package.json)" > /dev/null
if [ $? -eq 0 ]; then
  echo "✅ Package contains required files"
else
  echo "❌ Package missing required files"
  exit 1
fi

# Check for excluded files
tar -tzf "$TARBALL" | grep -E "^package/(src|tests|node_modules|\.github)" > /dev/null
if [ $? -eq 0 ]; then
  echo "❌ Package contains excluded files (src/tests/node_modules/.github)"
  exit 1
else
  echo "✅ Package excludes source/test files"
fi

echo "📊 Package size:"
ls -lh "$TARBALL"

# Clean up tarball
rm "$TARBALL"

# Generate checksums
echo "🔐 Generating checksums..."
cd binaries
sha256sum lecoder-cgpu-macos-* > checksums-macos.txt
sha256sum lecoder-cgpu-win-*.exe > checksums-windows.txt
sha256sum lecoder-cgpu-linux-* > checksums-linux.txt
cd ..

echo ""
echo "✅ Release v$VERSION prepared successfully!"
echo ""
echo "Next steps:"
echo "1. Review CHANGELOG.md"
echo "2. Commit changes: git add . && git commit -m 'chore: release v$VERSION'"
echo "3. Create tag: git tag v$VERSION"
echo "4. Push: git push && git push --tags"
echo "5. Test npm package: npm pack && tar -tzf lecoder-cgpu-$VERSION.tgz"
echo "6. Publish to npm: npm publish (or npm publish --dry-run first)"
echo "7. Create GitHub release with binaries from ./binaries/"