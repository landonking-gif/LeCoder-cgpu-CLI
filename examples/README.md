# Examples

This directory contains example scripts demonstrating advanced usage patterns for LeCoder cGPU CLI.

## Scripts

### multi-session-training.sh

**Purpose**: Demonstrates managing multiple GPU sessions for parallel experiments.

**Features**:
- Creates multiple named sessions with different GPU types
- Runs experiments in parallel across sessions
- Collects and aggregates results
- Proper cleanup of all sessions

**Usage**:
```bash
chmod +x multi-session-training.sh
./multi-session-training.sh
```

**Requirements**:
- Colab Pro (for multiple concurrent sessions)
- `jq` for JSON parsing
- Authenticated with `lecoder-cgpu auth login`

---

### auto-retry.py

**Purpose**: Provides automatic retry with exponential backoff for Colab operations.

**Features**:
- Categorizes errors (transient, resource, code, auth)
- Exponential backoff (1s, 2s, 4s, 8s, ...)
- Configurable max retries and timeouts
- Structured JSON output option

**Usage**:
```bash
# Simple execution
python auto-retry.py "print('Hello!')"

# With retry configuration
python auto-retry.py --max-retries 5 --timeout 600 "train_model()"

# Run from file with verbose output
python auto-retry.py --file train.py --verbose

# JSON output for scripting
python auto-retry.py --json "1 + 1"
```

**Error Categories**:
| Category | Behavior | Examples |
|----------|----------|----------|
| Transient | Retry with backoff | Connection timeout, WebSocket errors |
| Resource | Limited retries | Memory exhausted, session limit |
| Code | No retry | Syntax errors, import errors |
| Auth | No retry | Invalid credentials, expired tokens |

---

### notebook-automation.py

**Purpose**: Automates Colab notebook operations programmatically.

**Features**:
- Connect to Colab with GPU selection
- Create notebooks with cells
- Execute experiments with setup/run/cleanup stages
- Collect structured results with timing

**Usage**:
```bash
# Run the demo (GPU benchmark)
python notebook-automation.py demo --gpu T4

# Run custom experiment
python notebook-automation.py run \
    --name "my-experiment" \
    --setup "import torch" \
    --code "print(torch.cuda.is_available())" \
    --gpu V100

# Run from files
python notebook-automation.py run \
    --setup setup.py \
    --code experiment.py \
    --cleanup cleanup.py \
    --json
```

**Experiment Workflow**:
1. **Connect** - Ensures connection to Colab with specified GPU
2. **Setup** - Runs initialization code (imports, data loading)
3. **Experiment** - Executes main experiment code
4. **Cleanup** - Optional cleanup (memory clearing, etc.)

---

## Integration Examples

### Python Integration

```python
from auto_retry import run_with_retry

result = run_with_retry(
    code="import torch; torch.cuda.is_available()",
    max_retries=3,
    timeout=300
)

if result.success:
    print(f"Result: {result.result}")
else:
    print(f"Error: {result.error_message}")
```

### Bash Integration

```bash
#!/bin/bash
source ./multi-session-training.sh

# Use functions from the script
lecoder-cgpu connect --gpu T4
result=$(lecoder-cgpu run --kernel --json "1+1")
echo "$result" | jq '.result'
```

### CI/CD Pipeline

```yaml
- name: Run GPU Tests
  run: |
    python examples/auto-retry.py \
      --max-retries 3 \
      --timeout 600 \
      --json \
      "$(cat tests/gpu_test.py)" > results.json
    
    if jq -e '.success' results.json; then
      echo "Tests passed!"
    else
      echo "Tests failed: $(jq -r '.error.message' results.json)"
      exit 1
    fi
```

---

## Requirements

All examples require:
- Python 3.8+
- `lecoder-cgpu` installed and in PATH
- Authenticated with Google OAuth (`lecoder-cgpu auth login`)

Optional:
- `jq` for JSON processing in shell scripts
- Colab Pro for multi-session features
