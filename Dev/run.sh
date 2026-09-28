#!/bin/bash
cd "$(dirname "$0")"
uv run python ../app.py --file ../assets/Budget.xlsx
read -p "Press enter to continue..."