# Docker & Container Testing Guide

This document explains the challenges of testing `lecoder-cgpu` in Docker containers and provides solutions for developers and CI/CD environments.

## The Core Problem

**OAuth authentication cannot work inside Docker containers** due to a fundamental networking limitation:

1. The OAuth flow requires starting a local web server on `127.0.0.1` (loopback interface)
2. After user authentication, Google redirects to `http://127.0.0.1:<port>/callback`
3. In Docker:
   - The web server runs inside the container on its own `127.0.0.1`
   - The browser runs on the host machine on the host's `127.0.0.1`
   - These are **different network interfaces** - they cannot communicate
4. Result: The browser callback fails with "Connection refused" or "ERR_CONNECTION_REFUSED"

### Error Messages You'll See

**In the browser:**
```
This site can't be reached
127.0.0.1 refused to connect.
ERR_CONNECTION_REFUSED
```

**From Google OAuth (if you use a different OAuth client):**
```
Error 400: redirect_uri_mismatch
The redirect URI in the request, http://127.0.0.1:xxxxx/callback, 
does not match the ones authorized for the OAuth client.
```

**From Google (if email not in test users):**
```
Error 403: access_denied
[App Name] has not completed the Google verification process.
The app is currently being tested, and can only be accessed by 
developer-approved testers.
```

## Solutions for Container Testing

### Option 1: Copy Authentication Files (Recommended)

This is the **simplest and most reliable** method for testing in containers.

#### Prerequisites
On your **host machine** (with browser access):
1. Complete the OAuth setup once: `lecoder-cgpu auth`
2. Verify it works: `lecoder-cgpu status`

#### For Docker

**Method A: Direct file copy**
```bash
# On macOS:
docker cp ~/Library/Preferences/lecoder-cgpu container-name:/root/.config/lecoder-cgpu

# On Linux:
docker cp ~/.config/lecoder-cgpu container-name:/root/.config/lecoder-cgpu
```

**Method B: Environment variables in docker run**
```bash
# Get the auth files
CONFIG_JSON=$(cat ~/Library/Preferences/lecoder-cgpu/config.json)  # macOS
SESSION_JSON=$(cat ~/Library/Preferences/lecoder-cgpu/state/session.json)

# Or on Linux:
# CONFIG_JSON=$(cat ~/.config/lecoder-cgpu/config.json)
# SESSION_JSON=$(cat ~/.config/lecoder-cgpu/state/session.json)

# Run container with auth pre-configured
docker run --rm -it node:18 bash -c "
  npm install -g lecoder-cgpu@latest &&
  mkdir -p /root/.config/lecoder-cgpu/state &&
  echo '$CONFIG_JSON' > /root/.config/lecoder-cgpu/config.json &&
  echo '$SESSION_JSON' > /root/.config/lecoder-cgpu/state/session.json &&
  chmod 600 /root/.config/lecoder-cgpu/state/session.json &&
  lecoder-cgpu status --json
"
```

**Method C: Using Docker volumes**
```bash
# On macOS:
docker run --rm -it \
  -v ~/Library/Preferences/lecoder-cgpu:/root/.config/lecoder-cgpu:ro \
  node:18 bash

# On Linux:
docker run --rm -it \
  -v ~/.config/lecoder-cgpu:/root/.config/lecoder-cgpu:ro \
  node:18 bash
```

### Option 2: Use auth-export/auth-import Commands (v0.5.7+)

Starting from version 0.5.7, `lecoder-cgpu` includes dedicated commands for container authentication:

#### On Host Machine
```bash
# Export session token
lecoder-cgpu auth-export --json > session.json

# The output includes both the session and instructions
```

#### In Container
```bash
# Method 1: Import from JSON file
lecoder-cgpu auth-import "$(cat session.json | jq -c '.session')" --force

# Method 2: Pipe directly
cat session.json | jq -c '.session' | lecoder-cgpu auth-import - --force

# Verify
lecoder-cgpu status --json
```

**Important:** You still need to copy `config.json` (OAuth client credentials) to the container. The `auth-import` command only handles the session token.

### Option 3: Port Forwarding (Advanced, Not Recommended)

