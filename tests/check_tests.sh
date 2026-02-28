#!/usr/bin/env bash
EXPECTED_DIR="expected"
OUTPUT_DIR="outputs"
INPUT_DIR="inputs"
PASS=0
FAIL=0

echo "===== CHECKING OUTPUTS ====="

for f in "$INPUT_DIR"/*.txt; do
  name=$(basename "$f" .txt)
  FAILED=0

  # Check .out file
  if [ ! -f "$OUTPUT_DIR/$name.out" ]; then
    echo "$name: FAIL (missing output file)"
    FAIL=$((FAIL+1))
    echo "----------------------"
    continue
  fi

  if ! diff -q "$OUTPUT_DIR/$name.out" "$EXPECTED_DIR/$name.out" >/dev/null 2>&1; then
    echo "$name: FAIL (terminal output mismatch)"
    diff "$OUTPUT_DIR/$name.out" "$EXPECTED_DIR/$name.out"
    FAILED=1
  fi

  # Only check .atf if expected file exists
  if [ -f "$EXPECTED_DIR/$name.atf" ]; then
    if ! diff -q "$OUTPUT_DIR/$name.atf" "$EXPECTED_DIR/$name.atf" >/dev/null 2>&1; then
      echo "$name: FAIL (transaction file mismatch)"
      diff "$OUTPUT_DIR/$name.atf" "$EXPECTED_DIR/$name.atf"
      FAILED=1
    fi
  fi

  if [ $FAILED -eq 0 ]; then
    echo "$name: PASS"
    PASS=$((PASS+1))
  else
    FAIL=$((FAIL+1))
  fi

  echo "----------------------"
done

echo "===== TEST SUMMARY ====="
echo "Total PASS: $PASS"
echo "Total FAIL: $FAIL"
check_tests.sh
