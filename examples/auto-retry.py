#!/usr/bin/env python3
"""
auto-retry.py - Automatic retry with exponential backoff for Colab operations

This script demonstrates how to:
- Run code on Colab with automatic retry on transient failures
- Handle different error categories appropriately
- Use exponential backoff to avoid rate limiting
- Provide structured error reporting

Usage:
    python auto-retry.py "print('Hello, Colab!')"
    python auto-retry.py --max-retries 5 --timeout 600 "train_model()"
    python auto-retry.py --file train.py
"""

import subprocess
import json
import time
import sys
import argparse
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class ErrorCategory(Enum):
    """Categories of errors for retry decisions."""
    TRANSIENT = "transient"      # Network, connection issues - retry
    RESOURCE = "resource"         # Memory, quota - maybe retry with backoff
    CODE = "code"                 # Syntax, runtime errors - don't retry
    AUTH = "auth"                 # Authentication issues - don't retry
    UNKNOWN = "unknown"           # Unknown errors - cautious retry


# Error codes that are transient and should be retried
TRANSIENT_ERROR_CODES = {
    1101,  # Connection timeout
    1103,  # WebSocket error
    1105,  # Runtime terminated
    1401,  # Rate limited
    1402,  # API unavailable
}

# Error codes that might succeed with backoff
RESOURCE_ERROR_CODES = {
    1104,  # Session limit reached
    1204,  # Memory exhausted
}

# Error codes that should not be retried
NON_RETRYABLE_CODES = {
    1001, 1002, 1003, 1004,  # Auth errors
    1201, 1202, 1205, 1206,  # Code errors
}


@dataclass
class ExecutionResult:
    """Result of a code execution attempt."""
    success: bool
    result: Optional[str] = None
    stdout: str = ""
    stderr: str = ""
    execution_time: float = 0.0
    error_code: Optional[int] = None
    error_message: Optional[str] = None
    attempts: int = 1


def categorize_error(error_code: int) -> ErrorCategory:
    """Categorize an error code for retry decisions."""
    if error_code in TRANSIENT_ERROR_CODES:
        return ErrorCategory.TRANSIENT
    elif error_code in RESOURCE_ERROR_CODES:
        return ErrorCategory.RESOURCE
    elif error_code in NON_RETRYABLE_CODES:
        return ErrorCategory.CODE if error_code >= 1200 else ErrorCategory.AUTH
    else:
        return ErrorCategory.UNKNOWN


def should_retry(error_code: int, attempt: int, max_retries: int) -> bool:
    """Determine if an error should be retried."""
    if attempt >= max_retries:
        return False
    
    category = categorize_error(error_code)
    
    if category == ErrorCategory.TRANSIENT:
        return True
    elif category == ErrorCategory.RESOURCE:
        return attempt < 3  # Limited retries for resource issues
    elif category == ErrorCategory.UNKNOWN:
        return attempt < 2  # Very limited retries for unknown
    else:
        return False


def run_on_colab(
    code: str,
    timeout: int = 300,
    kernel: bool = True,
) -> Dict[str, Any]:
    """Execute code on Colab and return the result."""
    cmd = ["lecoder-cgpu", "run", "--json"]
    if kernel:
        cmd.append("--kernel")
    cmd.extend(["--timeout", str(timeout)])
    cmd.append(code)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout + 30  # Extra buffer for subprocess
        )
        
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": {
                    "code": 0,
                    "message": f"Invalid JSON response: {result.stdout[:200]}"
                },
                "stderr": result.stderr
            }
    
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": {
                "code": 1203,
                "message": "Execution timeout"
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": 0,
                "message": str(e)
            }
        }


def run_with_retry(
    code: str,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    timeout: int = 300,
    kernel: bool = True,
    verbose: bool = False,
) -> ExecutionResult:
    """
    Execute code with automatic retry on transient failures.
    
    Uses exponential backoff: delay = base_delay * 2^attempt
    """
    last_error_code = 0
    last_error_message = ""
    
    for attempt in range(1, max_retries + 1):
        if verbose:
            print(f"Attempt {attempt}/{max_retries}...", file=sys.stderr)
        
        result = run_on_colab(code, timeout=timeout, kernel=kernel)
        
        if result.get("success"):
            return ExecutionResult(
                success=True,
                result=result.get("result"),
                stdout=result.get("stdout", ""),
                stderr=result.get("stderr", ""),
                execution_time=result.get("executionTime", 0),
                attempts=attempt
            )
        
        # Extract error info
        error = result.get("error", {})
        last_error_code = error.get("code", 0)
        last_error_message = error.get("message", "Unknown error")
        
        if verbose:
            category = categorize_error(last_error_code)
            print(
                f"  Error (code={last_error_code}, category={category.value}): "
                f"{last_error_message}",
                file=sys.stderr
            )
        
        # Check if we should retry
        if not should_retry(last_error_code, attempt, max_retries):
            if verbose:
                print(f"  Not retrying (non-retryable error)", file=sys.stderr)
            break
        
        # Calculate backoff delay
        delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
        
        if verbose:
            print(f"  Retrying in {delay:.1f}s...", file=sys.stderr)
        
        time.sleep(delay)
    
    # All retries exhausted
    return ExecutionResult(
        success=False,
        error_code=last_error_code,
        error_message=last_error_message,
        attempts=attempt
    )


def main():
    parser = argparse.ArgumentParser(
        description="Run code on Colab with automatic retry"
    )
    parser.add_argument(
        "code",
        nargs="?",
        help="Python code to execute"
    )
    parser.add_argument(
        "--file", "-f",
        help="Read code from file"
    )
    parser.add_argument(
        "--max-retries", "-r",
        type=int,
        default=3,
        help="Maximum retry attempts (default: 3)"
    )
    parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=300,
        help="Execution timeout in seconds (default: 300)"
    )
    parser.add_argument(
        "--base-delay",
        type=float,
        default=1.0,
        help="Base delay for exponential backoff (default: 1.0)"
    )
    parser.add_argument(
        "--terminal",
        action="store_true",
        help="Use terminal mode instead of kernel mode"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON"
    )
    
    args = parser.parse_args()
    
    # Get code from argument or file
    if args.file:
        with open(args.file, "r") as f:
            code = f.read()
    elif args.code:
        code = args.code
    else:
        parser.error("Either code argument or --file is required")
    
    # Run with retry
    result = run_with_retry(
        code=code,
        max_retries=args.max_retries,
        base_delay=args.base_delay,
        timeout=args.timeout,
        kernel=not args.terminal,
        verbose=args.verbose,
    )
    
    # Output result
    if args.json:
        output = {
            "success": result.success,
            "result": result.result,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "executionTime": result.execution_time,
            "attempts": result.attempts,
        }
        if not result.success:
            output["error"] = {
                "code": result.error_code,
                "message": result.error_message,
            }
        print(json.dumps(output, indent=2))
    else:
        if result.success:
            if result.stdout:
                print(result.stdout)
            if result.result:
                print(f"Result: {result.result}")
            if args.verbose:
                print(
                    f"\nCompleted in {result.execution_time:.2f}s "
                    f"({result.attempts} attempt(s))",
                    file=sys.stderr
                )
        else:
            print(f"Error: {result.error_message}", file=sys.stderr)
            if args.verbose:
                print(
                    f"  Error code: {result.error_code}",
                    file=sys.stderr
                )
                print(
                    f"  Attempts: {result.attempts}",
                    file=sys.stderr
                )
            sys.exit(1)


if __name__ == "__main__":
    main()
