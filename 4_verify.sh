#!/bin/bash

input_csv="final_output.csv"

declare -A data_map

while IFS=, read -r year month pax pax_lastyr; do
    if [[ "$year" == "Year" ]]; then
        continue
    fi
    pax=$(echo "$pax" | tr -d '[:space:]' | tr -d '\n')  # Strip all spaces and newlines
    pax_lastyr=$(echo "$pax_lastyr" | tr -d '[:space:]' | tr -d '\n')  # Same for pax_lastyr
    
    data_map["$year,$month"]="$pax,$pax_lastyr"
done < "$input_csv"

echo "Verification Results:"
echo "---------------------"
for key in "${!data_map[@]}"; do
    year=$(echo "$key" | cut -d',' -f1)
    month=$(echo "$key" | cut -d',' -f2)

    current_pax=$(echo "${data_map[$year,$month]}" | cut -d',' -f1)

    next_year=$((year + 1))
    next_year_pax_lastyr=$(echo "${data_map[$next_year,$month]}" | cut -d',' -f2)

    if [[ -n "$next_year_pax_lastyr" ]]; then
        if [[ "$current_pax" -eq "$next_year_pax_lastyr" ]]; then
            :
        else
            echo "Mismatch found: Year=$year, Month=$month, Pax=$current_pax, Next Year PaxLastyr=$next_year_pax_lastyr"
        fi
    else
        :
    fi
done


# Verification Results:
# ---------------------
# Mismatch found: Year=2013, Month=mar, Pax=75414, Next Year PaxLastyr=75405
# Mismatch found: Year=2011, Month=jul, Pax=70858, Next Year PaxLastyr=70859
# Mismatch found: Year=2014, Month=sep, Pax=91992, Next Year PaxLastyr=91965
# Mismatch found: Year=2011, Month=apr, Pax=61567, Next Year PaxLastyr=61559
# Mismatch found: Year=2020, Month=jul, Pax=39917, Next Year PaxLastyr=39914
# Mismatch found: Year=2008, Month=oct, Pax=51564, Next Year PaxLastyr=51657
# Mismatch found: Year=2015, Month=apr, Pax=111920, Next Year PaxLastyr=111919

# Mismatch found: Year=2014, Month=jul - flipped domestic international