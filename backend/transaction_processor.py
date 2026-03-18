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

    End-of-session records (code 00) are silently skipped. All other codes
    are forwarded to apply_transaction(). Returns the fully updated accounts
    dictionary after all transactions have been processed.

    Parameters:
        accounts     (dict): Account records keyed by account number string.
        transactions (list): Ordered list of transaction dictionaries.

    Returns:
        dict: The updated accounts dictionary.
    """
    for txn in transactions:
        if txn["code"] == "00":
            # End-of-session marker; nothing to process
            continue
        apply_transaction(accounts, txn)

    return accounts


def apply_transaction(accounts: dict, txn: dict) -> None:
    """
    Dispatches a single transaction to the appropriate private handler.

    Before dispatching, verifies that the target account exists and is
    active (disabled accounts are rejected for all operations except
    delete). After the handler completes, applies the service fee via
    apply_fee() and increments the account's total_transactions counter.

    Parameters:
        accounts (dict): Current account state.
        txn      (dict): Single transaction dictionary with keys:
                         code, name, account_number, amount, misc.

    Returns:
        None. Modifies accounts in place.
    """
    code       = txn["code"]
    acct_num   = txn["account_number"]
    amount     = txn["amount"]

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
    if code == "01":
        _apply_withdrawal(account, amount)
    elif code == "02":
        # For transfers, the destination account number comes from txn["name"]
        # field parsed as an account number embedded in the transaction misc
        # context. Per the spec the destination is a second account number;
        # we use the misc field as the destination account number string.
        dst_num = txn["misc"].strip() if txn["misc"].strip() else txn["name"].strip()
        _apply_transfer(accounts, acct_num, dst_num, amount)
    elif code == "03":
        _apply_paybill(account, amount)
    elif code == "04":
        _apply_deposit(account, amount)
    elif code == "07":
        _apply_disable(account)
    elif code == "08":
        _apply_changeplan(account)

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
    Processes a withdrawal (code 01) by subtracting the amount from the
    account balance.

    Logs a constraint error and skips the withdrawal if the resulting
    balance would be negative.

    Parameters:
        account (dict):  The account to debit.
        amount  (float): The withdrawal amount in CAD.

    Returns:
        None. Modifies account['balance'] in place.
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

    Deducts the amount from the source account and credits it to the
    destination account. Both accounts must exist and both balances must
    remain non-negative after the transfer.

    Parameters:
        accounts (dict):  Full accounts dictionary.
        src_num  (str):   Source account number string.
        dst_num  (str):   Destination account number string.
        amount   (float): Transfer amount in CAD.

    Returns:
        None. Modifies account balances in place.
    """
    # Validate destination account exists
    if dst_num not in accounts:
        log_constraint_error(
            f"transfer destination account {dst_num} does not exist",
            "ACCOUNT_NOT_FOUND",
        )
        return

    src = accounts[src_num]
    dst = accounts[dst_num]

    # Validate source balance is sufficient
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
    Processes a bill payment (code 03) by subtracting the amount from the
    account balance.

    Logs a constraint error and skips if the resulting balance would be
    negative.

    Parameters:
        account (dict):  The account to debit.
        amount  (float): The bill payment amount in CAD.

    Returns:
        None. Modifies account['balance'] in place.
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

    Deposits never violate any constraint because they can only increase
    the balance.

    Parameters:
        account (dict):  The account to credit.
        amount  (float): The deposit amount in CAD.

    Returns:
        None. Modifies account['balance'] in place.
    """
    account["balance"] = round(account["balance"] + amount, 2)


def _apply_create(accounts: dict, txn: dict) -> None:
    """
    Creates a new account (code 05) using information from the transaction.

    The new account is added to the accounts dictionary with a zero balance
    and zero transaction count. Logs a constraint error and skips if the
    account number already exists.

    Parameters:
        accounts (dict): Full accounts dictionary.
        txn      (dict): Transaction record for the create operation.

    Returns:
        None. Adds new entry to accounts in place.
    """
    acct_num = txn["account_number"]

    if acct_num in accounts:
        log_constraint_error(
            f"account {acct_num} already exists; create rejected",
            "DUPLICATE_ACCOUNT",
        )
        return

    # Determine plan from misc field; default to NP if unrecognised
    plan = txn["misc"].strip() if txn["misc"].strip() in {"S", "N"} else "NP"
    if plan == "S":
        plan = "SP"
    elif plan == "N":
        plan = "NP"

    accounts[acct_num] = {
        "account_number":     acct_num,
        "name":               txn["name"],
        "status":             "A",
        "balance":            0.00,
        "total_transactions": 0,
        "plan":               plan,
    }


def _apply_delete(accounts: dict, account_number: str) -> None:
    """
    Removes an account (code 06) from the accounts dictionary.

    Deleted accounts will not appear in either output file because they
    are simply absent from the dictionary when the file writers run.

    Parameters:
        accounts       (dict): Full accounts dictionary.
        account_number (str):  Account number string to remove.

    Returns:
        None. Removes entry from accounts in place.
    """
    del accounts[account_number]


def _apply_disable(account: dict) -> None:
    """
    Disables an account (code 07) by setting its status to "D".

    The account remains in the output files with status D but will
    reject all future transactions (except delete).

    Parameters:
        account (dict): The account record to disable.

    Returns:
        None. Modifies account['status'] in place.
    """
    account["status"] = "D"


def _apply_changeplan(account: dict) -> None:
    """
    Toggles the account plan (code 08) between Student Plan (SP) and
    Non-Student Plan (NP).

    Parameters:
        account (dict): The account record to update.

    Returns:
        None. Modifies account['plan'] in place.
    """
    if account["plan"] == "SP":
        account["plan"] = "NP"
    else:
        account["plan"] = "SP"