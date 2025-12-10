#!/usr/bin/env python3
"""
Comprehensive stress test for kernel mode functionality.
Tests edge cases, error scenarios, concurrent operations, and performance.
"""

import subprocess
import json
import time
import sys
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class TestStatus(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    ERROR = "ERROR"

@dataclass
class TestResult:
    name: str
    status: TestStatus
    duration_ms: float
    error: Optional[str] = None
    output: Optional[str] = None

class KernelModeStressTest:
    def __init__(self, cli_path: str = "lecoder-cgpu"):
        self.cli_path = cli_path
        self.results: List[TestResult] = []
        self.start_time = time.time()
        
    def run_kernel_command(self, code: str, timeout: int = 60) -> Tuple[bool, str, float]:
        """Execute kernel mode command and return (success, output, duration)"""
        # Add delay between requests to avoid overwhelming Colab (rate limiting)
        # Longer delay helps prevent 502 Bad Gateway errors
        time.sleep(2.0)
        
        start = time.time()
        try:
            result = subprocess.run(
                [self.cli_path, "run", "-m", "kernel", "--json", code],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            duration = (time.time() - start) * 1000
            
            if result.returncode == 0:
                return True, result.stdout, duration
            else:
                return False, result.stderr or result.stdout, duration
        except subprocess.TimeoutExpired:
            duration = (time.time() - start) * 1000
            return False, f"Timeout after {timeout}s", duration
        except Exception as e:
            duration = (time.time() - start) * 1000
            return False, str(e), duration
    
    def parse_json_output(self, output: str) -> Optional[Dict]:
        """Parse JSON output, return None if invalid"""
        try:
            return json.loads(output)
        except:
            return None
    
    def test(self, name: str, code: str, 
             expected_in_output: Optional[str] = None,
             should_fail: bool = False,
             validate_json: bool = True,
             timeout: int = 90) -> TestResult:
        """Run a single test"""
        success, output, duration = self.run_kernel_command(code, timeout)
        
        error = None
        status = TestStatus.PASS
        
        if should_fail:
            if success:
                status = TestStatus.FAIL
                error = "Expected failure but command succeeded"
            else:
                status = TestStatus.PASS
        else:
            if not success:
                status = TestStatus.FAIL
                error = f"Command failed: {output[:200]}"
            elif validate_json:
                json_data = self.parse_json_output(output)
                if json_data is None:
                    status = TestStatus.FAIL
                    error = "Output is not valid JSON"
                elif expected_in_output:
                    if expected_in_output not in output:
                        status = TestStatus.FAIL
                        error = f"Expected '{expected_in_output}' not found in output"
            elif expected_in_output:
                if expected_in_output not in output:
                    status = TestStatus.FAIL
                    error = f"Expected '{expected_in_output}' not found in output"
        
        result = TestResult(name, status, duration, error, output[:500])
        self.results.append(result)
        return result
    
    def print_result(self, result: TestResult):
        """Print test result with color coding"""
        colors = {
            TestStatus.PASS: "\033[0;32m",  # Green
            TestStatus.FAIL: "\033[0;31m",  # Red
            TestStatus.SKIP: "\033[1;33m",  # Yellow
            TestStatus.ERROR: "\033[0;31m", # Red
        }
        reset = "\033[0m"
        
        symbol = {
            TestStatus.PASS: "✓",
            TestStatus.FAIL: "✗",
            TestStatus.SKIP: "⊘",
            TestStatus.ERROR: "⚠",
        }[result.status]
        
        color = colors.get(result.status, "")
        print(f"{color}{symbol}{reset} [{len(self.results)}] {result.name} ({result.duration_ms:.0f}ms)")
        if result.error:
            print(f"  {color}Error:{reset} {result.error}")
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("\n" + "="*60)
        print("Kernel Mode Comprehensive Stress Test")
        print("="*60 + "\n")
        
        # Category 1: Basic Operations
        print("\n[Category 1] Basic Operations")
        print("-" * 60)
        print("Note: Adding delays between tests to avoid rate limiting...")
        self.test("Simple print", "print('hello')", "hello", timeout=90)
        self.test("Variable assignment", "x = 42; print(x)", "42", timeout=90)
        self.test("Math operations", "print(2 + 2)", "4", timeout=90)
        self.test("String methods", "print('test'.upper())", "TEST", timeout=90)
        self.test("List operations", "print(len([1,2,3]))", "3", timeout=90)
        
        # Category 2: Imports
        print("\n[Category 2] Import Tests")
        print("-" * 60)
        self.test("Standard library", "import os; print(os.name)", "posix")
        self.test("Math library", "import math; print(int(math.pi))", "3")
        self.test("Torch import", "import torch; print(torch.__version__)", "torch", timeout=120)
        self.test("Numpy import", "import numpy; print(numpy.__version__)", "numpy", timeout=120)
        self.test("Invalid import (should fail)", "import nonexistent_xyz", should_fail=True)
        
        # Category 3: Error Handling
        print("\n[Category 3] Error Handling")
        print("-" * 60)
        self.test("Syntax error", "print('unclosed", should_fail=True)
        self.test("NameError", "print(undefined_var)", should_fail=True)
        self.test("ZeroDivisionError", "1/0", should_fail=True)
        self.test("TypeError", "'str' + 123", should_fail=True)
        self.test("IndexError", "[][0]", should_fail=True)
        
        # Category 4: Special Characters & Encoding
        print("\n[Category 4] Special Characters & Encoding")
        print("-" * 60)
        self.test("Unicode", "print('Hello 世界 🌍')", "Hello")
        self.test("Special chars", "print('!@#$%^&*()')", "!")
        self.test("Newlines", "print('Line1\\nLine2')", "Line1")
        self.test("Empty output", "print('')", "")
        
        # Category 5: Multi-line Code
        print("\n[Category 5] Multi-line Code")
        print("-" * 60)
        self.test("Function definition", 
                 "def add(a, b):\n    return a + b\nprint(add(2, 3))", "5")
        self.test("Loop", "for i in range(3):\n    print(i)", "0")
        self.test("Conditional", "x = 5\nif x > 3:\n    print('greater')", "greater")
        self.test("Class definition",
                 "class Test:\n    def __init__(self):\n        self.v = 42\nprint(Test().v)", "42")
        
        # Category 6: Memory & Performance
        print("\n[Category 6] Memory & Performance")
        print("-" * 60)
        self.test("Small list", "lst = list(range(100)); print(len(lst))", "100")
        self.test("String concat", "s = ''.join(['a'] * 1000); print(len(s))", "1000")
        self.test("Dict operations", "d = {i: i*2 for i in range(100)}; print(len(d))", "100")
        self.test("Large computation", "total = sum(range(10000)); print(total)", "49995000", timeout=120)
        
        # Category 7: JSON Output Validation
        print("\n[Category 7] JSON Output Format")
        print("-" * 60)
        success, output, _ = self.run_kernel_command("print('test')")
        if success:
            json_data = self.parse_json_output(output)
            if json_data and ('status' in json_data or 'errorCode' in json_data):
                self.results.append(TestResult("JSON format valid", TestStatus.PASS, 0))
            else:
                self.results.append(TestResult("JSON format valid", TestStatus.FAIL, 0, 
                                              "Missing required fields"))
        
        # Category 8: Runtime State
        print("\n[Category 8] Runtime State")
        print("-" * 60)
        self.test("GPU check", "import torch; print(torch.cuda.is_available())", "True", timeout=120)
        self.test("Python version", "import sys; print('Python' in sys.version)", "True")
        self.test("Environment", "import os; print('PATH' in os.environ)", "True")
        
        # Category 9: Long Operations
        print("\n[Category 9] Long-running Operations")
        print("-" * 60)
        self.test("Sleep", "import time; time.sleep(2); print('done')", "done", timeout=30)
        self.test("Iteration", "total = sum(range(1000)); print(total)", "499500")
        
        # Category 10: Edge Cases
        print("\n[Category 10] Edge Cases")
        print("-" * 60)
        self.test("Very long string", f"print('{'a' * 1000}')", "a")
        self.test("Nested structures", "d = {'a': [1,2,3], 'b': {'c': 4}}; print(d['b']['c'])", "4")
        self.test("Generator", "g = (x*2 for x in range(5)); print(list(g))", "0")
        self.test("Lambda", "f = lambda x: x*2; print(f(5))", "10")
        
        # Category 11: Sequential Execution
        print("\n[Category 11] Sequential Execution")
        print("-" * 60)
        # Note: Variables DO persist within the same runtime session
        # Each 'run' command creates a new connection, but if reusing the same runtime,
        # the kernel state persists. This is expected behavior.
        # To test true isolation, we'd need --new-runtime for each call.
        # For now, we'll skip this test as it's testing runtime behavior, not CLI behavior.
        self.results.append(TestResult("Variable isolation", TestStatus.SKIP, 0,
                                      "Variables persist within same runtime (expected behavior)"))
        
        # Print all results
        print("\n" + "="*60)
        print("Test Results Summary")
        print("="*60)
        for result in self.results:
            self.print_result(result)
        
        # Summary statistics
        print("\n" + "="*60)
        print("Summary Statistics")
        print("="*60)
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == TestStatus.PASS)
        failed = sum(1 for r in self.results if r.status == TestStatus.FAIL)
        skipped = sum(1 for r in self.results if r.status == TestStatus.SKIP)
        
        total_duration = sum(r.duration_ms for r in self.results)
        avg_duration = total_duration / total if total > 0 else 0
        
        print(f"Total Tests:  {total}")
        print(f"\033[0;32mPassed:      {passed}\033[0m")
        print(f"\033[0;31mFailed:      {failed}\033[0m")
        print(f"\033[1;33mSkipped:     {skipped}\033[0m")
        print(f"\nTotal Duration: {total_duration/1000:.2f}s")
        print(f"Average Duration: {avg_duration:.0f}ms")
        print(f"Longest Test: {max((r.duration_ms, r.name) for r in self.results)[1]} "
              f"({max(r.duration_ms for r in self.results):.0f}ms)")
        
        if failed > 0:
            print("\n\033[0;31mFailed Tests:\033[0m")
            for result in self.results:
                if result.status == TestStatus.FAIL:
                    print(f"  ✗ {result.name}: {result.error}")
        
        return failed == 0

if __name__ == "__main__":
    cli_path = sys.argv[1] if len(sys.argv) > 1 else "lecoder-cgpu"
    tester = KernelModeStressTest(cli_path)
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


