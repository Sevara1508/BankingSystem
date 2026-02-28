#!/usr/bin/env bash
shopt -s nullglob

# root = project root (two levels up from tests/scripts/)
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

EXPECTED_DIR="$ROOT_DIR/tests/expected"
OUTPUT_DIR="$ROOT_DIR/tests/outputs"
INPUT_DIR="$ROOT_DIR/tests/inputs"

PASS=0
FAIL=0

echo "===== CHECKING OUTPUTS ====="

for f in "$INPUT_DIR"/*.txt; do
  name=$(basename "$f" .txt)
  FAILED=0

  # ---- terminal output (.out) ----
  if [ ! -f "$EXPECTED_DIR/$name.out" ]; then
    echo "$name: FAIL (missing expected .out file: $EXPECTED_DIR/$name.out)"
    FAIL=$((FAIL+1))
    echo "----------------------"
    continue
  fi

  if [ ! -f "$OUTPUT_DIR/$name.out" ]; then
    echo "$name: FAIL (missing actual .out file: $OUTPUT_DIR/$name.out)"
    FAIL=$((FAIL+1))
    echo "----------------------"
    continue
  fi

  if ! diff -q "$OUTPUT_DIR/$name.out" "$EXPECTED_DIR/$name.out" >/dev/null 2>&1; then
    echo "$name: FAIL (terminal output mismatch)"
    diff "$OUTPUT_DIR/$name.out" "$EXPECTED_DIR/$name.out"
    FAILED=1
  fi

  # ---- transaction file (.atf) ----
  # only check if an expected .atf exists
  if [ -f "$EXPECTED_DIR/$name.atf" ]; then
    if [ ! -f "$OUTPUT_DIR/$name.atf" ]; then
      echo "$name: FAIL (missing actual .atf file: $OUTPUT_DIR/$name.atf)"
      FAILED=1
    elif ! diff -q "$OUTPUT_DIR/$name.atf" "$EXPECTED_DIR/$name.atf" >/dev/null 2>&1; then
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