#!/bin/bash

# Usage: ./get_cik.sh TICKER
# Example: ./get_cik.sh TMDX

# Check if ticker argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 TICKER"
  exit 1
fi

# Convert ticker to uppercase
ticker=$1

# Download the ticker file and search for the specified ticker
cik=$(grep -i "${ticker}" ticker.txt | awk '{printf "%010d", $2}')

# Check if CIK was found
if [ -n "$cik" ]; then
  echo $cik
  echo $cik | pbcopy
  echo "copied to clipboard!"
else
  echo "No CIK found for ${ticker}"
fi
