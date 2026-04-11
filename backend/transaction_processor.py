"""
transaction_processor.py - Transaction processing module for the Banking System Back End.

Applies every transaction in the merged transaction list to the in-memory
accounts dictionary. Enforces all business constraints, deducts per-transaction
service fees, and increments the TTTT counter after each real transaction.

Transaction codes:
    00 - end of session  (skip)
    01 - withdrawal
    02 - transfer
    03 - paybill
    04 - deposit
    05 - create account
    06 - delete account
    07 - disable account
    08 - changeplan

Usage:
    from transaction_processor import apply_all
    updated_accounts = apply_all(accounts, transactions)
"""

from print_error import log_constraint_error

# Service fee amounts per transaction by account plan type
FEE_STUDENT     = 0.05   # Student Plan (SP)
FEE_NON_STUDENT = 0.10   # Non-Student Plan (NP)


def apply_all(accounts: dict, transactions: list) -> dict:
    """
    Main dispatch loop. Iterates every transaction and applies it to the
    in-memory accounts dictionary.

    End-of-session records (code 00) are silently skipped. Transfer transactions
    (code 02) are handled in pairs: the first 02 is the source, the second is
    the destination. All other codes are forwarded to apply_transaction().

    Returns the fully updated accounts dictionary after all transactions have
    been processed.

    Parameters:
        accounts     (dict): Account records keyed by account number string.
        transactions (list): Ordered list of transaction dictionaries.

    Returns:
        dict: The updated accounts dictionary.
    """
    pending_transfer = None
    for txn in transactions:
        if txn["code"] == "00":
            continue
        if txn["code"] == "02":
            if pending_transfer is None:
                pending_transfer = txn
                continue
            else:
                # Complete the transfer
                src_num = pending_transfer["account_number"]
                dst_num = txn["account_number"]
                amount = pending_transfer["amount"]
                _apply_transfer(accounts, src_num, dst_num, amount)
                # Apply fee and increment counter for source
                account = accounts[src_num]
                apply_fee(account)
                account["total_transactions"] += 1
                pending_transfer = None
                continue
        # For other codes
        apply_transaction(accounts, txn)
    return accounts

    return accounts


def apply_transaction(accounts: dict, txn: dict) -> None:
    """
    Dispatches a single transaction to the appropriate private handler.

    Parameters:
        accounts (dict): Current account state.
        txn      (dict): Single transaction dictionary.

    Returns:
        None. Modifies accounts in place.
    """
    code     = txn["code"]
    acct_num = txn["account_number"]
    amount   = txn["amount"]

    # ---- Create does not require the account to pre-exist ---------------
    if code == "05":
        _apply_create(accounts, txn)
        return  # No fee charged on account creation

    # ---- All other codes require the account to exist -------------------
    if acct_num not in accounts:
        log_constraint_error(
            f"account {acct_num} does not exist",
            "ACCOUNT_NOT_FOUND",
        )
        return

    account = accounts[acct_num]

    # ---- Delete is allowed on disabled accounts -------------------------
    if code == "06":
        _apply_delete(accounts, acct_num)
        return  # No fee charged on deletion

    # ---- All remaining operations require an active account -------------
    if account["status"] == "D":
        log_constraint_error(
            f"account {acct_num} is disabled; transaction {code} rejected",
            "ACCOUNT_DISABLED",
        )
        return

    # ---- Dispatch to the appropriate handler ----------------------------
    # Track balance before to detect if handler silently aborted
    balance_before = account["balance"]
    succeeded = True

    if code == "01":
        _apply_withdrawal(account, amount)
        if account["balance"] == balance_before:
            succeeded = False
    elif code == "03":
        _apply_paybill(account, amount)
        if account["balance"] == balance_before:
            succeeded = False
    elif code == "04":
        _apply_deposit(account, amount)
    elif code == "07":
        _apply_disable(account)
    elif code == "08":
        _apply_changeplan(account)
    else:
        log_constraint_error(
            f"unknown transaction code {code} for account {acct_num}",
            "UNKNOWN_CODE",
        )
        return  # No fee for unknown codes

    if not succeeded:
        return  # Constraint was violated; no fee, no counter increment

    # ---- Apply the per-transaction service fee and increment counter ----
    apply_fee(account)
    account["total_transactions"] += 1


