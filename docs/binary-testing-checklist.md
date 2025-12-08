# Binary Testing Checklist

Before releasing binaries, manually test on each platform:

## macOS (x64 and arm64)

- [ ] Binary downloads without corruption
- [ ] Binary is executable (`chmod +x` works)
- [ ] `lecoder-cgpu --version` shows correct version
- [ ] `lecoder-cgpu --help` displays help text
- [ ] `lecoder-cgpu auth` triggers OAuth flow
- [ ] OAuth callback works in browser
- [ ] `lecoder-cgpu connect` establishes runtime connection
- [ ] `lecoder-cgpu run "echo test"` executes successfully
- [ ] `lecoder-cgpu status` shows runtime info
- [ ] Config files created in `~/.config/lecoder-cgpu/`
- [ ] No Node.js installation required

## Windows (x64)

- [ ] Binary downloads without corruption
- [ ] `lecoder-cgpu.exe --version` shows correct version
- [ ] `lecoder-cgpu.exe --help` displays help text
- [ ] `lecoder-cgpu.exe auth` triggers OAuth flow
- [ ] OAuth callback works in browser
- [ ] `lecoder-cgpu.exe connect` establishes runtime connection
- [ ] `lecoder-cgpu.exe run "echo test"` executes successfully
- [ ] `lecoder-cgpu.exe status` shows runtime info
- [ ] Config files created in `%APPDATA%\lecoder-cgpu\`
- [ ] No Node.js installation required
- [ ] Works in PowerShell and CMD

## Linux (x64 and arm64)

- [ ] Binary downloads without corruption
- [ ] Binary is executable (`chmod +x` works)
- [ ] `lecoder-cgpu --version` shows correct version
- [ ] `lecoder-cgpu --help` displays help text
- [ ] `lecoder-cgpu auth` triggers OAuth flow
- [ ] OAuth callback works in browser
- [ ] `lecoder-cgpu connect` establishes runtime connection
- [ ] `lecoder-cgpu run "echo test"` executes successfully
- [ ] `lecoder-cgpu status` shows runtime info
- [ ] Config files created in `~/.config/lecoder-cgpu/`
- [ ] No Node.js installation required
- [ ] Works on Ubuntu 20.04+, Debian 11+, RHEL 8+

## Cross-Platform

- [ ] SHA256 checksums match for all binaries
- [ ] Binary sizes are reasonable (50-80MB)
- [ ] No runtime errors or crashes
- [ ] All commands work identically to npm version
- [ ] Documentation is accurate
