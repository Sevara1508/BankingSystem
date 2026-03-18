"""
main.py - Entry point for the Banking System Back End.

Program intention:
    This program is an overnight batch processor that applies a day's worth
    of banking transactions to the Master Bank Accounts File. It reads the
    previous day's master accounts and the merged transaction file, applies
    every transaction while enforcing business constraints, then writes two
    updated output files for the next day.

Input files (provided as command-line arguments):
    1. Old Master Bank Accounts File  - fixed-length 42-char records
    2. Merged Bank Account Transaction File - fixed-length 40-char records

Output files (provided as command-line arguments):
    3. New Master Bank Accounts File  - fixed-length 42-char records (with TTTT and plan)
    4. New Current Bank Accounts File - fixed-length 37-char records (no TTTT or plan)

How to run:
    python main.py <old_master> <transactions> <new_master> <new_current>

    Example:
        python main.py old_master.txt transactions.txt new_master.txt new_current.txt

Exit codes:
    0 - success
    1 - fatal error (malformed input or wrong number of arguments)
"""

import sys

from read                import read_old_bank_accounts, read_transactions
from transaction_processor import apply_all
from write               import write_new_master_accounts, write_new_current_accounts
from print_error         import log_constraint_error

# Expected number of command-line arguments (program name + 4 file paths)
EXPECTED_ARG_COUNT = 5


def run(argv: list) -> None:
    """
    Main entry point for the Back End. Validates command-line arguments,
    then executes the full read -> process -> write pipeline in order.

    Pipeline steps:
        1. Validate that exactly four file path arguments are provided
        2. Read the Old Master Bank Accounts File into an in-memory dict
        3. Read the Merged Bank Account Transaction File into a list
        4. Apply all transactions to the accounts dictionary
        5. Write the updated accounts to the New Master Bank Accounts File
        6. Write the updated accounts to the New Current Bank Accounts File

    Parameters:
        argv (list): Command-line argument list (sys.argv). Expected format:
                     [program_name, old_master, transactions, new_master, new_current]

    Returns:
        None. Writes output files and exits with code 0 on success,
        or code 1 on any fatal error.
    """
    # ---- Step 1: Validate command-line arguments ------------------------
    if len(argv) != EXPECTED_ARG_COUNT:
        log_constraint_error(
            f"expected 4 file path arguments, got {len(argv) - 1}",
            "command-line arguments",
            fatal=True,
        )

    old_master_path    = argv[1]
    transactions_path  = argv[2]
    new_master_path    = argv[3]
    new_current_path   = argv[4]

    # ---- Step 2: Read the Old Master Bank Accounts File -----------------
    accounts = read_old_bank_accounts(old_master_path)

    # ---- Step 3: Read the Merged Bank Account Transaction File ----------
    transactions = read_transactions(transactions_path)

    # ---- Step 4: Apply all transactions to the in-memory accounts dict --
    accounts = apply_all(accounts, transactions)

    # ---- Step 5: Write the New Master Bank Accounts File ----------------
    write_new_master_accounts(accounts, new_master_path)

    # ---- Step 6: Write the New Current Bank Accounts File ---------------
    write_new_current_accounts(accounts, new_current_path)


if __name__ == "__main__":
    run(sys.argv)