def apply_fee(account: dict) -> None:
    """
    Deducts the daily service fee from the account after each real transaction.

    The fee amount depends on the account plan:
        SP (Student Plan)     : $0.05 per transaction
        NP (Non-Student Plan) : $0.10 per transaction

    Logs a constraint error and leaves the balance unchanged if the fee
    would cause the balance to go below $0.00.

    Parameters:
        account (dict): The account record to debit.

    Returns:
        None. Modifies account['balance'] in place.
    """
    fee = FEE_STUDENT if account["plan"] == "SP" else FEE_NON_STUDENT

    if account["balance"] - fee < 0.0:
        log_constraint_error(
            f"account {account['account_number']}: service fee of ${fee:.2f} "
            f"would cause negative balance ({account['balance']:.2f}); fee not applied",
            "NEGATIVE_BALANCE_FEE",
        )
        return

    account["balance"] = round(account["balance"] - fee, 2)


# ---------------------------------------------------------------------------
# Private transaction handlers
# ---------------------------------------------------------------------------

def _apply_withdrawal(account: dict, amount: float) -> None:
    """
    Processes a withdrawal (code 01).

    Logs a constraint error and skips if the resulting balance would be negative.
    """
    if account["balance"] - amount < 0.0:
        log_constraint_error(
            f"account {account['account_number']}: withdrawal of ${amount:.2f} "
            f"would cause negative balance ({account['balance']:.2f})",
            "NEGATIVE_BALANCE",
        )
        return

    account["balance"] = round(account["balance"] - amount, 2)


def _apply_transfer(accounts: dict, src_num: str, dst_num: str, amount: float) -> None:
    """
    Transfers funds between two accounts (code 02).
    """
    if dst_num not in accounts:
        log_constraint_error(
            f"transfer destination account {dst_num} does not exist",
            "ACCOUNT_NOT_FOUND",
        )
        return

    src = accounts[src_num]
    dst = accounts[dst_num]

    if src["balance"] - amount < 0.0:
        log_constraint_error(
            f"account {src_num}: transfer of ${amount:.2f} would cause "
            f"negative balance ({src['balance']:.2f})",
            "NEGATIVE_BALANCE",
        )
        return

    src["balance"] = round(src["balance"] - amount, 2)
    dst["balance"] = round(dst["balance"] + amount, 2)


def _apply_paybill(account: dict, amount: float) -> None:
    """
    Processes a bill payment (code 03).
    """
    if account["balance"] - amount < 0.0:
        log_constraint_error(
            f"account {account['account_number']}: paybill of ${amount:.2f} "
            f"would cause negative balance ({account['balance']:.2f})",
            "NEGATIVE_BALANCE",
        )
        return

    account["balance"] = round(account["balance"] - amount, 2)


def _apply_deposit(account: dict, amount: float) -> None:
    """
    Processes a deposit (code 04) by adding the amount to the account balance.
    """
    account["balance"] = round(account["balance"] + amount, 2)


def _apply_create(accounts: dict, txn: dict) -> None:
    """
    Creates a new account (code 05).

    FIX 1: Uses txn["amount"] as the opening balance (was hardcoded 0.00).
    FIX 2: Accepts both short ("S"/"N") and full ("SP"/"NP") plan codes in misc.
    """
    acct_num = txn["account_number"]

    if acct_num in accounts:
        log_constraint_error(
            f"account {acct_num} already exists; create rejected",
            "DUPLICATE_ACCOUNT",
        )
        return

    # Accept "SP"/"S" → SP, "NP"/"N" → NP, anything else → NP
    misc = txn.get("misc", "").strip()
    if misc in {"SP", "S"}:
        plan = "SP"
    elif misc in {"NP", "N"}:
        plan = "NP"
    else:
        plan = "NP"

    accounts[acct_num] = {
        "account_number":     acct_num,
        "name":               txn.get("name", ""),
        "status":             "A",
        "balance":            round(txn.get("amount", 0.00), 2),  # FIX: use amount
        "total_transactions": 0,
        "plan":               plan,
    }


def _apply_delete(accounts: dict, account_number: str) -> None:
    """
    Removes an account (code 06) from the accounts dictionary.
    """
    del accounts[account_number]


def _apply_disable(account: dict) -> None:
    """
    Disables an account (code 07) by setting its status to "D".
    """
    account["status"] = "D"


def _apply_changeplan(account: dict) -> None:
    """
    Changes the account plan from SP to NP (code 08). No reverse allowed.
    """
    if account["plan"] != "SP":
        log_constraint_error(
            f"account {account['account_number']}: changeplan only allowed from SP to NP",
            "INVALID_PLAN_CHANGE",
        )
        return
    account["plan"] = "NP"