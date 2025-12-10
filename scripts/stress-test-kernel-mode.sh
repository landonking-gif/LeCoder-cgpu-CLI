#!/bin/bash
# Comprehensive stress test for kernel mode functionality
# Tests various edge cases, error scenarios, and use cases

set -e

CLI="lecoder-cgpu"
TEST_COUNT=0
PASS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test result tracking
declare -a FAILED_TESTS=()
declare -a PASSED_TESTS=()

log_test() {
    local test_name="$1"
    local status="$2"
    local details="$3"
    
    TEST_COUNT=$((TEST_COUNT + 1))
    
    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}✓${NC} [$TEST_COUNT] $test_name"
        PASS_COUNT=$((PASS_COUNT + 1))
        PASSED_TESTS+=("$test_name")
    elif [ "$status" = "FAIL" ]; then
        echo -e "${RED}✗${NC} [$TEST_COUNT] $test_name"
        echo -e "  ${RED}Error:${NC} $details"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        FAILED_TESTS+=("$test_name: $details")
    elif [ "$status" = "SKIP" ]; then
        echo -e "${YELLOW}⊘${NC} [$TEST_COUNT] $test_name (skipped)"
        SKIP_COUNT=$((SKIP_COUNT + 1))
    fi
}

run_kernel_test() {
    local test_name="$1"
    local code="$2"
    local expected_pattern="$3"
    local should_fail="${4:-false}"
    
    local output
    local exit_code=0
    
    output=$($CLI run -m kernel --json "$code" 2>&1) || exit_code=$?
    
    if [ "$should_fail" = "true" ]; then
        if [ $exit_code -ne 0 ]; then
            log_test "$test_name" "PASS" ""
            return 0
        else
            log_test "$test_name" "FAIL" "Expected failure but command succeeded"
            return 1
        fi
    fi
    
    if echo "$output" | grep -q "$expected_pattern"; then
        log_test "$test_name" "PASS" ""
        return 0
    else
        log_test "$test_name" "FAIL" "Output doesn't match expected pattern: $expected_pattern"
        echo "  Actual output: $output"
        return 1
    fi
}

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Kernel Mode Stress Test Suite${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if CLI is available
if ! command -v $CLI &> /dev/null; then
    echo -e "${RED}Error: $CLI not found. Please install it first.${NC}"
    exit 1
fi

echo -e "${BLUE}Starting stress tests...${NC}"
echo ""

# ==========================================
# Category 1: Basic Functionality Tests
# ==========================================
echo -e "${YELLOW}Category 1: Basic Functionality${NC}"

run_kernel_test "Simple print statement" \
    "print('hello world')" \
    "hello world"

run_kernel_test "Variable assignment" \
    "x = 42; print(x)" \
    "42"

run_kernel_test "Math operations" \
    "result = 2 + 2; print(result)" \
    "4"

run_kernel_test "String operations" \
    "s = 'test'; print(s.upper())" \
    "TEST"

run_kernel_test "List operations" \
    "lst = [1, 2, 3]; print(len(lst))" \
    "3"

echo ""

# ==========================================
# Category 2: Import Tests
# ==========================================
echo -e "${YELLOW}Category 2: Import Tests${NC}"

run_kernel_test "Standard library import" \
    "import os; print(os.name)" \
    "posix\|nt"

run_kernel_test "Math library import" \
    "import math; print(math.pi)" \
    "3.14159"

run_kernel_test "Torch import (if available)" \
    "import torch; print(torch.__version__)" \
    "[0-9]\+\.[0-9]\+\.[0-9]\+" || log_test "Torch import" "SKIP" "Torch not available"

run_kernel_test "Numpy import (if available)" \
    "import numpy as np; print(np.__version__)" \
    "[0-9]\+\.[0-9]\+\.[0-9]\+" || log_test "Numpy import" "SKIP" "Numpy not available"

run_kernel_test "Invalid import (should fail)" \
    "import nonexistent_module_xyz123" \
    "" \
    "true"

echo ""

# ==========================================
# Category 3: Error Handling Tests
# ==========================================
echo -e "${YELLOW}Category 3: Error Handling${NC}"

run_kernel_test "Syntax error" \
    "print('unclosed string" \
    "" \
    "true"

run_kernel_test "NameError" \
    "print(undefined_variable)" \
    "" \
    "true"

run_kernel_test "ZeroDivisionError" \
    "1/0" \
    "" \
    "true"

run_kernel_test "TypeError" \
    "'string' + 123" \
    "" \
    "true"

run_kernel_test "IndexError" \
    "lst = []; print(lst[0])" \
    "" \
    "true"

echo ""

# ==========================================
# Category 4: Edge Cases - Special Characters
# ==========================================
echo -e "${YELLOW}Category 4: Special Characters & Encoding${NC}"

run_kernel_test "Unicode characters" \
    "print('Hello 世界 🌍')" \
    "Hello"

run_kernel_test "Special characters in string" \
    "print('Special: !@#\$%^&*()')" \
    "Special"

run_kernel_test "Newlines in output" \
    "print('Line1\\nLine2')" \
    "Line1"

run_kernel_test "Escape sequences" \
    "print('Tab\\tSeparated')" \
    "Tab"

run_kernel_test "Empty string" \
    "print('')" \
    ""

echo ""

# ==========================================
# Category 5: Multi-line Code
# ==========================================
echo -e "${YELLOW}Category 5: Multi-line Code${NC}"

run_kernel_test "Function definition" \
    "def add(a, b):\n    return a + b\nprint(add(2, 3))" \
    "5"

run_kernel_test "Loop" \
    "for i in range(3):\n    print(i)" \
    "0"

run_kernel_test "Conditional" \
    "x = 5\nif x > 3:\n    print('greater')" \
    "greater"

run_kernel_test "Class definition" \
    "class Test:\n    def __init__(self):\n        self.value = 42\nobj = Test()\nprint(obj.value)" \
    "42"

echo ""

# ==========================================
# Category 6: Memory & Performance Tests
# ==========================================
echo -e "${YELLOW}Category 6: Memory & Performance${NC}"

run_kernel_test "Small list creation" \
    "lst = list(range(100)); print(len(lst))" \
    "100"

run_kernel_test "String concatenation" \
    "s = ''.join(['a'] * 1000); print(len(s))" \
    "1000"

run_kernel_test "Dictionary operations" \
    "d = {i: i*2 for i in range(100)}; print(len(d))" \
    "100"

echo ""

# ==========================================
# Category 7: JSON Output Validation
# ==========================================
echo -e "${YELLOW}Category 7: JSON Output Format${NC}"

test_json_output() {
    local test_name="$1"
    local code="$2"
    
    local output
    output=$($CLI run -m kernel --json "$code" 2>&1)
    
    # Check if output is valid JSON
    if echo "$output" | python3 -m json.tool > /dev/null 2>&1; then
        # Check for required fields
        if echo "$output" | python3 -c "import sys, json; d=json.load(sys.stdin); assert 'status' in d or 'errorCode' in d" 2>/dev/null; then
            log_test "$test_name" "PASS" ""
            return 0
        else
            log_test "$test_name" "FAIL" "Missing required JSON fields"
            return 1
        fi
    else
        log_test "$test_name" "FAIL" "Output is not valid JSON"
        return 1
    fi
}

test_json_output "JSON output format (success)" "print('test')"
test_json_output "JSON output format (error)" "1/0" || true

echo ""

# ==========================================
# Category 8: Runtime State Tests
# ==========================================
echo -e "${YELLOW}Category 8: Runtime State Management${NC}"

run_kernel_test "Check GPU availability" \
    "import torch; print(torch.cuda.is_available())" \
    "True\|False" || log_test "GPU check" "SKIP" "Torch not available"

run_kernel_test "System information" \
    "import sys; print(sys.version)" \
    "Python"

run_kernel_test "Environment variables" \
    "import os; print('PATH' in os.environ)" \
    "True"

echo ""

# ==========================================
# Category 9: Long-running Operations
# ==========================================
echo -e "${YELLOW}Category 9: Long-running Operations${NC}"

run_kernel_test "Sleep operation" \
    "import time; time.sleep(1); print('done')" \
    "done"

run_kernel_test "Iteration (1000 iterations)" \
    "total = sum(range(1000)); print(total)" \
    "499500"

echo ""

# ==========================================
# Category 10: Concurrent Execution Tests
# ==========================================
echo -e "${YELLOW}Category 10: Sequential Execution${NC}"

# Test that we can run multiple commands sequentially
test_sequential() {
    local test_name="Sequential execution"
    local result1
    local result2
    
    result1=$($CLI run -m kernel --json "x = 10" 2>&1)
    result2=$($CLI run -m kernel --json "print(x)" 2>&1)
    
    # Variables don't persist between runs (expected behavior)
    if echo "$result2" | grep -q "NameError\|not defined"; then
        log_test "$test_name" "PASS" ""
        return 0
    else
        log_test "$test_name" "FAIL" "Variables persisted between runs unexpectedly"
        return 1
    fi
}

test_sequential

echo ""

# ==========================================
# Summary
# ==========================================
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "Total Tests:  $TEST_COUNT"
echo -e "${GREEN}Passed:      $PASS_COUNT${NC}"
echo -e "${RED}Failed:      $FAIL_COUNT${NC}"
echo -e "${YELLOW}Skipped:     $SKIP_COUNT${NC}"
echo ""

if [ $FAIL_COUNT -gt 0 ]; then
    echo -e "${RED}Failed Tests:${NC}"
    for test in "${FAILED_TESTS[@]}"; do
        echo -e "  ${RED}✗${NC} $test"
    done
    echo ""
    exit 1
else
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
fi


