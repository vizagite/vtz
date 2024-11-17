#!/bin/bash

input_csv="output.csv"
output_csv="sorted_output.csv"

temp_csv=$(mktemp)
month_order="jan feb mar apr may jun jul aug sep oct nov dec"

head -n 1 "$input_csv" > "$output_csv"

tail -n +2 "$input_csv" | awk -F, -v month_order="$month_order" '
BEGIN {
    # Define the month order
    split(month_order, month_array, " ")
    for (i in month_array) {
        month_map[month_array[i]] = i
    }
}
{
    # Convert month to numeric value for sorting
    month_num = month_map[$2]
    printf "%s,%02d,%s,%s,%s,%s\n", $1, month_num, $3, $4, $2, $0
}' | sort -t, -k1,1n -k2,2n -k3,3n | cut -d, -f6- > "$temp_csv"

cat "$temp_csv" >> "$output_csv"

rm "$temp_csv"