#!/bin/bash

DIR="./data/accounts"
echo -e "Email\tTotal_Earnings"

for file in "$DIR"/*; do
    if [[ -f $file ]]; then
        email=$(awk -F= '/^Email=/{print $2}' "$file")
        earnings=$(awk -F= '/^Total_Earnings=/{print $2}' "$file")
        if [[ -n $email && -n $earnings ]]; then
            echo -e "$email\t$earnings"
        fi
    fi
done