"""
BankAccount Module

CLASS: BankAccount
DESCRIPTION: Represents a single bank account with fields like accountNumber, 
name, status, balance, plan.

"""


class BankAccount:
    """
    BankAccount
    
    Represents a single bank account in the banking system.
    
    Attributes:
        account_number: 5-digit account number (string)
        holder_name: Name of account holder (max 20 chars)
        balance: Current balance in dollars
        status: Account status - 'A' (active) or 'D' (disabled)
        plan: Transaction plan - 'SP' (student) or 'NP' (non-student)
    """
    
    def __init__(self, account_number, holder_name, balance, status='A', plan='SP'):
        """
        Initialize a new BankAccount.
        
        Args:
            account_number: 5-digit account number
            holder_name: Name of the account holder
            balance: Initial balance
            status: 'A' for active or 'D' for disabled (default: 'A')
            plan: 'SP' for student plan or 'NP' for non-student (default: 'SP')
        """
        self.account_number = str(account_number).zfill(5)
        self.holder_name = str(holder_name).strip()[:20]  # Max 20 chars
        self.balance = float(balance)
        self.status = status if status in ['A', 'D'] else 'A'
        self.plan = plan if plan in ['SP', 'NP'] else 'SP'
    
    def withdraw(self, amount):
        """
        Deducts amount from balance if sufficient funds exist.
        
        Args:
            amount: Amount to withdraw
            
        Returns:
            True if withdrawal successful, False if insufficient funds
        """
        amount = float(amount)
        
        if amount <= 0:
            return False
        
        if self.balance >= amount:
            self.balance -= amount
            return True
        
        return False
    
    def deposit(self, amount):
        """
        Adds amount to balance.
        
        Args:
            amount: Amount to deposit
            
        Returns:
            True (deposits always succeed for valid amounts)
        """
        amount = float(amount)
        
        if amount <= 0:
            return False
        
        self.balance += amount
        return True
    
    def is_valid_for(self, user):
        """
        Returns True if account belongs to specified user AND account status is active (A).
        
        Args:
            user: Username to check ownership against
            
        Returns:
            True if account is valid for the user, False otherwise
        """
        if self.status != 'A':
            return False
        
        if user is None:
            return False
        
        return self.holder_name.strip() == str(user).strip()
    
    # Getters
    def get_account_number(self):
        """Return the account number."""
        return self.account_number
    
    def get_holder_name(self):
        """Return the account holder's name."""
        return self.holder_name
    
    def get_balance(self):
        """Return the current balance."""
        return self.balance
    
    def get_status(self):
        """Return the account status ('A' or 'D')."""
        return self.status
    
    def get_plan(self):
        """Return the transaction plan ('SP' or 'NP')."""
        return self.plan
    
    # Setters
    def set_account_number(self, account_number):
        """
        Set the account number.
        
        Args:
            account_number: New account number
        """
        self.account_number = str(account_number).zfill(5)
    
    def set_holder_name(self, holder_name):
        """
        Set the account holder's name.
        
        Args:
            holder_name: New holder name (max 20 chars)
        """
        self.holder_name = str(holder_name).strip()[:20]
    
    def set_balance(self, balance):
        """
        Set the account balance.
        
        Args:
            balance: New balance amount
        """
        self.balance = float(balance)
    
    def set_status(self, status):
        """
        Set the account status.
        
        Args:
            status: 'A' for active or 'D' for disabled
        """
        if status in ['A', 'D']:
            self.status = status
    
    def set_plan(self, plan):
        """
        Set the transaction plan.
        
        Args:
            plan: 'SP' for student plan or 'NP' for non-student
        """
        if plan in ['SP', 'NP']:
            self.plan = plan
    
    def __str__(self):
        """
        String representation of the account.
        
        Returns:
            Formatted string with account details
        """
        return (f"Account {self.account_number}: {self.holder_name}, "
                f"Balance: ${self.balance:.2f}, Status: {self.status}, Plan: {self.plan}")
    
    def __repr__(self):
        """
        Official string representation for debugging.
        
        Returns:
            String that could recreate the object
        """
        return (f"BankAccount(account_number='{self.account_number}', "
                f"holder_name='{self.holder_name}', balance={self.balance}, "
                f"status='{self.status}', plan='{self.plan}')")