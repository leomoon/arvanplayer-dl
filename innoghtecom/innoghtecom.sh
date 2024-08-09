#!/bin/bash

# Check if the input file is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <input_file>"
    exit 1
fi

input_file="$1"

# Check if the input file exists
if [ ! -f "$input_file" ]; then
    echo "Error: Input file '$input_file' not found."
    exit 1
fi

# Check if the Python script exists
python_script="download.py"
if [ ! -f "$python_script" ]; then
    echo "Error: Python script '$python_script' not found in the current directory."
    exit 1
fi

# Process each line in the input file
while IFS=' ' read -r url output_name || [[ -n "$url" ]]; do
    if [[ -n "$url" && -n "$output_name" ]]; then
        echo "Processing: $url -> $output_name"
        .venv/bin/python "$python_script" "$url" "$output_name"

        # Check the exit status of the Python script
        if [ $? -eq 0 ]; then
            echo "Download completed successfully: $output_name"
        else
            echo "Error occurred while processing: $url -> $output_name"
        fi

        echo "-----------------------------------"
    fi
done < "$input_file"

echo "All downloads completed."