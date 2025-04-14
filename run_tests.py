#!/usr/bin/env python3
"""
Test runner for the exo Multi-Agent Framework
"""

import os
import sys
import subprocess
import argparse

def run_tests(args):
    """Run the tests with the specified options."""
    # Construct the pytest command
    cmd = ["pytest"]
    
    # Add verbosity
    if args.verbose:
        cmd.append("-v")
    
    # Add coverage
    if args.coverage:
        cmd.extend(["--cov=exo", "--cov-report=term", "--cov-report=html"])
    
    # Add specific test files or directories
    if args.tests:
        cmd.extend(args.tests)
    else:
        cmd.append("exo/tests/")
    
    # Run the tests
    print(f"Running tests with command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    return result.returncode

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run tests for the exo Multi-Agent Framework")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("-c", "--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("tests", nargs="*", help="Specific test files or directories to run")
    
    args = parser.parse_args()
    
    # Run the tests
    return run_tests(args)

if __name__ == "__main__":
    sys.exit(main())
