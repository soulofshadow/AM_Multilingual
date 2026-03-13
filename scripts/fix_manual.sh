#!/bin/bash
set -e  

echo "***************************************************************************************"
echo "⚠️   Make sure you have updated the failed_log.csv file with the necessary corrections."
echo "***************************************************************************************"

echo "▶ Step 1: manual_repair.py"
python3 -m src.manual_repair

echo "▶ Step 2: write_library.py"
python3 -m src.write_library

echo "✅ All done!"
