"""
Main Entry Point for Banking System Front End

Loads accounts and runs FrontEndApp.
"""

from account_manager import AccountManager
from front_end_app import FrontEndApp

import sys
sys.stdout.reconfigure(encoding='utf-8') #to fix checkmark error

def main():
    """Main function to run the banking system front end."""

    accounts_file = sys.argv[1] if len(sys.argv) > 1 else "current_accounts.txt"
    transaction_file = sys.argv[2] if len(sys.argv) > 2 else "daily_transaction.txt"

    # Print header
    print("=" * 80)
    
    # Load accounts from file
    account_manager = AccountManager()
    try:
        account_manager.load_from_file(accounts_file)
        print("✓ Accounts loaded successfully")
        print(f"✓ {len(account_manager.accounts)} accounts available")
    except FileNotFoundError:
        print(f"ERROR: {accounts_file} not found!")
        print("Make sure the file is in the same folder as this script.")
        return
    
    # Print available commands menu
    print("\n" + "=" * 80)
    print("AVAILABLE COMMANDS:")
    print("=" * 80)
    print("login       - Start a session")
    print("withdrawal  - Withdraw money")
    print("transfer    - Transfer money between accounts")
    print("paybill     - Pay a bill")
    print("deposit     - Deposit money")
    print("create      - Create account (admin only)")
    print("delete      - Delete account (admin only)")
    print("disable     - Disable account (admin only)")
    print("changeplan  - Change plan SP→NP (admin only)")
    print("logout      - End session")
    print("quit        - Exit program")
    print("=" * 80)
    print()
    
    # Create and run FrontEndApp
    app = FrontEndApp(account_manager, transaction_file)
    app.main()


if __name__ == "__main__":
    main()