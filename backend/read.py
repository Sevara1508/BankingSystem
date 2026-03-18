"""
read.py - Input file reading and parsing module for the Banking System Back End.

Reads and validates both input files, converting each fixed-length record
into an in-memory dictionary. Any malformed line triggers a fatal error
and halts the program immediately.

Accepted account file formats:
    45-char Master Bank Accounts File  - full format including TTTT and SP/NP plan
    37-char Current Bank Accounts File - frontend output; TTTT defaults to 0,
                                         plan defaults to NP

Transaction file format (frontend output, no spaces between fields):
    CC(2) + NAME(20) + NNNNN(5) + PPPPPPPP(8) + MM(2) + padding = 40 chars total

Usage:
    from read import read_old_bank_accounts, read_transactions
    accounts = read_old_bank_accounts("old_master.txt")
    transactions = read_transactions("daily_transaction.txt")
"""

from print_error import log_constraint_error


# ---------------------------------------------------------------------------
# Field-position constants for the Master Bank Accounts File
# ---------------------------------------------------------------------------
CURRENT_LINE_LENGTH  = 37   # Frontend current accounts file (no TTTT or plan)
MASTER_LINE_LENGTH   = 45   # Full master accounts file (includes TTTT and plan)

MASTER_ACCT_NUM      = slice(0, 5)    # NNNNN       positions  0-4
MASTER_NAME          = slice(6, 26)   # NAME (20)   positions  6-25
MASTER_STATUS        = 27             # S           position   27
MASTER_BALANCE       = slice(29, 37)  # PPPPPPPP    positions 29-36
MASTER_TRANS_COUNT   = slice(38, 42)  # TTTT        positions 38-41
MASTER_PLAN          = slice(43, 45)  # SP or NP    positions 43-44

# Default values used when reading the 37-char current accounts file
DEFAULT_TRANS_COUNT  = 0
DEFAULT_PLAN         = "NP"

# ---------------------------------------------------------------------------
# Field-position constants for the Transaction File (frontend format)
# No spaces between fields. Total 40 chars per line.
# CC(2) + NAME(20) + NNNNN(5) + PPPPPPPP(8) + MM(2) + padding(3) = 40
# ---------------------------------------------------------------------------
TXN_LINE_LENGTH   = 40
TXN_CODE          = slice(0, 2)    # CC           positions  0-1
TXN_NAME          = slice(2, 22)   # NAME (20)    positions  2-21
TXN_ACCT_NUM      = slice(22, 27)  # NNNNN        positions 22-26
TXN_AMOUNT        = slice(27, 35)  # PPPPPPPP     positions 27-34
TXN_MISC          = slice(35, 37)  # MM (2 chars) positions 35-36

VALID_STATUSES    = {"A", "D"}
VALID_PLANS       = {"SP", "NP"}
VALID_TX_CODES    = {"00", "01", "02", "03", "04", "05", "06", "07", "08"}


def read_old_bank_accounts(file_path):
    """
    Opens and reads an accounts input file in either supported format:
        - 37-char Current Bank Accounts File (produced by the Frontend)
        - 45-char Master Bank Accounts File (full format with TTTT and plan)

    When reading the 37-char format, TTTT defaults to 0 and plan defaults
    to NP since those fields are not present in that file.

    The returned dictionary is keyed by account number string so that
    TransactionProcessor can perform O(1) account lookups.

    Halts with a fatal error if any line is malformed.

    Args:
        file_path (str): Path to the accounts input file.

    Returns:
        dict: Keys are zero-padded 5-digit account number strings.
              Each value is a dict with keys:
                  account_number     (str)   - zero-padded 5-digit string
                  name               (str)   - account holder name, stripped
                  status             (str)   - "A" or "D"
                  balance            (float) - current balance in CAD
                  total_transactions (int)   - TTTT counter (0 if not in file)
                  plan               (str)   - "SP" or "NP" (NP if not in file)
    """
    accounts = {}

    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
    except OSError as e:
        log_constraint_error(str(e), file_path, fatal=True)

    for line_num, raw_line in enumerate(lines, start=1):
        line = raw_line.rstrip("\n")

        # Skip the END_OF_FILE sentinel record
        if line.strip() == "END_OF_FILE":
            continue

        # ---- Detect file format from line length ------------------------
        line_len = len(line)
        if line_len not in (CURRENT_LINE_LENGTH, MASTER_LINE_LENGTH):
            log_constraint_error(
                f"line {line_num} has {line_len} characters, "
                f"expected {CURRENT_LINE_LENGTH} (current accounts) "
                f"or {MASTER_LINE_LENGTH} (master accounts)",
                file_path,
                fatal=True,
            )

        # ---- Parse fields common to both formats ------------------------
        acct_num_str = line[MASTER_ACCT_NUM]   # positions 0-4  (5 digits)
        name_str     = line[MASTER_NAME]        # positions 6-25 (20 chars)
        status_str   = line[MASTER_STATUS]      # position  27
        balance_str  = line[MASTER_BALANCE]     # positions 29-36

        # Account number: must be 5-digit numeric
        if not acct_num_str.isdigit():
            log_constraint_error(
                f"line {line_num}: account number '{acct_num_str}' is not numeric",
                file_path,
                fatal=True,
            )

        # Status: must be A or D
        if status_str not in VALID_STATUSES:
            log_constraint_error(
                f"line {line_num}: status '{status_str}' is not A or D",
                file_path,
                fatal=True,
            )

        # Balance: must match XXXXX.XX format
        balance = _parse_balance(balance_str, line_num, file_path)

        # ---- Parse TTTT and plan only if this is the full master format -
        if line_len == MASTER_LINE_LENGTH:
            trans_count_str = line[MASTER_TRANS_COUNT]
            plan_str        = line[MASTER_PLAN]

            if not trans_count_str.isdigit():
                log_constraint_error(
                    f"line {line_num}: transaction count '{trans_count_str}' is not numeric",
                    file_path,
                    fatal=True,
                )

            if plan_str not in VALID_PLANS:
                log_constraint_error(
                    f"line {line_num}: plan type '{plan_str}' is not SP or NP",
                    file_path,
                    fatal=True,
                )

            trans_count = int(trans_count_str)
            plan        = plan_str

        else:
            # 37-char current accounts file: use safe defaults
            trans_count = DEFAULT_TRANS_COUNT
            plan        = DEFAULT_PLAN

        # ---- Build account record keyed by zero-padded account number ---
        # Important: key must stay zero-padded (e.g. "00001") so that
        # transaction lookups match the account numbers in the transaction file
        accounts[acct_num_str] = {
            "account_number":     acct_num_str,
            "name":               name_str.rstrip(" "),
            "status":             status_str,
            "balance":            balance,
            "total_transactions": trans_count,
            "plan":               plan,
        }

    return accounts


