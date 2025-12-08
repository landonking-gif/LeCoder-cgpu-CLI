#!/usr/bin/env python3
"""
notebook-automation.py - Automate Colab notebook operations

This script demonstrates how to:
- Connect to Colab programmatically
- Create and manage notebooks
- Execute cells and collect outputs
- Handle errors and cleanup

Usage:
    python notebook-automation.py --create "My Experiment"
    python notebook-automation.py --run notebook_id
    python notebook-automation.py --export notebook_id output.ipynb
"""

import subprocess
import json
import sys
import argparse
import time
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class NotebookCell:
    """Represents a notebook cell."""
    cell_type: str  # 'code' or 'markdown'
    source: str
    outputs: Optional[List[Dict]] = None
    execution_count: Optional[int] = None


@dataclass
class Notebook:
    """Represents a Colab notebook."""
    id: str
    name: str
    cells: List[NotebookCell]


def run_command(args: List[str], json_output: bool = False) -> Dict[str, Any]:
    """Run a lecoder-cgpu command and return the result."""
    cmd = ["lecoder-cgpu"] + args
    if json_output:
        cmd.append("--json")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if json_output:
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": {"message": f"Invalid JSON: {result.stdout[:200]}"},
                "stderr": result.stderr
            }
    else:
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }


def ensure_connected(gpu: str = "T4") -> bool:
    """Ensure we're connected to a Colab runtime."""
    status = run_command(["status"], json_output=True)
    
    if status.get("connected"):
        print(f"Already connected to {status.get('runtime', {}).get('gpu', 'runtime')}")
        return True
    
    print(f"Connecting to Colab with {gpu} GPU...")
    result = run_command(["connect", "--gpu", gpu])
    
    if result.get("success"):
        print("Connected!")
        return True
    else:
        print(f"Failed to connect: {result.get('stderr', 'Unknown error')}")
        return False


