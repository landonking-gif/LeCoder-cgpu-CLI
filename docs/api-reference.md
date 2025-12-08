# API Reference

Complete reference for LeCoder cGPU CLI commands, JSON schemas, error codes, and integration patterns.

## Table of Contents

- [Command Reference](#command-reference)
- [JSON Output Schemas](#json-output-schemas)
- [Error Codes](#error-codes)
- [Exit Codes](#exit-codes)
- [Environment Variables](#environment-variables)
- [Configuration Files](#configuration-files)
- [Integration Patterns](#integration-patterns)

---

## Command Reference

### Global Options

These options are available for all commands:

| Option | Alias | Description |
|--------|-------|-------------|
| `--verbose` | `-v` | Enable verbose logging |
| `--json` | | Output results as JSON |
| `--help` | `-h` | Display help information |
| `--version` | `-V` | Display version number |

### Authentication Commands

#### `lecoder-cgpu auth login`

Authenticate with Google OAuth.

```bash
lecoder-cgpu auth login [options]
```

**Options:**
| Option | Description |
|--------|-------------|
| `--headless` | Use device code flow (for SSH/remote) |

**Example:**
```bash
# Interactive login
lecoder-cgpu auth login

# Headless login for SSH sessions
lecoder-cgpu auth login --headless
```

#### `lecoder-cgpu auth logout`

Clear stored authentication tokens.

```bash
lecoder-cgpu auth logout
```

#### `lecoder-cgpu auth status`

Check current authentication status.

```bash
lecoder-cgpu auth status
```

**Output:**
```
✓ Authenticated as user@example.com
  Token expires: 2024-12-15T10:30:00Z
```

---

### Connection Commands

#### `lecoder-cgpu connect`

Connect to a Colab runtime.

```bash
lecoder-cgpu connect [options]
```

**Options:**
| Option | Alias | Default | Description |
|--------|-------|---------|-------------|
| `--gpu` | `-g` | `T4` | GPU type: `T4`, `V100`, `A100`, `L4` |
| `--tpu` | | | Use TPU instead of GPU |
| `--cpu` | | | Use CPU-only runtime |
| `--name` | `-n` | auto | Session name for identification |
| `--new-runtime` | | false | Force new runtime creation |
| `--timeout` | `-t` | `60` | Connection timeout in seconds |

**Examples:**
```bash
# Connect with default T4 GPU
lecoder-cgpu connect

# Connect with A100 GPU
lecoder-cgpu connect --gpu A100

# Named session
lecoder-cgpu connect --gpu T4 --name training-session

# CPU-only for light workloads
lecoder-cgpu connect --cpu
```

#### `lecoder-cgpu disconnect`

Disconnect from current runtime.

```bash
lecoder-cgpu disconnect [options]
```

**Options:**
| Option | Description |
|--------|-------------|
| `--keep-runtime` | Don't terminate the runtime |
| `--all` | Disconnect all sessions |

#### `lecoder-cgpu status`

Show connection and runtime status.

```bash
lecoder-cgpu status [--json]
```

**JSON Output:**
```json
{
  "authenticated": true,
  "connected": true,
  "runtime": {
    "id": "abc123",
    "gpu": "T4",
    "uptime": "1h 23m",
    "memoryUsed": "8.2GB",
    "memoryTotal": "15GB"
  },
  "session": {
    "id": "session-1",
    "name": "default",
    "createdAt": "2024-12-14T10:00:00Z"
  }
}
```

---

### Execution Commands

#### `lecoder-cgpu run`

Execute code on the remote runtime.

```bash
lecoder-cgpu run [options] <code>
```

**Options:**
| Option | Alias | Default | Description |
|--------|-------|---------|-------------|
| `--kernel` | `-k` | false | Use Jupyter kernel mode |
| `--timeout` | `-t` | `300` | Execution timeout (seconds) |
| `--json` | | false | Output as JSON |
| `--file` | `-f` | | Run code from file |
| `--quiet` | `-q` | false | Suppress stdout |

**Examples:**
```bash
# Terminal mode (shell command)
lecoder-cgpu run "nvidia-smi"

# Kernel mode (Python code)
lecoder-cgpu run --kernel "import torch; print(torch.cuda.is_available())"

# Run from file
lecoder-cgpu run --kernel --file train.py

# JSON output for scripting
lecoder-cgpu run --kernel --json "1 + 1"

# Long-running with extended timeout
lecoder-cgpu run --kernel --timeout 3600 "train_model()"
```

**JSON Output Schema:**
```json
{
  "success": true,
  "result": "2",
  "stdout": "",
  "stderr": "",
  "executionTime": 0.023,
  "exitCode": 0
}
```

#### `lecoder-cgpu kernel`

Kernel management commands.

```bash
lecoder-cgpu kernel <subcommand>
```

**Subcommands:**
| Command | Description |
|---------|-------------|
| `status` | Show kernel status |
| `restart` | Restart the kernel |
| `interrupt` | Interrupt current execution |

---

### Session Commands

#### `lecoder-cgpu sessions list`

List all active sessions.

```bash
lecoder-cgpu sessions list [--json]
```

**JSON Output:**
```json
{
  "sessions": [
    {
      "id": "session-1",
      "name": "training",
      "gpu": "T4",
      "status": "connected",
      "createdAt": "2024-12-14T10:00:00Z",
      "lastActivity": "2024-12-14T11:30:00Z"
    }
  ],
  "tier": "pro",
  "limit": 5,
  "used": 1
}
```

#### `lecoder-cgpu sessions switch`

Switch to a different session.

```bash
lecoder-cgpu sessions switch <session-id>
```

#### `lecoder-cgpu sessions close`

Close a session.

```bash
lecoder-cgpu sessions close <session-id> [options]
```

**Options:**
| Option | Description |
|--------|-------------|
| `--force` | Force close even if stale |
| `--all` | Close all sessions |

---

### File Transfer Commands

#### `lecoder-cgpu upload`

Upload file to runtime.

```bash
lecoder-cgpu upload <local-path> [remote-path]
```

**Examples:**
```bash
# Upload to current directory
lecoder-cgpu upload model.pt

# Upload to specific path
lecoder-cgpu upload data.csv /content/data/
```

#### `lecoder-cgpu download`

Download file from runtime.

```bash
lecoder-cgpu download <remote-path> [local-path]
```

---

### History Commands

#### `lecoder-cgpu logs`

View execution history.

```bash
lecoder-cgpu logs [options]
```

**Options:**
| Option | Alias | Default | Description |
|--------|-------|---------|-------------|
| `--limit` | `-n` | `50` | Number of entries |
| `--since` | | | Filter by date (ISO format) |
| `--status` | | | Filter: `success`, `error` |
| `--json` | | false | Output as JSON |

#### `lecoder-cgpu logs stats`

Show execution statistics.

```bash
lecoder-cgpu logs stats [--json]
```

**JSON Output:**
```json
{
  "totalExecutions": 156,
  "successRate": 0.94,
  "averageExecutionTime": 2.3,
  "byStatus": {
    "success": 147,
    "error": 9
  }
}
```

#### `lecoder-cgpu logs clear`

Clear execution history.

```bash
lecoder-cgpu logs clear [--confirm]
```

---

## JSON Output Schemas

### Standard Response

All `--json` outputs follow this pattern:

```typescript
interface CommandResponse {
  success: boolean;
  data?: any;           // Command-specific data
  error?: {
    code: number;
    message: string;
    details?: string;
  };
  timing?: {
    startedAt: string;  // ISO timestamp
    completedAt: string;
    duration: number;   // milliseconds
  };
}
```

### Execution Response

```typescript
interface ExecutionResponse {
  success: boolean;
  result: string | null;    // Return value (kernel mode)
  stdout: string;
  stderr: string;
  executionTime: number;    // seconds
  exitCode: number;         // 0 = success
  error?: {
    code: number;
    message: string;
    traceback?: string;
  };
}
```

### Session Response

```typescript
interface SessionResponse {
  id: string;
  name: string;
  status: 'connected' | 'disconnected' | 'stale';
  runtime: {
    id: string;
    type: 'gpu' | 'tpu' | 'cpu';
    variant?: string;       // 'T4', 'V100', etc.
    createdAt: string;
  };
  kernel?: {
    id: string;
    status: 'idle' | 'busy' | 'dead';
  };
}
```

---

## Error Codes

### Authentication Errors (1001-1099)

| Code | Message | Recovery |
|------|---------|----------|
| 1001 | Not authenticated | Run `lecoder-cgpu auth login` |
| 1002 | Token expired | Re-authenticate |
| 1003 | Invalid credentials | Check OAuth flow |
| 1004 | Insufficient scopes | Re-authenticate with correct scopes |

### Connection Errors (1101-1199)

| Code | Message | Recovery |
|------|---------|----------|
| 1101 | Connection timeout | Retry or check network |
| 1102 | Runtime unavailable | Try different GPU type |
| 1103 | WebSocket error | Reconnect |
| 1104 | Session limit reached | Close unused sessions |
| 1105 | Runtime terminated | Reconnect |

### Execution Errors (1201-1299)

| Code | Message | Recovery |
|------|---------|----------|
| 1201 | Syntax error | Fix code syntax |
| 1202 | Runtime error | Debug code logic |
| 1203 | Execution timeout | Increase timeout or optimize |
| 1204 | Memory exhausted | Reduce memory usage |
| 1205 | Import error | Install missing packages |
| 1206 | I/O error | Check file paths |
| 1207 | Kernel died | Restart kernel |

### File Transfer Errors (1301-1399)

| Code | Message | Recovery |
|------|---------|----------|
| 1301 | File not found | Check path |
| 1302 | Permission denied | Check permissions |
| 1303 | Transfer failed | Retry |
| 1304 | File too large | Compress or use Drive |

### API Errors (1401-1499)

| Code | Message | Recovery |
|------|---------|----------|
| 1401 | Rate limited | Wait and retry |
| 1402 | API unavailable | Check Colab status |
| 1403 | Invalid request | Check parameters |
| 1404 | Forbidden | Check permissions |

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | Authentication required |
| 4 | Connection failed |
| 5 | Execution failed |
| 6 | Timeout |
| 130 | Interrupted (Ctrl+C) |

---

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `LECODER_CONFIG_DIR` | Config directory | `~/.config/lecoder-cgpu` |
| `LECODER_REFRESH_TOKEN` | OAuth refresh token (CI) | `1//0abc...` |
| `LECODER_LOG_LEVEL` | Log verbosity | `debug`, `info`, `warn`, `error` |
| `LECODER_TIMEOUT` | Default timeout | `300` |
| `NO_COLOR` | Disable colored output | `1` |

---

## Configuration Files

### Location

| OS | Path |
|----|------|
| macOS | `~/.config/lecoder-cgpu/` |
| Linux | `~/.config/lecoder-cgpu/` |
| Windows | `%APPDATA%\lecoder-cgpu\` |

### Files

| File | Purpose |
|------|---------|
| `tokens.json` | OAuth tokens (encrypted) |
| `config.json` | User preferences |
| `state/sessions.json` | Active sessions |
| `state/history.jsonl` | Execution history |

### config.json Schema

```json
{
  "defaultGpu": "T4",
  "defaultTimeout": 300,
  "maxHistorySize": 1000,
  "autoReconnect": true,
  "verboseLogging": false
}
```

---

## Integration Patterns

### Python Integration

```python
import subprocess
import json

def run_on_colab(code: str, timeout: int = 300) -> dict:
    """Execute code on Colab and return structured result."""
    result = subprocess.run(
        ["lecoder-cgpu", "run", "--kernel", "--json", code],
        capture_output=True,
        text=True,
        timeout=timeout
    )
    return json.loads(result.stdout)

# Example usage
result = run_on_colab("import torch; torch.cuda.is_available()")
if result["success"]:
    print(f"Result: {result['result']}")
else:
    print(f"Error: {result['error']['message']}")
```

### Bash Integration

```bash
#!/bin/bash
# run-training.sh

run_colab() {
    local code="$1"
    local result
    
    result=$(lecoder-cgpu run --kernel --json "$code" 2>/dev/null)
    
    if echo "$result" | jq -e '.success' > /dev/null; then
        echo "$result" | jq -r '.result'
        return 0
    else
        echo "Error: $(echo "$result" | jq -r '.error.message')" >&2
        return 1
    fi
}

# Connect
lecoder-cgpu connect --gpu T4

# Run training
run_colab "train_model(epochs=10)"

# Check GPU memory
run_colab "import torch; torch.cuda.memory_allocated() / 1e9"
```

### Node.js Integration

```javascript
import { execSync } from 'child_process';

function runOnColab(code, options = {}) {
    const { timeout = 300000, kernel = true } = options;
    
    const args = ['lecoder-cgpu', 'run', '--json'];
    if (kernel) args.push('--kernel');
    args.push(code);
    
    try {
        const output = execSync(args.join(' '), {
            timeout,
            encoding: 'utf8'
        });
        return JSON.parse(output);
    } catch (error) {
        return {
            success: false,
            error: { message: error.message }
        };
    }
}

// Example
const result = runOnColab('1 + 1');
console.log(result.result); // "2"
```

### GitHub Actions Integration

```yaml
# .github/workflows/gpu-tests.yml
name: GPU Tests

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup lecoder-cgpu
        run: npm install -g lecoder-cgpu
      
      - name: Authenticate
        env:
          LECODER_REFRESH_TOKEN: ${{ secrets.LECODER_REFRESH_TOKEN }}
        run: lecoder-cgpu auth status
      
      - name: Connect to Colab
        run: lecoder-cgpu connect --gpu T4
      
      - name: Run Tests
        run: |
          lecoder-cgpu upload tests/ /content/tests/
          lecoder-cgpu run --kernel --json "
            import subprocess
            result = subprocess.run(['pytest', '/content/tests/'], capture_output=True)
            print(result.stdout.decode())
            exit(result.returncode)
          "
      
      - name: Cleanup
        if: always()
        run: lecoder-cgpu disconnect
```

### Error Recovery Pattern

```python
import subprocess
import json
import time

def run_with_retry(code: str, max_retries: int = 3) -> dict:
    """Run code with automatic retry on transient failures."""
    transient_errors = {1101, 1103, 1401}  # Connection, WebSocket, Rate limit
    
    for attempt in range(max_retries):
        result = subprocess.run(
            ["lecoder-cgpu", "run", "--kernel", "--json", code],
            capture_output=True,
            text=True
        )
        
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            time.sleep(2 ** attempt)
            continue
        
        if data.get("success"):
            return data
        
        error_code = data.get("error", {}).get("code", 0)
        if error_code not in transient_errors:
            return data  # Non-retryable error
        
        time.sleep(2 ** attempt)
    
    return {"success": False, "error": {"message": "Max retries exceeded"}}
```

---

## Rate Limits

| Operation | Limit | Window |
|-----------|-------|--------|
| `connect` | 10 | per minute |
| `run` | 60 | per minute |
| `upload/download` | 30 | per minute |
| API calls | 100 | per minute |

**Note:** These are approximate and may vary based on Colab tier and usage patterns.

---

## Version History

| Version | Changes |
|---------|---------|
| 0.5.1 | Added multi-session, kernel mode, JSON output |
| 0.5.0 | Initial stable release |

For detailed changelog, see [CHANGELOG.md](../CHANGELOG.md).