def read_transactions(file_path):
    """
    Opens and reads the transaction file produced by the Frontend.

    Frontend format (no spaces between fields, 40 chars per line):
        Positions  0-1  : CC    - two-digit transaction code
        Positions  2-21 : NAME  - account holder name, space-padded to 20
        Positions 22-26 : NNNNN - 5-digit account number
        Positions 27-34 : PPPPPPPP - amount in XXXXX.XX format
        Positions 35-36 : MM    - 2-char miscellaneous/plan flag
        Positions 37-39 : padding spaces

    All records including 00 end-of-session markers are included so that
    apply_all() can handle multi-session files correctly.

    Halts with a fatal error if any line is malformed.

    Args:
        file_path (str): Path to the transaction file.

    Returns:
        list of dicts, each with keys:
            code           (str)   - two-digit transaction code "00"-"08"
            name           (str)   - account holder name, stripped
            account_number (str)   - 5-digit zero-padded account number
            amount         (float) - transaction amount in CAD
            misc           (str)   - 2-char miscellaneous / plan flag, stripped
    """
    transactions = []

    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
    except OSError as e:
        log_constraint_error(str(e), file_path, fatal=True)

    for line_num, raw_line in enumerate(lines, start=1):
        line = raw_line.rstrip("\n")

        # ---- Parse the transaction code first so we can handle the
        # end-of-session record (code 00) which may be shorter than 40 chars
        code_str = line[TXN_CODE] if len(line) >= 2 else ""

        # End-of-session records may be padded to fewer than 40 chars;
        # accept any line starting with "00" as a valid end-of-session marker
        if code_str == "00":
            transactions.append({
                "code":           "00",
                "name":           "",
                "account_number": "00000",
                "amount":         0.0,
                "misc":           "",
            })
            continue

        # ---- Validate total line length for all real transactions -------
        if len(line) != TXN_LINE_LENGTH:
            log_constraint_error(
                f"line {line_num} has {len(line)} characters, expected {TXN_LINE_LENGTH}",
                file_path,
                fatal=True,
            )

        # ---- Parse and validate each field ------------------------------
        code_str   = line[TXN_CODE]
        name_str   = line[TXN_NAME]
        acct_str   = line[TXN_ACCT_NUM]
        amount_str = line[TXN_AMOUNT]
        misc_str   = line[TXN_MISC]

        # Transaction code: must be a known two-digit numeric code
        if code_str not in VALID_TX_CODES:
            log_constraint_error(
                f"line {line_num}: unknown transaction code '{code_str}'",
                file_path,
                fatal=True,
            )

        # Account number: must be 5-digit numeric
        if not acct_str.isdigit():
            log_constraint_error(
                f"line {line_num}: account number '{acct_str}' is not numeric",
                file_path,
                fatal=True,
            )

        # Amount: must match XXXXX.XX
        amount = _parse_balance(amount_str, line_num, file_path)

        transactions.append({
            "code":           code_str,
            "name":           name_str.strip(),
            "account_number": acct_str,
            "amount":         amount,
            "misc":           misc_str.strip(),
        })

    return transactions


# ---------------------------------------------------------------------------
# Private helper
# ---------------------------------------------------------------------------

def _parse_balance(value_str, line_num, file_path):
    """
    Validates and converts a balance string in XXXXX.XX format to a float.

    Halts with a fatal error if the string does not match the required
    8-character XXXXX.XX format (no negative sign permitted).

    Args:
        value_str (str):  The raw 8-character balance string.
        line_num  (int):  Line number in the file (for error messages).
        file_path (str):  Source file path (for error messages).

    Returns:
        float: The parsed balance value.
    """
    if (len(value_str) != 8
            or value_str[5] != "."
            or not value_str[:5].isdigit()
            or not value_str[6:].isdigit()):
        log_constraint_error(
            f"line {line_num}: balance '{value_str}' does not match XXXXX.XX format",
            file_path,
            fatal=True,
        )

    return float(value_str)