def create_notebook(name: str, cells: List[NotebookCell]) -> Optional[str]:
    """Create a new Colab notebook."""
    # Build notebook JSON
    notebook_json = {
        "cells": [
            {
                "cell_type": cell.cell_type,
                "source": cell.source.split("\n"),
                "metadata": {},
                **({"outputs": [], "execution_count": None} if cell.cell_type == "code" else {})
            }
            for cell in cells
        ],
        "metadata": {
            "colab": {
                "name": name,
                "provenance": []
            },
            "kernelspec": {
                "name": "python3",
                "display_name": "Python 3"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 0
    }
    
    # Write to temp file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ipynb', delete=False) as f:
        json.dump(notebook_json, f)
        temp_path = f.name
    
    # Upload to Drive
    result = run_command(["notebook", "create", "--name", name, "--from", temp_path])
    
    # Clean up temp file
    import os
    os.unlink(temp_path)
    
    if result.get("success"):
        # Parse notebook ID from output
        # This is a simplified example - actual parsing depends on command output
        print(f"Created notebook: {name}")
        return "notebook-id"  # Would be parsed from actual output
    else:
        print(f"Failed to create notebook: {result.get('stderr')}")
        return None


def execute_notebook_cell(code: str, timeout: int = 300) -> Dict[str, Any]:
    """Execute a code cell on the connected runtime."""
    result = run_command(
        ["run", "--kernel", "--timeout", str(timeout), code],
        json_output=True
    )
    return result


def run_experiment(
    name: str,
    setup_code: str,
    experiment_code: str,
    cleanup_code: Optional[str] = None,
    gpu: str = "T4"
) -> Dict[str, Any]:
    """
    Run a complete experiment workflow.
    
    Args:
        name: Experiment name for logging
        setup_code: Code to run first (imports, data loading)
        experiment_code: Main experiment code
        cleanup_code: Optional cleanup code
        gpu: GPU type to use
    
    Returns:
        Dictionary with results and timing
    """
    results = {
        "name": name,
        "success": False,
        "stages": {},
        "total_time": 0
    }
    
    start_time = time.time()
    
    # Connect
    if not ensure_connected(gpu):
        results["error"] = "Failed to connect"
        return results
    
    # Run setup
    print(f"[{name}] Running setup...")
    setup_result = execute_notebook_cell(setup_code)
    results["stages"]["setup"] = {
        "success": setup_result.get("success", False),
        "time": setup_result.get("executionTime", 0)
    }
    
    if not setup_result.get("success"):
        results["error"] = f"Setup failed: {setup_result.get('error', {}).get('message')}"
        return results
    
    # Run experiment
    print(f"[{name}] Running experiment...")
    exp_result = execute_notebook_cell(experiment_code, timeout=3600)
    results["stages"]["experiment"] = {
        "success": exp_result.get("success", False),
        "time": exp_result.get("executionTime", 0),
        "result": exp_result.get("result"),
        "stdout": exp_result.get("stdout")
    }
    
    if not exp_result.get("success"):
        results["error"] = f"Experiment failed: {exp_result.get('error', {}).get('message')}"
    else:
        results["success"] = True
    
    # Run cleanup if provided
    if cleanup_code:
        print(f"[{name}] Running cleanup...")
        cleanup_result = execute_notebook_cell(cleanup_code)
        results["stages"]["cleanup"] = {
            "success": cleanup_result.get("success", False),
            "time": cleanup_result.get("executionTime", 0)
        }
    
    results["total_time"] = time.time() - start_time
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Automate Colab notebook operations"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Create notebook
    create_parser = subparsers.add_parser("create", help="Create a new notebook")
    create_parser.add_argument("name", help="Notebook name")
    create_parser.add_argument("--template", help="Template to use")
    
    # Run experiment
    run_parser = subparsers.add_parser("run", help="Run an experiment")
    run_parser.add_argument("--name", default="experiment", help="Experiment name")
    run_parser.add_argument("--setup", help="Setup code or file")
    run_parser.add_argument("--code", required=True, help="Experiment code or file")
    run_parser.add_argument("--cleanup", help="Cleanup code or file")
    run_parser.add_argument("--gpu", default="T4", help="GPU type")
    run_parser.add_argument("--json", action="store_true", help="JSON output")
    
    # Demo
    demo_parser = subparsers.add_parser("demo", help="Run demo experiment")
    demo_parser.add_argument("--gpu", default="T4", help="GPU type")
    
    args = parser.parse_args()
    
    if args.command == "create":
        # Create a simple notebook
        cells = [
            NotebookCell(
                cell_type="markdown",
                source=f"# {args.name}\n\nCreated by notebook-automation.py"
            ),
            NotebookCell(
                cell_type="code",
                source="import torch\nprint(f'PyTorch: {torch.__version__}')\nprint(f'CUDA: {torch.cuda.is_available()}')"
            ),
        ]
        notebook_id = create_notebook(args.name, cells)
        if notebook_id:
            print(f"Notebook created: {notebook_id}")
        else:
            sys.exit(1)
    
    elif args.command == "run":
        # Load code from file if needed
        def load_code(code_or_file: str) -> str:
            if code_or_file.endswith(".py"):
                with open(code_or_file) as f:
                    return f.read()
            return code_or_file
        
        setup = load_code(args.setup) if args.setup else "import torch"
        code = load_code(args.code)
        cleanup = load_code(args.cleanup) if args.cleanup else None
        
        results = run_experiment(
            name=args.name,
            setup_code=setup,
            experiment_code=code,
            cleanup_code=cleanup,
            gpu=args.gpu
        )
        
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"\n{'='*50}")
            print(f"Experiment: {results['name']}")
            print(f"Success: {results['success']}")
            print(f"Total time: {results['total_time']:.2f}s")
            
            for stage, data in results.get("stages", {}).items():
                status = "✓" if data.get("success") else "✗"
                print(f"  {status} {stage}: {data.get('time', 0):.2f}s")
            
            if not results["success"] and "error" in results:
                print(f"\nError: {results['error']}")
                sys.exit(1)
    
    elif args.command == "demo":
        # Run a demo experiment
        setup_code = """
import torch
import time
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
"""
        
        experiment_code = """
import torch
import time

# Simple GPU benchmark
if torch.cuda.is_available():
    device = torch.device('cuda')
    
    # Matrix multiplication benchmark
    sizes = [1000, 2000, 4000]
    results = []
    
    for size in sizes:
        a = torch.randn(size, size, device=device)
        b = torch.randn(size, size, device=device)
        
        # Warmup
        torch.matmul(a, b)
        torch.cuda.synchronize()
        
        # Benchmark
        start = time.time()
        for _ in range(10):
            c = torch.matmul(a, b)
        torch.cuda.synchronize()
        elapsed = time.time() - start
        
        gflops = (2 * size ** 3 * 10) / elapsed / 1e9
        results.append({
            'size': size,
            'time': elapsed / 10,
            'gflops': gflops
        })
        print(f"Size {size}: {gflops:.1f} GFLOPS")
    
    print(f"\\nBenchmark complete!")
else:
    print("No GPU available - skipping benchmark")
"""
        
        cleanup_code = """
import torch
import gc
if torch.cuda.is_available():
    torch.cuda.empty_cache()
gc.collect()
print("Cleanup complete")
"""
        
        results = run_experiment(
            name="GPU Benchmark Demo",
            setup_code=setup_code,
            experiment_code=experiment_code,
            cleanup_code=cleanup_code,
            gpu=args.gpu
        )
        
        print(f"\n{'='*50}")
        print(f"Demo completed: {'✓' if results['success'] else '✗'}")
        print(f"Total time: {results['total_time']:.2f}s")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
