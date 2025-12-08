# Testing Guide

Complete guide to running and writing tests for LeCoder cGPU CLI.

## Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Mock Infrastructure](#mock-infrastructure)
- [Coverage Goals](#coverage-goals)
- [CI Integration](#ci-integration)

---

## Overview

LeCoder cGPU uses [Vitest](https://vitest.dev/) as the testing framework with the following test categories:

| Category | Purpose | Location | Run Time |
|----------|---------|----------|----------|
| **Unit** | Test individual modules in isolation | `tests/unit/` | Fast (~10s) |
| **Integration** | Test CLI commands end-to-end | `tests/integration/` | Medium (~30s) |
| **E2E** | Test complete user workflows | `tests/e2e/` | Slower (~60s) |
| **Performance** | Benchmark critical paths | `tests/performance/` | Variable |

---

## Test Structure

```
tests/
├── mocks/                    # Mock implementations
│   ├── mock-jupyter-kernel.ts
│   ├── mock-colab-client.ts
│   └── mock-drive-client.ts
├── unit/                     # Unit tests
│   ├── session-manager.test.ts
│   ├── colab-connection.test.ts
│   ├── connection-pool.test.ts
│   ├── runtime-manager.test.ts
│   ├── error-handler.test.ts
│   └── remote-command-runner.test.ts
├── integration/              # Integration tests
│   ├── run-command.test.ts
│   ├── connect-command.test.ts
│   ├── sessions-command.test.ts
│   └── logs-command.test.ts
├── e2e/                      # End-to-end tests
│   ├── full-workflow.test.ts
│   └── error-scenarios.test.ts
└── performance/              # Performance benchmarks
    └── connection-benchmark.test.ts
```

---

## Running Tests

### Prerequisites

```bash
# Install dependencies
npm install

# Build the project
npm run build
```

### Run All Tests

```bash
# Run entire test suite
npm test

# Run with verbose output
npm test -- --reporter=verbose
```

### Run by Category

```bash
# Unit tests only (fastest)
npm run test:unit

# Integration tests
npm run test:integration

# E2E tests
npm run test:e2e

# Performance benchmarks
npm run test:perf
```

### Run Specific Files

```bash
# Single test file
npx vitest tests/unit/session-manager.test.ts

# Pattern matching
npx vitest session

# Specific test by name
npx vitest -t "should enforce tier limits"
```

### Watch Mode

```bash
# Re-run on file changes
npm test -- --watch

# Watch specific files
npx vitest --watch tests/unit/
```

### Coverage Report

```bash
# Generate coverage report
npm run test:coverage

# View HTML report
open coverage/index.html
```

---

## Writing Tests

### Test File Naming

- Unit tests: `<module-name>.test.ts`
- Integration tests: `<command-name>.test.ts` or `<feature-name>.test.ts`
- E2E tests: `<workflow-name>.test.ts`

### Basic Test Structure

```typescript
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

describe('ModuleName', () => {
    beforeEach(() => {
        // Setup before each test
    });

    afterEach(() => {
        // Cleanup after each test
        vi.clearAllMocks();
    });

    describe('methodName', () => {
        it('should do expected behavior', () => {
            // Arrange
            const input = 'test';
            
            // Act
            const result = module.method(input);
            
            // Assert
            expect(result).toBe('expected');
        });

        it('should handle edge case', () => {
            expect(() => module.method(null)).toThrow();
        });
    });
});
```

### Testing Async Code

```typescript
describe('AsyncModule', () => {
    it('should resolve successfully', async () => {
        const result = await asyncFunction();
        expect(result).toBeDefined();
    });

    it('should reject on error', async () => {
        await expect(asyncFunction('bad')).rejects.toThrow('Error message');
    });

    it('should timeout correctly', async () => {
        const promise = slowFunction();
        await expect(promise).rejects.toThrow('Timeout');
    }, 10000); // Extended timeout for this test
});
```

### Mocking Dependencies

```typescript
import { vi } from 'vitest';
import { ColabClient } from '../src/colab/client';

// Mock entire module
vi.mock('../src/colab/client');

describe('RuntimeManager', () => {
    it('should create runtime', async () => {
        // Setup mock
        const mockCreate = vi.fn().mockResolvedValue({ id: 'runtime-1' });
        vi.mocked(ColabClient).mockImplementation(() => ({
            createRuntime: mockCreate,
        } as any));

        // Test
        const manager = new RuntimeManager(new ColabClient());
        await manager.create('T4');

        // Verify
        expect(mockCreate).toHaveBeenCalledWith({ gpu: 'T4' });
    });
});
```

### Testing CLI Commands

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { runCommand } from '../src/commands/run';

describe('run command', () => {
    beforeEach(() => {
        // Mock the session/connection
        vi.mock('../src/session/manager', () => ({
            SessionManager: vi.fn().mockImplementation(() => ({
                getActiveSession: vi.fn().mockResolvedValue({
                    id: 'session-1',
                    execute: vi.fn().mockResolvedValue({
                        success: true,
                        result: '2',
                    }),
                }),
            })),
        }));
    });

    it('should execute code in kernel mode', async () => {
        const result = await runCommand('1 + 1', { kernel: true });
        
        expect(result.success).toBe(true);
        expect(result.result).toBe('2');
    });

    it('should format JSON output', async () => {
        const result = await runCommand('1 + 1', { kernel: true, json: true });
        
        expect(() => JSON.parse(result)).not.toThrow();
    });
});
```

### Testing Error Handling

```typescript
describe('Error handling', () => {
    it('should categorize syntax errors', () => {
        const error = new Error('SyntaxError: invalid syntax');
        const categorized = categorizeError(error);
        
        expect(categorized.code).toBe(1201);
        expect(categorized.category).toBe('syntax');
        expect(categorized.recoverable).toBe(false);
    });

    it('should suggest recovery for transient errors', () => {
        const error = new Error('Connection reset');
        const categorized = categorizeError(error);
        
        expect(categorized.recoverable).toBe(true);
        expect(categorized.suggestion).toContain('retry');
    });
});
```

---

## Mock Infrastructure

### MockJupyterKernel

Simulates a Jupyter kernel for testing without network calls:

```typescript
import { MockJupyterKernel } from '../mocks/mock-jupyter-kernel';

describe('Kernel execution', () => {
    let kernel: MockJupyterKernel;

    beforeEach(async () => {
        kernel = new MockJupyterKernel();
        await kernel.start();
    });

    afterEach(async () => {
        await kernel.stop();
    });

    it('should execute code', async () => {
        const result = await kernel.execute('1 + 1');
        expect(result.data['text/plain']).toBe('2');
    });

    it('should simulate errors', async () => {
        kernel.setNextError(new Error('MemoryError'));
        await expect(kernel.execute('x')).rejects.toThrow('MemoryError');
    });
});
```

### MockColabClient

Mocks Colab API responses:

```typescript
import { MockColabClient } from '../mocks/mock-colab-client';

describe('Runtime management', () => {
    const client = new MockColabClient();

    it('should list kernels', async () => {
        const kernels = await client.listKernels('notebook-1');
        expect(kernels).toHaveLength(1);
    });

    it('should simulate quota exceeded', async () => {
        client.setQuotaExceeded(true);
        await expect(client.createRuntime()).rejects.toThrow('quota');
    });
});
```

### MockDriveClient

Mocks Google Drive API:

```typescript
import { MockDriveClient } from '../mocks/mock-drive-client';

describe('File operations', () => {
    const drive = new MockDriveClient();

    beforeEach(() => {
        drive.reset();
        drive.addFile({ id: 'file-1', name: 'test.ipynb' });
    });

    it('should list files', async () => {
        const files = await drive.listFiles();
        expect(files).toContainEqual(expect.objectContaining({ name: 'test.ipynb' }));
    });
});
```

---

## Coverage Goals

### Target Coverage

| Metric | Target | Current |
|--------|--------|---------|
| Line Coverage | ≥80% | - |
| Branch Coverage | ≥75% | - |
| Function Coverage | ≥85% | - |
| Statement Coverage | ≥80% | - |

### Critical Paths (100% Coverage Required)

- Authentication flow (`src/auth/`)
- Error handling (`src/core/error-handler.ts`)
- Session management (`src/session/`)
- Connection state machine (`src/jupyter/colab-connection.ts`)

### Coverage Commands

```bash
# Generate coverage report
npm run test:coverage

# Check coverage thresholds
npm run test:ci

# View coverage by file
npx vitest --coverage --reporter=verbose
```

### Vitest Coverage Configuration

```typescript
// vitest.config.ts
export default defineConfig({
    test: {
        coverage: {
            provider: 'v8',
            reporter: ['text', 'html', 'lcov'],
            exclude: [
                'node_modules/',
                'tests/',
                '**/*.d.ts',
            ],
            thresholds: {
                lines: 80,
                branches: 75,
                functions: 85,
                statements: 80,
            },
        },
    },
});
```

---

## CI Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run linter
        run: npm run lint
      
      - name: Run unit tests
        run: npm run test:unit
      
      - name: Run integration tests
        run: npm run test:integration
      
      - name: Run E2E tests
        run: npm run test:e2e
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: coverage/lcov.info
```

### Pre-commit Hook

```bash
#!/bin/bash
# scripts/pre-commit.sh

echo "Running tests..."
npm run test:unit

if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi

echo "Tests passed!"
```

### Local CI Simulation

```bash
# Run the same tests as CI
npm run test:ci

# This runs:
# 1. Lint check
# 2. Type check
# 3. Unit tests with coverage
# 4. Integration tests
# 5. Coverage threshold check
```

---

## Best Practices

### DO

✅ Write tests before fixing bugs (TDD for regressions)  
✅ Use descriptive test names that explain the scenario  
✅ Test edge cases and error conditions  
✅ Mock external dependencies (network, filesystem)  
✅ Clean up resources in `afterEach`  
✅ Use `vi.useFakeTimers()` for time-dependent tests  

### DON'T

❌ Test implementation details (test behavior, not internals)  
❌ Write flaky tests that depend on timing  
❌ Skip tests without documenting why  
❌ Commit with failing tests  
❌ Mock too much (test real integration when possible)  

### Test Isolation

```typescript
describe('Session tests', () => {
    let originalEnv: NodeJS.ProcessEnv;

    beforeEach(() => {
        // Save environment
        originalEnv = { ...process.env };
        // Set test environment
        process.env.LECODER_CONFIG_DIR = '/tmp/test-config';
    });

    afterEach(() => {
        // Restore environment
        process.env = originalEnv;
        // Clean up files
        fs.rmSync('/tmp/test-config', { recursive: true, force: true });
    });
});
```

### Debugging Tests

```bash
# Run with debugger
node --inspect-brk node_modules/.bin/vitest tests/unit/session-manager.test.ts

# Verbose output
npx vitest --reporter=verbose

# Run single test
npx vitest -t "specific test name"
```

---

## Troubleshooting Tests

### Test Timeout

```typescript
// Increase timeout for slow tests
it('should handle slow operation', async () => {
    // ...
}, 30000); // 30 second timeout
```

### Mock Not Working

```typescript
// Ensure mock is defined before import
vi.mock('../src/module'); // Must be hoisted

import { Module } from '../src/module'; // Import after mock
```

### Async Cleanup Issues

```typescript
afterEach(async () => {
    // Wait for all pending operations
    await new Promise(resolve => setTimeout(resolve, 100));
    vi.clearAllMocks();
});
```

---

For more information, see the [Vitest documentation](https://vitest.dev/).
