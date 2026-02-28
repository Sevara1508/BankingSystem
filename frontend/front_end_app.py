"""
Front End Application Module

This module defines the FrontEndApp class, which serves as the main entry point for the banking system front end.

The FrontEndApp is responsible for:
- Reading transaction commands from standard input
- Printing system responses to standard output
- Delegating transaction handling to the TransactionProcessor

"""

from session_manager import SessionManager
from account_manager import AccountManager
from TransactionProcessor import TransactionProcessor
from TransactionLog import TransactionLog


class FrontEndApp:
    """
    FrontEndApp

    Coordinates user interaction and transaction processing for the
    banking system front end.

    """

    def __init__(self, account_manager):
        """
        Initialize the FrontEndApp.

        :param account_manager: Instance of AccountManager with loaded accounts

        """
        self.account_manager = account_manager
        self.session_manager = SessionManager()
        self.transaction_log = TransactionLog()
        self.transaction_processor = TransactionProcessor(
            self.session_manager,
            self.account_manager,
            self.transaction_log
        )

    def main(self):
        """
        Main execution loop for the front end.

        Continuously reads commands from standard input until EOF or quit.

        """
        while True:
            try:
                command = input("Enter command: ").strip().lower()
                
                if not command:
                    continue
                
                if command == "quit":
                    print("\nExiting banking system. Goodbye!")
                    break
                    
                self.dispatch_command(command)
                
            except EOFError:
                print("\nEnd of input. Exiting.")
                break
            except KeyboardInterrupt:
                print("\n\nInterrupted. Exiting.")
                break

    def dispatch_command(self, command):
        """
        Interpret and route a transaction command.

        :param command: Transaction code entered by user

        """
        if command == "login":
            self.handle_login()

        elif command == "logout":
            self.transaction_processor.process_logout()

        elif command == "withdrawal":
            self.transaction_processor.process_withdrawal()

        elif command == "transfer":
            self.transaction_processor.process_transfer()

        elif command == "paybill":
            self.transaction_processor.process_paybill()

        elif command == "deposit":
            self.transaction_processor.process_deposit()

        elif command == "create":
            self.transaction_processor.process_create()

        elif command == "delete":
            self.transaction_processor.process_delete()

        elif command == "disable":
            self.transaction_processor.process_disable()

        elif command == "changeplan":
            self.transaction_processor.process_change_plan()

        else:
            print(f"ERROR: Unknown command '{command}'")
            print("Valid commands: login, logout, withdrawal, transfer, paybill, deposit, create, delete, disable, changeplan")

    def handle_login(self):
        """
        Handle login transaction input sequence.
        Asks for session type and delegates to appropriate processor method.

        """
        if self.session_manager.is_logged_in():
            print("ERROR: Already logged in. Please logout first.")
            return

        session_type = input("Session type (standard/admin): ").strip().lower()

        if session_type == "standard":
            # Get username for standard login
            user_name = input("Enter your name: ").strip()

            # ADD THIS VALIDATION - INDENTED CORRECTLY INSIDE THE IF BLOCK
            if not self.account_manager.user_exists(user_name):
                print(f"ERROR: User '{user_name}' does not have any accounts")
                return
                
            # Start session in SessionManager
            self.session_manager.start_standard_session(user_name)
            print(f"Login successful. Standard mode.")

        elif session_type == "admin":
            # Start admin session
            self.session_manager.start_admin_session()
            print("Login successful. Admin mode.")

        else:
            print("ERROR: Invalid session type. Must be 'standard' or 'admin'")