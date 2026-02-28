#!/usr/bin/env bash
INPUT_DIR="inputs"
OUTPUT_DIR="outputs"
ACCOUNTS="../frontend/current_accounts.txt"

mkdir -p "$OUTPUT_DIR"
echo "===== RUNNING TESTS ====="

for f in "$INPUT_DIR"/*.txt; do
  name=$(basename "$f" .txt)
  echo "Running test: $name"
  python3 ../frontend/main.py "$ACCOUNTS" "$OUTPUT_DIR/$name.atf" < "$f" > "$OUTPUT_DIR/$name.out"
  echo "Saved outputs for $name"
  echo "----------------------"
done

echo "DONE. Outputs stored in $OUTPUT_DIR"
