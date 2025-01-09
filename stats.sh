#!/bin/bash

DIR="./data/accounts"

# Print the header with nice formatting
echo -e "Email\t\t\t\tTotal_Earnings"
echo -e "-----------------------------------------------------"

# Collect data to create a structured format for column
output=""

for file in "$DIR"/*; do
    if [[ -f $file ]]; then
        email=$(awk -F= '/^Email=/{print $2}' "$file")
        earnings=$(awk -F= '/^Total_Earnings=/{print $2}' "$file")
        if [[ -n $email && -n $earnings ]]; then
            output+="$email\t$earnings\n"
        fi
    fi
done

# Use column to format the output
echo -e "$output" | column -t -s $'\t'