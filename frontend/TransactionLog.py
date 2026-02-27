"""
TransactionLog class
Builds and stores 40-character fixed-format transaction records,
writes them to file at logout.
"""

class TransactionLog:
    """
    Formats and stores all transactions during a session.
    Writes to daily transaction file on logout with end-of-session marker.
    Transaction format: CC AAAAAAAAAAAAAAAAAAAA NNNNN PPPPPPPP MM
    - CC: 2-digit transaction code
    - AAAAAAAAAAAAAAAAAAAA: Account holder name (20 chars, left-justified)
    - NNNNN: Account number (5 digits, zero-filled)
    - PPPPPPPP: Amount (8 chars with .00, right-justified)
    - MM: Misc info (varies by transaction type)
    Total: 40 characters + newline
    """
    
    def __init__(self):
        """Initialize empty transaction list"""
        self.transactions = []  # List to store formatted transaction strings
    
    def log_withdrawal(self, account_number, amount):
        """
        Record withdrawal transaction (code 01)
        
        Args:
            account_number: 5-digit account number
            amount: Amount withdrawn
        """
        # Format: 01 AAAAAAAAAAAAAAAAAAAA NNNNN PPPPPPPP (spaces)
        code = "01"
        name = ""  # Account holder name not needed for withdrawal
        acc = self._format_account(account_number)
        amt = self._format_amount(amount)
        misc = " " * 4  # Empty misc field
        
        transaction = f"{code} {name:<20} {acc} {amt} {misc}"
        self.transactions.append(transaction)
    
    def log_transfer(self, from_account, to_account, amount):
        """
        Record transfer transaction (code 02)
        
        Args:
            from_account: Source account number
            to_account: Destination account number (goes in misc field)
            amount: Amount transferred
        """
        # Format: 02 AAAAAAAAAAAAAAAAAAAA NNNNN PPPPPPPP NNNNN
        code = "02"
        name = ""  # Account holder name not needed
        acc = self._format_account(from_account)
        amt = self._format_amount(amount)
        misc = self._format_account(to_account)  # To-account in misc field
        
        transaction = f"{code} {name:<20} {acc} {amt} {misc}"
        self.transactions.append(transaction)
    
    def log_paybill(self, account_number, amount, company_code):
        """
        Record paybill transaction (code 03)
        
        Args:
            account_number: Account number paying the bill
            amount: Amount paid
            company_code: EC, CQ, or FI (goes in misc field)
        """
        # Format: 03 AAAAAAAAAAAAAAAAAAAA NNNNN PPPPPPPP CC
        code = "03"
        name = ""  # Account holder name not needed
        acc = self._format_account(account_number)
        amt = self._format_amount(amount)
        misc = f"{company_code:<4}"  # Company code in misc field
        
        transaction = f"{code} {name:<20} {acc} {amt} {misc}"
        self.transactions.append(transaction)
    
    def log_deposit(self, account_number, amount):
        """
        Record deposit transaction (code 04)
        
        Args:
            account_number: Account number receiving deposit
            amount: Amount deposited
        """
        # Format: 04 AAAAAAAAAAAAAAAAAAAA NNNNN PPPPPPPP (spaces)
        code = "04"
        name = ""  # Account holder name not needed
        acc = self._format_account(account_number)
        amt = self._format_amount(amount)
        misc = " " * 4  # Empty misc field
        
        transaction = f"{code} {name:<20} {acc} {amt} {misc}"
        self.transactions.append(transaction)
    
    def log_create(self, account_number, amount):
        """
        Record account creation transaction (code 05)
        
        Args:
            account_number: New account number
            amount: Initial balance
        """
        # Format: 05 AAAAAAAAAAAAAAAAAAAA NNNNN PPPPPPPP SP
        code = "05"
        name = ""  # Account holder name from account object
        acc = self._format_account(account_number)
        amt = self._format_amount(amount)
        misc = "SP  "  # Student plan in misc field
        
        transaction = f"{code} {name:<20} {acc} {amt} {misc}"
        self.transactions.append(transaction)
    
    def log_delete(self, account_number):
        """
        Record account deletion transaction (code 06)
        
        Args:
            account_number: Account being deleted
        """
        # Format: 06 AAAAAAAAAAAAAAAAAAAA NNNNN 00000.00 (spaces)
        code = "06"
        name = ""  # Account holder name from account object
        acc = self._format_account(account_number)
        amt = "00000.00"  # Zero amount for delete
        misc = " " * 4  # Empty misc field
        
        transaction = f"{code} {name:<20} {acc} {amt} {misc}"
        self.transactions.append(transaction)
    
    def log_disable(self, account_number):
        """
        Record account disable transaction (code 07)
        
        Args:
            account_number: Account being disabled
        """
        # Format: 07 AAAAAAAAAAAAAAAAAAAA NNNNN 00000.00 (spaces)
        code = "07"
        name = ""  # Account holder name from account object
        acc = self._format_account(account_number)
        amt = "00000.00"  # Zero amount for disable
        misc = " " * 4  # Empty misc field
        
        transaction = f"{code} {name:<20} {acc} {amt} {misc}"
        self.transactions.append(transaction)
    
    def log_change_plan(self, account_number):
        """
        Record change plan transaction (code 08)
        
        Args:
            account_number: Account changing from SP to NP
        """
        # Format: 08 AAAAAAAAAAAAAAAAAAAA NNNNN 00000.00 NP
        code = "08"
        name = ""  # Account holder name from account object
        acc = self._format_account(account_number)
        amt = "00000.00"  # Zero amount for change plan
        misc = "NP  "  # New plan in misc field
        
        transaction = f"{code} {name:<20} {acc} {amt} {misc}"
        self.transactions.append(transaction)
    
    def write_to_file(self, filename):
        """
        Write all transactions to file with end-of-session marker
        
        Args:
            filename: Output file name (e.g., "daily_transaction.txt")
        """
        try:
            with open(filename, 'w') as f:
                # Write all stored transactions
                for transaction in self.transactions:
                    f.write(transaction + '\n')
                
                # Write end-of-session marker (code 00)
                end_marker = "00" + " " * 38  # 00 + 38 spaces = 40 chars
                f.write(end_marker + '\n')
            
            print(f"Successfully wrote {len(self.transactions)} transactions to {filename}")
            
        except Exception as e:
            print(f"ERROR: Could not write to file {filename}: {e}")
    
    def get_transaction_count(self):
        """Return number of transactions logged"""
        return len(self.transactions)
    
    def _format_account(self, account_number):
        """
        Format account number to 5 digits, zero-filled
        
        Args:
            account_number: Raw account number (string or int)
        Returns:
            5-character string, zero-filled
        """
        # Remove any non-digit characters and convert to int
        if isinstance(account_number, str):
            # Extract digits only
            digits = ''.join(filter(str.isdigit, account_number))
            if digits:
                num = int(digits)
            else:
                num = 0
        else:
            num = int(account_number)
        
        # Format as 5 digits with leading zeros
        return f"{num:05d}"
    
    def _format_amount(self, amount):
        """
        Format amount to 8 characters with .00, right-justified
        
        Args:
            amount: Dollar amount (float or int)
        Returns:
            8-character string, e.g., "00110.00"
        """
        # Convert to float and ensure 2 decimal places
        amt_float = float(amount)
        
        # Format as 8 characters with leading zeros
        # Example: 110.00 -> "00110.00"
        dollars = int(amt_float)
        cents = int(round((amt_float - dollars) * 100))
        
        # Handle rounding issues
        if cents >= 100:
            dollars += 1
            cents -= 100
        
        # Format with leading zeros
        return f"{dollars:05d}.{cents:02d}"