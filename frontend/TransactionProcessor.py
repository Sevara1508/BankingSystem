"""
TransactionProcessor class
Handles all banking transactions by prompting for input, validating rules,
and logging successful transactions to TransactionLog.
"""

class TransactionProcessor:
    """
    Processes all 10 transaction types:
    - Login (standard and admin)
    - Withdrawal, Transfer, Paybill, Deposit
    - Create, Delete, Disable, Changeplan (admin only)
    - Logout
    """
    
    def __init__(self, session_manager, account_manager, transaction_log):
        """
        Initialize TransactionProcessor with required managers
        
        Args:
            session_manager: SessionManager instance for login state and limits
            account_manager: AccountManager instance for account operations
            transaction_log: TransactionLog instance for recording transactions
        """
        self.session = session_manager
        self.account_manager = account_manager
        self.transaction_log = transaction_log
        self.scanner = input  # Using Python's built-in input() function
    
    def process_standard_login(self):
        """Start a standard user session with non-admin privileges"""
        print("Logging in as standard user...")
        self.session.login(is_admin=False)
        print("Login successful. Standard mode.")
    
    def process_admin_login(self):
        """Start an admin session with privileged transaction access"""
        print("Logging in as admin...")
        self.session.login(is_admin=True)
        print("Login successful. Admin mode.")
    
    def process_withdrawal(self):
        """Handle withdrawal transaction with validation and limit checking"""
        if not self.session.is_logged_in():
            print("ERROR: Must be logged in first")
            return
        
        # Get account number
        acc_num = input("Enter account number: ").strip()
        
        # Get account
        account = self.account_manager.get_account(acc_num)
        if not account:
            print("ERROR: Account does not exist")
            return
        
        # Check if account is active
        if account.status != 'A':
            print("ERROR: Account is disabled")
            return
        
        # Check ownership (if standard mode)
        if not self.session.is_admin():
            if not account.is_valid_for(self.session.get_current_user()):
                print("ERROR: Account does not belong to current user")
                return
        
        # Get amount
        try:
            amount = float(input("Enter amount to withdraw: $"))
            if amount <= 0:
                print("ERROR: Amount must be positive")
                return
        except ValueError:
            print("ERROR: Invalid amount")
            return
        
        # Check session limit
        if not self.session.can_withdraw(amount):
            print(f"ERROR: Would exceed ${self.session.withdrawal_limit} session limit")
            return
        
        # Attempt withdrawal
        if account.withdraw(amount):
            # Record in session for limit tracking
            self.session.record_withdrawal(amount)
            
            # Log transaction
            self.transaction_log.log_withdrawal(acc_num, amount)
            
            print(f"Withdrawal successful. New balance: ${account.balance:.2f}")
        else:
            print("ERROR: Insufficient funds")
    
    def process_transfer(self):
        """Handle transfer transaction between two accounts"""
        if not self.session.is_logged_in():
            print("ERROR: Must be logged in first")
            return
        
        # Get from-account
        from_acc = input("Enter account number to transfer FROM: ").strip()
        account_from = self.account_manager.get_account(from_acc)
        if not account_from:
            print("ERROR: Source account does not exist")
            return
        
        # Check if source account is active
        if account_from.status != 'A':
            print("ERROR: Source account is disabled")
            return
        
        # Check ownership (if standard mode)
        if not self.session.is_admin():
            if not account_from.is_valid_for(self.session.get_current_user()):
                print("ERROR: Source account does not belong to current user")
                return
        
        # Get to-account
        to_acc = input("Enter account number to transfer TO: ").strip()
        account_to = self.account_manager.get_account(to_acc)
        if not account_to:
            print("ERROR: Destination account does not exist")
            return
        
        # Check if destination account is active
        if account_to.status != 'A':
            print("ERROR: Destination account is disabled")
            return
        
        # Get amount
        try:
            amount = float(input("Enter amount to transfer: $"))
            if amount <= 0:
                print("ERROR: Amount must be positive")
                return
        except ValueError:
            print("ERROR: Invalid amount")
            return
        
        # Check session limit
        if not self.session.can_transfer(amount):
            print(f"ERROR: Would exceed ${self.session.transfer_limit} session limit")
            return
        
        # Attempt transfer (withdraw from source, deposit to destination)
        if account_from.withdraw(amount):
            account_to.deposit(amount)
            
            # Record in session for limit tracking
            self.session.record_transfer(amount)
            
            # Log transaction
            self.transaction_log.log_transfer(from_acc, to_acc, amount)
            
            print(f"Transfer successful.")
            print(f"Source balance: ${account_from.balance:.2f}")
            print(f"Destination balance: ${account_to.balance:.2f}")
        else:
            print("ERROR: Insufficient funds in source account")
    
    def process_paybill(self):
        """Handle bill payment to approved companies (EC, CQ, FI)"""
        if not self.session.is_logged_in():
            print("ERROR: Must be logged in first")
            return
        
        # Valid company codes
        valid_companies = {
            "EC": "The Bright Light Electric Company",
            "CQ": "Credit Card Company Q",
            "FI": "Fast Internet, Inc."
        }
        
        # Get account number
        acc_num = input("Enter account number: ").strip()
        
        # Get account
        account = self.account_manager.get_account(acc_num)
        if not account:
            print("ERROR: Account does not exist")
            return
        
        # Check if account is active
        if account.status != 'A':
            print("ERROR: Account is disabled")
            return
        
        # Check ownership (if standard mode)
        if not self.session.is_admin():
            if not account.is_valid_for(self.session.get_current_user()):
                print("ERROR: Account does not belong to current user")
                return
        
        # Get company code
        company = input("Enter company code (EC, CQ, or FI): ").strip().upper()
        if company not in valid_companies:
            print("ERROR: Invalid company. Must be EC, CQ, or FI")
            return
        
        # Get amount
        try:
            amount = float(input("Enter amount to pay: $"))
            if amount <= 0:
                print("ERROR: Amount must be positive")
                return
        except ValueError:
            print("ERROR: Invalid amount")
            return
        
        # Check session limit
        if not self.session.can_pay_bill(amount):
            print(f"ERROR: Would exceed ${self.session.paybill_limit} session limit")
            return
        
        # Attempt payment
        if account.withdraw(amount):
            # Record in session for limit tracking
            self.session.record_pay_bill(amount)
            
            # Log transaction
            self.transaction_log.log_paybill(acc_num, amount, company)
            
            print(f"Payment to {valid_companies[company]} successful.")
            print(f"New balance: ${account.balance:.2f}")
        else:
            print("ERROR: Insufficient funds")
    
    def process_deposit(self):
        """Handle deposit transaction"""
        if not self.session.is_logged_in():
            print("ERROR: Must be logged in first")
            return
        
        # Get account number
        acc_num = input("Enter account number: ").strip()
        
        # Get account
        account = self.account_manager.get_account(acc_num)
        if not account:
            print("ERROR: Account does not exist")
            return
        
        # Check if account is active
        if account.status != 'A':
            print("ERROR: Account is disabled")
            return
        
        # Get amount
        try:
            amount = float(input("Enter amount to deposit: $"))
            if amount <= 0:
                print("ERROR: Amount must be positive")
                return
        except ValueError:
            print("ERROR: Invalid amount")
            return
        
        # Deposit (no session limit)
        account.deposit(amount)
        
        # Log transaction
        self.transaction_log.log_deposit(acc_num, amount)
        
        print(f"Deposit successful. New balance: ${account.balance:.2f}")
        print("NOTE: Deposited funds are not available for withdrawal in current session.")
    
    def process_create(self):
        """PRIVILEGED: Create new account (admin only)"""
        if not self.session.is_logged_in():
            print("ERROR: Must be logged in first")
            return
        
        if not self.session.is_admin():
            print("ERROR: Create account is admin only")
            return
        
        # Get account holder name
        name = input("Enter account holder name: ").strip()
        if not name:
            print("ERROR: Name cannot be empty")
            return
        
        # Get initial balance
        try:
            balance = float(input("Enter initial balance: $"))
            if balance < 0:
                print("ERROR: Balance cannot be negative")
                return
        except ValueError:
            print("ERROR: Invalid amount")
            return
        
        # Create account
        account_num = self.account_manager.create_account(name, balance)
        
        if account_num:
            # Log transaction
            self.transaction_log.log_create(account_num, balance)
            print(f"Account created successfully. Account number: {account_num}")
        else:
            print("ERROR: Could not create account")
    
    def process_delete(self):
        """PRIVILEGED: Delete account (admin only)"""
        if not self.session.is_logged_in():
            print("ERROR: Must be logged in first")
            return
        
        if not self.session.is_admin():
            print("ERROR: Delete account is admin only")
            return
        
        # Get account holder name
        name = input("Enter account holder name: ").strip()
        
        # Get account number
        acc_num = input("Enter account number: ").strip()
        
        # Verify account exists and matches name
        account = self.account_manager.get_account(acc_num)
        if not account:
            print("ERROR: Account does not exist")
            return
        
        if account.holder_name != name:
            print("ERROR: Account holder name does not match")
            return
        
        # Delete account
        self.account_manager.delete_account(acc_num)
        
        # Log transaction
        self.transaction_log.log_delete(acc_num)
        
        print(f"Account {acc_num} deleted successfully.")
    
    def process_disable(self):
        """PRIVILEGED: Disable account (admin only)"""
        if not self.session.is_logged_in():
            print("ERROR: Must be logged in first")
            return
        
        if not self.session.is_admin():
            print("ERROR: Disable account is admin only")
            return
        
        # Get account holder name
        name = input("Enter account holder name: ").strip()
        
        # Get account number
        acc_num = input("Enter account number: ").strip()
        
        # Verify account exists and matches name
        account = self.account_manager.get_account(acc_num)
        if not account:
            print("ERROR: Account does not exist")
            return
        
        if account.holder_name != name:
            print("ERROR: Account holder name does not match")
            return
        
        # Disable account
        self.account_manager.disable_account(acc_num)
        
        # Log transaction
        self.transaction_log.log_disable(acc_num)
        
        print(f"Account {acc_num} disabled successfully.")
    
    def process_change_plan(self):
        """PRIVILEGED: Change account plan from SP to NP (admin only)"""
        if not self.session.is_logged_in():
            print("ERROR: Must be logged in first")
            return
        
        if not self.session.is_admin():
            print("ERROR: Change plan is admin only")
            return
        
        # Get account holder name
        name = input("Enter account holder name: ").strip()
        
        # Get account number
        acc_num = input("Enter account number: ").strip()
        
        # Verify account exists and matches name
        account = self.account_manager.get_account(acc_num)
        if not account:
            print("ERROR: Account does not exist")
            return
        
        if account.holder_name != name:
            print("ERROR: Account holder name does not match")
            return
        
        if account.plan != 'SP':
            print("ERROR: Account is not on student plan")
            return
        
        # Change plan
        self.account_manager.change_plan(acc_num)
        
        # Log transaction
        self.transaction_log.log_change_plan(acc_num)
        
        print(f"Account {acc_num} plan changed from SP to NP successfully.")
    
    def process_logout(self):
        """End session and write transaction file"""
        if not self.session.is_logged_in():
            print("ERROR: Not logged in")
            return
        
        # Write transaction file
        filename = "daily_transaction.txt"
        self.transaction_log.write_to_file(filename)
        
        # Logout
        self.session.logout()
        
        print(f"Session ended. Transactions written to {filename}")
        print("Goodbye!")