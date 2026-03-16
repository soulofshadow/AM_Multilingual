#!/bin/bash
set -e

PROJECT=$(pwd)

cd "$PROJECT"
bash scripts/fix_manual.sh

if [ -f "$PROJECT/data/needs_review.csv" ]; then
    NEED_COUNT=$(python3 -c "
import csv
with open('$PROJECT/data/needs_review.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))
    print(len(rows) // 2 if rows else 0)
")
    
    if [ "$NEED_COUNT" -eq 0 ]; then
        echo "All fixed successfully, no needs review."
    else
        echo "$NEED_COUNT needs review: data/needs_review.csv"
    fi
else
    echo "All fixed successfully"
fi