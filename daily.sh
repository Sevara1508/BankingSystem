#!/bin/bash
# =============================================================================
# daily.sh – CSCI 3060U Phase 6: Daily Banking System Script
# Group 21: Bushrat Zahan, Menhdi Patel, Sevara Omonova, Nabiha Shah
#
# Implements Phase 6 spec:
#   (i)  Runs the Front End over a number of transaction sessions, saving
#        each session's Bank Account Transaction File in a separate file.
#   (ii) Concatenates all session files into a Merged Daily Bank Account
#        Transaction File.
#  (iii) Runs the Back End with the merged file as input.
#
# USAGE (run from repo root):
#   ./daily.sh <current_accounts> <master_accounts> <output_dir> <input_dir>
#
#   current_accounts – 37-char Current Bank Accounts File for the Front End
#                      e.g., frontend/current_accounts.txt  (Day 1 initial)
#                      or    outputs/dayN/new_current.baf   (Day N+1 chained)
#   master_accounts  – 45-char Master Bank Accounts File for the Back End
#                      e.g., backend/old_master.txt         (Day 1 initial)
#                      or    outputs/dayN/new_master.baf    (Day N+1 chained)
#   output_dir       – Directory for all output files (created if needed)
#   input_dir        – Directory containing session input files:
#                        session1.txt, session2.txt, session3.txt, ...
#                      Any missing session file runs interactively.
#
# OUTPUT FILES written into <output_dir>:
#   session1.atf  session2.atf  session3.atf   – Per-session transaction files
#   merged.atf                                  – Merged input for Back End
#   new_master.baf                              – New 45-char Master Accounts
#   new_current.baf                             – New 37-char Current Accounts
# =============================================================================

# --------------------------------------------------------------------------
# Configuration – update PYTHON if your system uses a different command
# --------------------------------------------------------------------------
PYTHON="python3"                         # or "python" if python3 is not found
FRONTEND="frontend/main.py"             # relative to repo root
BACKEND="backend/main.py"              # relative to repo root  
NUM_SESSIONS=6                           # number of Front End sessions per day

# --------------------------------------------------------------------------
# Argument validation
# --------------------------------------------------------------------------
if [ "$#" -lt 4 ]; then
    echo "Usage: $0 <current_accounts> <master_accounts> <output_dir> <input_dir>"
    echo ""
    echo "Example:"
    echo "  ./daily.sh frontend/current_accounts.txt backend/old_master.txt \\"
    echo "             outputs/day1 inputs/day1"
    exit 1
fi

CURRENT_ACCOUNTS="$1"
MASTER_ACCOUNTS="$2"
OUTPUT_DIR="$3"
INPUT_DIR="$4"

if [ ! -f "$CURRENT_ACCOUNTS" ]; then
    echo "ERROR: Current accounts file not found: $CURRENT_ACCOUNTS"
    exit 1
fi
if [ ! -f "$MASTER_ACCOUNTS" ]; then
    echo "ERROR: Master accounts file not found: $MASTER_ACCOUNTS"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

# --------------------------------------------------------------------------
# Step (i): Run Front End sessions
# --------------------------------------------------------------------------
echo "=== Running $NUM_SESSIONS Front End session(s) ==="

SESSION_ATF_LIST=""     # space-separated list of produced ATF files

for i in $(seq 1 $NUM_SESSIONS); do
    SESSION_ATF="$OUTPUT_DIR/session${i}.atf"
    SESSION_INPUT="$INPUT_DIR/session${i}.txt"

    echo ""
    echo "--- Session $i ---"

    if [ -f "$SESSION_INPUT" ]; then
        echo "  Input file : $SESSION_INPUT"
        echo "  Output ATF : $SESSION_ATF"
        # frontend/main.py takes argv[1]=accounts_file, argv[2]=output_atf
        # stdin is redirected from the session input file
        $PYTHON "$FRONTEND" "$CURRENT_ACCOUNTS" "$SESSION_ATF" < "$SESSION_INPUT"
    else
        echo "  No input file found at $SESSION_INPUT — running interactively."
        echo "  Use banking commands. Type 'logout' then 'quit' to end."
        $PYTHON "$FRONTEND" "$CURRENT_ACCOUNTS" "$SESSION_ATF"
    fi

    # Confirm the ATF was written; if not, insert a placeholder so merge works
    if [ ! -f "$SESSION_ATF" ]; then
        echo "  WARNING: ATF not produced for session $i — inserting empty session."
        printf "00                                      \n" > "$SESSION_ATF"
    fi

    SESSION_ATF_LIST="$SESSION_ATF_LIST $SESSION_ATF"
done

# --------------------------------------------------------------------------
# Step (ii): Concatenate session files into Merged Daily Bank Account
#            Transaction File, then append a final empty end-of-session
#            record as required by the spec.
# --------------------------------------------------------------------------
echo ""
echo "=== Merging transaction files ==="

MERGED_ATF="$OUTPUT_DIR/merged.atf"
> "$MERGED_ATF"   # start fresh

for atf in $SESSION_ATF_LIST; do
    cat "$atf" >> "$MERGED_ATF"
done

# Append the required final empty end-of-session record (code 00, padded to 40)
printf "%-40s\n" "00" >> "$MERGED_ATF"

echo "Merged ATF: $MERGED_ATF"

# --------------------------------------------------------------------------
# Step (iii): Run Back End
# --------------------------------------------------------------------------
echo ""
echo "=== Running Back End ==="

NEW_MASTER="$OUTPUT_DIR/new_master.baf"
NEW_CURRENT="$OUTPUT_DIR/new_current.baf"

# backend/main.py: argv[1]=old_master, argv[2]=merged_txn,
#                  argv[3]=new_master,  argv[4]=new_current
$PYTHON "$BACKEND" "$MASTER_ACCOUNTS" "$MERGED_ATF" "$NEW_MASTER" "$NEW_CURRENT"

if [ "$?" -ne 0 ]; then
    echo "ERROR: Back End failed. Check output above."
    exit 1
fi

# --------------------------------------------------------------------------
# Summary
# --------------------------------------------------------------------------
echo ""
echo "=== Daily run complete ==="
echo "  New Master Bank Accounts File  : $NEW_MASTER"
echo "  New Current Bank Accounts File : $NEW_CURRENT"
