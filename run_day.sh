#!/bin/bash
# run_day.sh — Works with files in frontend/ and backend/ folders

echo "=== FRONT END: Users do transactions ==="
# Run front end; waits until user types 'quit'
python frontend/main.py frontend/current_accounts.txt frontend/daily_transaction.txt

echo "=== BACK END: Applying transactions ==="
# Run back end to update master and current accounts
python backend/main.py backend/old_master.txt frontend/daily_transaction.txt backend/new_master.txt frontend/new_current.txt

echo "=== Rolling over files for next day ==="
# Replace old files with new ones
cp frontend/new_current.txt frontend/current_accounts.txt
cp backend/new_master.txt backend/old_master.txt

echo "✅ Done! Next day is ready."