Theoretically, you could:
1. Publish the container's port: `docker run -p 40119:40119 ...`
2. Configure OAuth redirect URI to use the host's IP
3. Manually handle the callback

**Why we don't recommend this:**
- Requires modifying OAuth client configuration for each test
- Doesn't work in CI/CD without additional infrastructure
- More complex than simply copying files
- Poses security risks (exposing OAuth callbacks)

## Testing Workflows

### For Developers

```bash
#!/bin/bash
# test-lecoder-in-docker.sh

# Get auth from host
if [[ "$OSTYPE" == "darwin"* ]]; then
  CONFIG_PATH=~/Library/Preferences/lecoder-cgpu
else
  CONFIG_PATH=~/.config/lecoder-cgpu
fi

CONFIG_JSON=$(cat $CONFIG_PATH/config.json)
SESSION_JSON=$(cat $CONFIG_PATH/state/session.json)

# Run tests in Docker
docker run --rm node:18 bash -c "
  npm install -g lecoder-cgpu@latest
  mkdir -p /root/.config/lecoder-cgpu/state
  echo '$CONFIG_JSON' > /root/.config/lecoder-cgpu/config.json
  echo '$SESSION_JSON' > /root/.config/lecoder-cgpu/state/session.json
  chmod 600 /root/.config/lecoder-cgpu/state/session.json
  
  # Run your tests
  lecoder-cgpu status --json
  lecoder-cgpu run -m kernel 'import torch; print(torch.cuda.is_available())' --json
"
```

### For CI/CD Pipelines

Store the authentication files as **secrets**:

#### GitHub Actions Example
```yaml
name: Test lecoder-cgpu

on: [push, pull_request]

jobs:
  test-docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up auth files
        env:
          LECODER_CONFIG: ${{ secrets.LECODER_CONFIG_JSON }}
          LECODER_SESSION: ${{ secrets.LECODER_SESSION_JSON }}
        run: |
          mkdir -p ~/.config/lecoder-cgpu/state
          echo "$LECODER_CONFIG" > ~/.config/lecoder-cgpu/config.json
          echo "$LECODER_SESSION" > ~/.config/lecoder-cgpu/state/session.json
          chmod 600 ~/.config/lecoder-cgpu/state/session.json
      
      - name: Test in Docker
        run: |
          docker run --rm \
            -v ~/.config/lecoder-cgpu:/root/.config/lecoder-cgpu:ro \
            node:18 bash -c "
              npm install -g lecoder-cgpu@latest &&
              lecoder-cgpu status --json
            "
```

#### GitLab CI Example
```yaml
test-docker:
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - mkdir -p /root/.config/lecoder-cgpu/state
    - echo "$LECODER_CONFIG" > /root/.config/lecoder-cgpu/config.json
    - echo "$LECODER_SESSION" > /root/.config/lecoder-cgpu/state/session.json
  script:
    - docker run --rm 
        -v /root/.config/lecoder-cgpu:/root/.config/lecoder-cgpu:ro 
        node:18 
        npm install -g lecoder-cgpu && lecoder-cgpu status --json
```

## Container Detection

Starting from version 0.5.7, `lecoder-cgpu` automatically detects when it's running inside a container and displays helpful warnings:

```
⚠️  Warning: Running inside a container (Docker/Kubernetes/etc.)
OAuth login requires browser access and won't work in containers.

To authenticate in containers:
1. On a machine with browser access, run: lecoder-cgpu auth
2. Export session: lecoder-cgpu auth-export --json > session.json
3. Copy both files to the container:
   - config.json (OAuth client credentials)
   - state/session.json (user session token)
4. Or use: lecoder-cgpu auth-import '<session JSON>' --force

Continuing anyway (will likely fail)...
```

### How Detection Works

The tool checks for:
1. `/.dockerenv` file (present in most Docker containers)
2. `/proc/self/cgroup` containing `docker`, `containerd`, or `kubepods`

## Required Files

To successfully use `lecoder-cgpu` in a container, you need **both** files:

