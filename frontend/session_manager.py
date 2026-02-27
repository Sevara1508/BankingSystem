"""
Session Manager Module

This module defines the SessionManager class, which is responsible for:
- tracking front end session state
- including login status 
- session mode
- per-session transaction limits

The SessionManager does not perform transaction logic. It only stores and validates session-related information.

"""
class SessionManager:
    """
    SessionManager

    Manages login state, session mode, per-session constraints for the banking system front end. 

    """

    STANDARD_WITHDRAWAL_LIMIT = 500.00
    STANDARD_TRANSFER_LIMIT = 1000.00
    STANDARD_PAYBILL_LIMIT = 2000.00

    def __init__(self):
        """
        Initialize a new SessionManager.

        Starts with no active session.

        """

        self.logged_in = False
        self.session_mode = None #Standard or Admin           
        self.current_user_name = None
        self.withdrawal_total = 0.0
        self.transfer_total = 0.0
        self.paybill_total = 0.0
        
        # For compatibility with TransactionProcessor
        self.withdrawal_limit = self.STANDARD_WITHDRAWAL_LIMIT
        self.transfer_limit = self.STANDARD_TRANSFER_LIMIT
        self.paybill_limit = self.STANDARD_PAYBILL_LIMIT

    def login(self, is_admin=False, user_name=None):
        """
        Start a session (standard or admin).
        
        :param is_admin: True for admin session, False for standard
        :param user_name: Name of account holder (for standard mode only)
        """
        if is_admin:
            self.start_admin_session()
        else:
            self.start_standard_session(user_name)

    def start_standard_session(self, user_name):
        """
        Start a standard session.

        :param user_name: Name of the account holder

        """

        self.logged_in = True
        self.session_mode = "standard"
        self.current_user_name = user_name
        self.withdrawal_total = 0.0
        self.transfer_total = 0.0
        self.paybill_total = 0.0

    def start_admin_session(self):
        """
        Start an admin session.

        """

        self.logged_in = True
        self.session_mode = "admin"
        self.current_user_name = None
        self.withdrawal_total = 0.0
        self.transfer_total = 0.0
        self.paybill_total = 0.0

    def logout(self):
        """
        End the current session and reset all session state.
        Alias for end_session() for compatibility.
        """
        self.end_session()

    def end_session(self):
        """
        End the current session and reset all session state.
    
        """

        self.logged_in = False
        self.session_mode = None
        self.current_user_name = None
        self.withdrawal_total = 0.0
        self.transfer_total = 0.0
        self.paybill_total = 0.0

    def is_logged_in(self):
        """
        Check whether a session is currently active.

        :return: True if logged in, False otherwise

        """

        return self.logged_in

    def is_admin(self):
        """
        Check whether the current session is admin mode.
        Alias for is_admin_mode() for compatibility.

        :return: True if admin session, False otherwise

        """
        return self.is_admin_mode()

    def is_admin_mode(self):
        """
        Check whether the current session is admin mode.

        :return: True if admin session, False otherwise

        """

        return self.session_mode == "admin"

    def get_current_user(self):
        """
        Get the name of the currently logged-in user.
        
        :return: Username for standard mode, None for admin mode
        """
        return self.current_user_name

    def can_withdraw(self, amount):
        """
        Validate whether a withdrawal is allowed under session rules.

        :param amount: Withdrawal amount
        :return: True if allowed, False otherwise

        """

        if self.session_mode == "admin":
            return True

        projected_total = self.withdrawal_total + amount

        if projected_total > self.STANDARD_WITHDRAWAL_LIMIT:
            return False

        return True

    def record_withdrawal(self, amount):
        """
        Record a withdrawal toward session limits.

        :param amount: Withdrawal amount
        
        """

        self.withdrawal_total += amount

    def can_transfer(self, amount):
        """
        Validate whether a transfer is allowed under session rules.

        :param amount: Transfer amount
        :return: True if allowed, False otherwise

        """

        if self.session_mode == "admin":
            return True

        projected_total = self.transfer_total + amount

        if projected_total > self.STANDARD_TRANSFER_LIMIT:
            return False

        return True

    def record_transfer(self, amount):
        """
        Record a transfer toward session limits.

        :param amount: Transfer amount
        
        """

        self.transfer_total += amount

    def can_pay_bill(self, amount):
        """
        Validate whether a bill payment is allowed under session rules.

        :param amount: Payment amount
        :return: True if allowed, False otherwise

        """

        if self.session_mode == "admin":
            return True

        projected_total = self.paybill_total + amount

        if projected_total > self.STANDARD_PAYBILL_LIMIT:
            return False

        return True

    def record_pay_bill(self, amount):
        """
        Record a bill payment toward session limits.

        :param amount: Payment amount
        
        """

        self.paybill_total += amount