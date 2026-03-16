#!/bin/bash
set -e

PROJECT=$(pwd)
LOCK="$PROJECT/am_fixer.lock"

# 1. If it is running, exit directly
if [ -f "$LOCK" ]; then
    echo "Already running, skipping."
    exit 0
fi

# 2. Hold
sleep 1

# 3. Check agains
if [ -f "$LOCK" ]; then
    echo "Already running after sleep, skipping."
    exit 0
fi

# 4. Create lock
touch "$LOCK"
trap "rm -f '$LOCK'" EXIT

# 5. Run the fixer
cd "$PROJECT"
bash scripts/fix_gemini.sh

# 6. Read the log and notify
if [ -f "$PROJECT/data/needs_review.csv" ]; then
    NEED_COUNT=$(python3 -c "
import csv
with open('$PROJECT/data/needs_review.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))
    print(len(rows) // 2 if rows else 0)
")
    
    if [ "$NEED_COUNT" -eq 0 ]; then
        echo "All fixed successfully"
    else
        echo "$NEED_COUNT needs review: data/needs_review.csv"
    fi
else
    echo "All fixed successfully"
fi


# 7. Remove lock
rm -f "$LOCK"