| File | Contains | Purpose | Source |
|------|----------|---------|--------|
| `config.json` | OAuth client ID and secret | Google API credentials | Created during setup wizard |
| `state/session.json` | Refresh token | User authentication | Created after OAuth login |

**File locations:**
- macOS: `~/Library/Preferences/lecoder-cgpu/`
- Linux: `~/.config/lecoder-cgpu/`
- Container: `/root/.config/lecoder-cgpu/` (or user's home if not root)

## Security Considerations

### Protecting Sensitive Files

Both `config.json` and `session.json` contain sensitive credentials:

```bash
# Always set restrictive permissions
chmod 600 /root/.config/lecoder-cgpu/config.json
chmod 600 /root/.config/lecoder-cgpu/state/session.json

# Or for the entire directory
chmod -R 700 /root/.config/lecoder-cgpu
```

### CI/CD Best Practices

1. **Never commit auth files to version control**
   ```gitignore
   .config/lecoder-cgpu/
   config.json
   session.json
   ```

2. **Use encrypted secrets** in CI/CD platforms:
   - GitHub Actions: Repository Secrets
   - GitLab CI: CI/CD Variables (masked)
   - Jenkins: Credentials Plugin
   - CircleCI: Environment Variables (encrypted)

3. **Rotate tokens periodically**:
   - Refresh tokens can be revoked at https://myaccount.google.com/permissions
   - Re-run `lecoder-cgpu auth` to generate new tokens

4. **Limit secret access**:
   - Only give CI jobs that need GPU access
   - Use separate Google accounts for CI vs development

## Troubleshooting

### "OAuth login timed out"

```
✗ OAuth login timed out.

This is expected in containers - the browser callback can't reach 127.0.0.1 inside the container.
```

**Solution:** Use file copy method (see Option 1 above).

### "Error 403: access_denied"

```
lesearch has not completed the Google verification process
Error 403: access_denied
```

**Solution:** Add your email as a test user:
1. Visit https://console.cloud.google.com/auth/audience
2. Select your Google Cloud project
3. Click "Add users" under Test Users
4. Add your Google account email
5. Save and retry authentication

### "Missing required fields" when importing session

```
Invalid session JSON: Missing required fields
Expected format: { id, refreshToken, scopes, account: { id, label } }
```

**Solution:** Make sure you're importing the session object, not the wrapper:
```bash
# Wrong:
lecoder-cgpu auth-import "$(cat session.json)"

# Correct:
lecoder-cgpu auth-import "$(cat session.json | jq -c '.session')"
```

### Container can authenticate but commands fail

**Check:**
1. Network connectivity: `docker run --rm node:18 curl -I https://colab.research.google.com`
2. Session validity: `lecoder-cgpu status --json | jq '.authenticated'`
3. Token expiry: Refresh tokens last 6 months, re-authenticate if expired

## Alternative Approaches (Not Implemented)

### Why Not Use Service Accounts?

Google Colab API doesn't support service account authentication. It requires:
- User OAuth consent
- Access to user's Google Drive
- Colab notebook execution context tied to user account

### Why Not Use Remote OAuth Proxy?

Could set up a remote OAuth server, but:
- Adds infrastructure complexity
- Introduces security risks (OAuth tokens in transit)
- Not needed for legitimate use cases
- File copy method is simpler and more secure

## Summary

| Method | Pros | Cons | Recommended For |
|--------|------|------|-----------------|
| **File Copy** | ✅ Simple<br>✅ Secure<br>✅ Works everywhere | ❌ Manual step | Development, CI/CD |
| **auth-import** | ✅ Programmatic<br>✅ Clean API | ❌ Requires version 0.5.7+<br>❌ Still needs config.json | Automation scripts |
| **Volume Mount** | ✅ Easy updates | ❌ Less portable | Local development |
| **Port Forward** | ✅ Mimics host | ❌ Complex<br>❌ Insecure | ❌ Not recommended |

**Best practice:** Use file copy method with encrypted CI/CD secrets for production environments.

## References

- [npm Package Checklist](./npm-package-checklist.md) - Contains Docker testing procedures
- [AGENTS.md](../AGENTS.md) - Container authentication section for AI agents
- [Installation Guide](./installation.md) - Initial setup instructions
