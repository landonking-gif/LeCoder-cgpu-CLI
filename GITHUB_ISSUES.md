# GitHub Issues to Create

These issues were identified during testing. Create them in the GitHub repository.

---

## Issue 1: Auth login doesn't allow switching to different Google account ✅ FIXED

**Title:** `[Bug] Cannot login with different Google account - OAuth flow reuses cached session`

**Labels:** `bug`, `auth`, `priority: medium`

**Status:** ✅ FIXED - Added `--select-account` flag to force account picker

**Description:**

### Problem
When running `lecoder-cgpu auth login` while already authenticated, users cannot easily login with a different Google account. The flow prompts "Re-authenticate?" but doesn't provide a clear way to switch accounts.

### Current Behavior
```
$ lecoder-cgpu auth login
Currently authenticated as User A <usera@gmail.com>
Re-authenticate? This will clear your current session. (y/N): N
Authentication cancelled.
```

Even when answering "Y", the browser OAuth flow may auto-select the previously used account.

### Expected Behavior
- Provide explicit option to login with a different account (e.g., `--switch-account` flag)
- Clear browser OAuth hint/login_hint to allow account selection
- Document the workflow for switching accounts

### Proposed Solution
1. Add `--switch-account` or `--new-account` flag to `auth login`
2. When this flag is used, pass `prompt: "select_account"` to the OAuth URL instead of `prompt: "consent"`
3. Optionally clear any login hints

### Affected Files
- `src/auth/oauth-manager.ts` (line 88-96)
- `src/index.ts` (auth command)

---

## Issue 2: Logout command doesn't fully clear cached state ✅ FIXED

**Title:** `[Bug] logout command doesn't clear all cached credentials - wizard flow cannot be re-tested`

**Labels:** `bug`, `auth`, `priority: high`

**Status:** ✅ FIXED - Added `--all` flag to remove ALL configuration

**Description:**

### Problem
After running `lecoder-cgpu logout`, the tool retains OAuth app credentials (client ID/secret) in `config.json`. Users cannot test the first-time setup wizard without manually deleting files.

### Current Behavior
```bash
$ lecoder-cgpu logout
Signed out and cleared session cache.

# But config.json still exists with client ID/secret
$ ls ~/.config/lecoder-cgpu/
config.json  state/
```

### Expected Behavior
Provide options to:
1. Clear session only (current behavior)
2. Clear everything including OAuth app config (`--all` flag)
3. Document what files are stored and how to fully reset

### Proposed Solution
1. Add `--all` or `--reset` flag to `logout` command
2. When used, also delete `config.json`
3. Add confirmation prompt before deleting everything
4. Update help text to document storage locations

### Affected Files
- `src/index.ts` (logout command, lines 771-780)

---

## Issue 3: Config file lacks restrictive permissions ✅ FIXED

**Title:** `[Security] config.json should have 0o600 permissions like session.json`

**Labels:** `security`, `enhancement`, `priority: medium`

**Status:** ✅ FIXED - Config file now written with 0o600 permissions

**Description:**

### Problem
The session file (`session.json`) correctly uses `0o600` permissions to protect the refresh token, but `config.json` (which contains the OAuth client secret) is written with default permissions.

### Current Code
```typescript
// session-storage.ts - CORRECT ✅
await fs.writeFile(this.sessionFile, JSON.stringify(session, null, 2), { 
  encoding: "utf-8", 
  mode: 0o600 
});

// config.ts - MISSING PERMISSIONS ⚠️
await fs.writeFile(targetPath, JSON.stringify(parsed, null, 2) + "\n", "utf-8");
```

### Expected Behavior
Config file should also use `0o600` permissions since it contains the client secret.

### Proposed Solution
```typescript
// In config.ts writeConfigFile()
await fs.writeFile(targetPath, JSON.stringify(parsed, null, 2) + "\n", {
  encoding: "utf-8",
  mode: 0o600
});
await fs.chmod(targetPath, 0o600);
```

### Affected Files
- `src/config.ts` (line 120-121)

---

## Issue 4: Drive API may require separate credentials for some accounts

**Title:** `[Enhancement] Support separate Drive API credentials for accounts with different OAuth clients`

**Labels:** `enhancement`, `auth`, `priority: low`

**Description:**

### Problem
Some Google accounts may have Drive API enabled under a different project/OAuth client than the one used for Colab access. Currently, the tool uses a single set of OAuth credentials for all APIs.

### Context
When enabling Drive API, Google Cloud Console creates a new OAuth client, giving users a different client ID. The current tool doesn't support using different credentials for Drive operations.

### Expected Behavior
For most users, a single OAuth client with both Colab and Drive scopes should work. However, we should:
1. Document this clearly in the setup wizard
2. Provide better error messages when Drive API fails due to credential mismatch
3. Consider future support for separate Drive credentials if needed

### Proposed Solution
1. Update setup wizard to emphasize enabling Drive API in the SAME project
2. Improve error handling for Drive API 403 errors to suggest credential configuration
3. Document the single-project requirement in installation guide

### Affected Files
- `src/config.ts` (wizard)
- `GETTING_STARTED.md`
- `INSTALLATION.md`

---

## Issue 5: Browser OAuth may auto-select previous account ✅ FIXED

**Title:** `[Enhancement] Allow forcing account selection in OAuth flow`

**Labels:** `enhancement`, `ux`, `priority: medium`

**Status:** ✅ FIXED - Added `--select-account` flag to `auth` command

---

## Issue 6: Kernel mode session management selects wrong runtime

**Title:** `[Bug] Kernel mode may connect to wrong runtime with stale kernel`

**Labels:** `bug`, `kernel`, `priority: medium`

**Description:**

### Problem
When using `lecoder-cgpu run -m kernel`, the tool may connect to a runtime with a kernel stuck in "starting" state instead of one with an "idle" kernel, causing WebSocket 404 errors.

### Observed Behavior
```
Kernel ID: 4fc0d952-...
Kernel verified, status: starting
Unhandled kernel client error: Unexpected server response: 404
```

Meanwhile, another runtime has an idle kernel that would work:
```json
{
  "endpoint": "gpu-a100-s-28tprldzv5avn",
  "kernel": {"state": "idle"}
}
```

### Root Cause
The session manager doesn't check kernel state when selecting a runtime. It may select a session whose kernel is stuck in "starting" state.

### Proposed Solution
1. When selecting a session for kernel mode, check if the kernel is in an actionable state
2. If kernel is stuck in "starting" for too long, try another session or create a new one
3. Add kernel state validation to session selection logic

### Workaround
Use terminal mode which doesn't require kernel WebSocket:
```bash
lecoder-cgpu run 'python3 -c "print(\"hello\")"'
```

### Affected Files
- `src/session/session-manager.ts`
- `src/runtime/runtime-manager.ts`
- `src/jupyter/colab-connection.ts`

