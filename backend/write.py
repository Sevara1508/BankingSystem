"""
write.py - Output file writing module for the Banking System Back End.

Serializes the final in-memory accounts dictionary into the two required
output files using exact fixed-length formats. Both files are sorted in
ascending order by account number and terminated with an END_OF_FILE
sentinel record.

Output files produced:
    New Master Bank Accounts File    - 45 characters per line (includes TTTT and plan)
    New Current Bank Accounts File   - 37 characters per line (no TTTT or plan)

Usage:
    from write import write_new_master_accounts, write_new_current_accounts
    write_new_master_accounts(accounts, "new_master.txt")
    write_new_current_accounts(accounts, "new_current.txt")
"""

from print_error import log_constraint_error

# Sentinel appended at the end of every output file
END_OF_FILE_SENTINEL = "END_OF_FILE"


def write_new_master_accounts(accounts, file_path):
    """
    Writes all updated account records to the New Master Bank Accounts File.

    Each account is formatted as a 45-character fixed-length line:
        NNNNN AAAAAAAAAAAAAAAAAAAA S PPPPPPPP TTTT SP|NP
    Accounts are sorted in ascending order by account number. An
    END_OF_FILE sentinel record is appended at the end.

    Format details:
        Positions  0-4   : Account number, right-justified, zero-padded (5 chars)
        Position   5     : Space separator
        Positions  6-25  : Name, left-justified, space-padded to 20 chars
        Position   26    : Space separator
        Position   27    : Status ("A" or "D")
        Position   28    : Space separator
        Positions  29-36 : Balance in XXXXX.XX format (8 chars)
        Position   37    : Space separator
        Positions  38-41 : Transaction count, right-justified, zero-padded (4 chars)
        Position   42    : Space separator
        Positions  43-44 : Plan type ("SP" or "NP")

    Args:
        accounts  (dict): Final account state keyed by account number string.
        file_path (str):  Destination path for the New Master Bank Accounts File.

    Returns:
        None. Creates or overwrites the output file.
    """
    sorted_accounts = sorted(accounts.values(), key=lambda a: a["account_number"])

    try:
        with open(file_path, "w") as f:
            for account in sorted_accounts:
                line = _format_master_line(account)
                f.write(line + "\n")
            f.write(END_OF_FILE_SENTINEL + "\n")
    except OSError as e:
        log_constraint_error(str(e), file_path, fatal=True)


def write_new_current_accounts(accounts, file_path):
    """
    Writes all updated account records to the New Current Bank Accounts File.

    Each account is formatted as a 37-character fixed-length line:
        NNNNN AAAAAAAAAAAAAAAAAAAA S PPPPPPPP
    This file does NOT include the TTTT transaction count or SP/NP plan type
    fields. Accounts are sorted ascending by account number. An END_OF_FILE
    sentinel is appended at the end.

    Format details:
        Positions  0-4   : Account number, right-justified, zero-padded (5 chars)
        Position   5     : Space separator
        Positions  6-25  : Name, left-justified, space-padded to 20 chars
        Position   26    : Space separator
        Position   27    : Status ("A" or "D")
        Position   28    : Space separator
        Positions  29-36 : Balance in XXXXX.XX format (8 chars)

    Args:
        accounts  (dict): Final account state keyed by account number string.
        file_path (str):  Destination path for the New Current Bank Accounts File.

    Returns:
        None. Creates or overwrites the output file.
    """
    sorted_accounts = sorted(accounts.values(), key=lambda a: a["account_number"])

    try:
        with open(file_path, "w") as f:
            for account in sorted_accounts:
                line = _format_current_line(account)
                f.write(line + "\n")
            f.write(END_OF_FILE_SENTINEL + "\n")
    except OSError as e:
        log_constraint_error(str(e), file_path, fatal=True)


# ---------------------------------------------------------------------------
# Private formatting helpers
# ---------------------------------------------------------------------------

def _format_master_line(account):
    """
    Formats a single account record as a 45-character Master file line.

    Args:
        account (dict): Account record dictionary.

    Returns:
        str: Exactly 45-character string (no trailing newline).
    """
    acct_num  = account["account_number"].zfill(5)           # NNNNN
    name      = account["name"].ljust(20)[:20]               # 20-char name
    status    = account["status"]                             # A or D
    balance   = _format_balance(account["balance"])          # XXXXX.XX
    tx_count  = str(account["total_transactions"]).zfill(4)  # TTTT
    plan      = account["plan"]                               # SP or NP

    return f"{acct_num} {name} {status} {balance} {tx_count} {plan}"


def _format_current_line(account):
    """
    Formats a single account record as a 37-character Current Accounts line.

    Args:
        account (dict): Account record dictionary.

    Returns:
        str: Exactly 37-character string (no trailing newline).
    """
    acct_num = account["account_number"].zfill(5)    # NNNNN
    name     = account["name"].ljust(20)[:20]        # 20-char name
    status   = account["status"]                      # A or D
    balance  = _format_balance(account["balance"])   # XXXXX.XX

    return f"{acct_num} {name} {status} {balance}"


def _format_balance(balance):
    """
    Converts a float balance to the required XXXXX.XX 8-character string.

    The integer part is zero-padded to 5 digits and the decimal part is
    always exactly 2 digits.

    Args:
        balance (float): Account balance in CAD.

    Returns:
        str: 8-character balance string in XXXXX.XX format.
    """
    integer_part, decimal_part = f"{balance:.2f}".split(".")
    return integer_part.zfill(5) + "." + decimal_part