"""
DSSATTools test suite initialization.
"""

import os
import sys

def run_tests(*args):
    """
    Programmatically executes the test_run.py test suite using pytest.
    
    Accepts arbitrary arguments (*args) to pass along to the underlying 
    pytest call (e.g., passing '-v' for verbose output).
    """
    try:
        import pytest
    except ImportError:
        raise ImportError(
            "The 'pytest' package is required to execute the test suite. "
            "Please install it using: pip install pytest"
        )

    # Dynamically resolve the absolute path of this tests directory
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Target specifically the test_run.py file as requested
    target_test_file = os.path.join(tests_dir, "test_run.py")

    # Verify the target test file actually exists in the installation layout
    if not os.path.exists(target_test_file):
        raise FileNotFoundError(
            f"Could not locate the core test file at: {target_test_file}. "
            "Ensure package data files are included properly in your source distribution."
        )

    print("=" * 60)
    print("         DSSATTools Automated Test Suite Engine")
    print("=" * 60)
    print(f"Targeting test file: {target_test_file}\n")

    # Combine our targeted test file path with any extra arguments passed by the user
    pytest_args = [target_test_file] + list(args)

    # Execute pytest programmatically and catch the exit status code
    status = pytest.main(pytest_args)
    
    # Return the status code to the caller (0 = success, non-zero = failure)
    return status