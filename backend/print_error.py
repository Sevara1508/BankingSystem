"""
print_error.py - Error logging module for the Banking System Back End.

Centralizes all error output in the required ERROR: <msg> format.
Fatal errors terminate the program immediately via sys.exit(1).

Usage:
    from print_error import log_constraint_error
    log_constraint_error("balance would go negative", "NO_NEGATIVE_BALANCE")
    log_constraint_error("malformed line", "transactions.txt", fatal=True)
"""

import sys


def log_constraint_error(description, context, fatal=False):
    """
    Logs an error message to stdout in the required ERROR: <msg> format.

    For non-fatal constraint violations, prints the error and returns so
    processing can continue. For fatal errors, prints the error and
    immediately terminates the program with exit code 1.

    Args:
        description (str): Detailed explanation of what went wrong.
        context (str):     The constraint type label (non-fatal) or the
                           input file name (fatal) where the error occurred.
        fatal (bool):      If True, calls sys.exit(1) after printing.
                           Defaults to False.

    Returns:
        None. Terminates program if fatal=True.
    """
    if fatal:
        print(f"ERROR: Fatal error - File {context} - {description}")
        sys.exit(1)
    else:
        print(f"ERROR: {context}: {description}")