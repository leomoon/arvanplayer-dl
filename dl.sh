#!/bin/bash

# Check if the correct number of arguments is provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <url_file> <dest_dir>"
    exit 1
fi

# File containing the URLs
url_file="$1"

# Destination directory
dest_dir="$2"

# Check if the URL file exists
if [ ! -f "$url_file" ]; then
    echo "File not found: $url_file"
    exit 1
fi

# Create the destination directory if it doesn't exist
mkdir -p "$dest_dir"

# Initialize the counter for downloaded JSON files
json_counter=1

# Download each JSON file
while IFS= read -r url || [ -n "$url" ]; do
    # Calculate the file number with leading zeros
    json_file_num=$(printf "%02d" $json_counter)
    # Get the file extension from the URL
    json_extension="${url##*.}"
    # Download the JSON file
    echo "[i] Downloading $url >>> ${dest_dir}/${json_file_num}.${json_extension}"
    curl -s -o "${dest_dir}/${json_file_num}.${json_extension}" "$url"
    # Increment the counter
    ((json_counter++))
done < "$url_file"

echo "JSON files download complete."

# Process each JSON file in the destination directory
i=1
for file in "$dest_dir"/*.json; do
    if [ -f "$file" ]; then
        # Extract the src URL from the JSON file
        src_url=$(jq -r '.source[0].src' "$file")
        # Get the file extension from the URL
        extension="${src_url##*.}"
        # Calculate the file number with leading zeros
        file_num=$(printf "%02d" $i)
        # Download the file and save it in the same directory with the correct extension
        echo "[i] Downloading $src_url >>> ${dest_dir}/${file_num}.${extension}"
        curl -s -o "${dest_dir}/${file_num}.${extension}" "$src_url"
        # Increment the counter
        ((i++))
    fi
done

echo "M3U8 files download complete."

# Process each downloaded M3U8 file to find the last M3U8 line and run the Python script
i=1
for file in "$dest_dir"/*.m3u8; do
    if [ -f "$file" ]; then
        # Find the last line in the M3U8 file that contains ".m3u8"
        last_m3u8_line=$(grep '\.m3u8$' "$file" | tail -n 1)

        # Get the corresponding JSON file and its src URL
        json_file=$(printf "%02d.json" $i)
        src_url=$(jq -r '.source[0].src' "$dest_dir/$json_file")
        base_url=$(dirname "$src_url")

        # Construct the new URL
        new_url="${base_url}/${last_m3u8_line}"
        # echo "[i] New URL for $json_file: $new_url"

        # Run the Python script to download the video
        output_file=$(printf "%02d.mp4" $i)
        echo "[i] Running: python3 dl.py \"$new_url\" \"$dest_dir/$output_file\""
        python3 dl.py "$new_url" "$dest_dir/$output_file"

        # Increment the counter
        ((i++))
    fi
done

echo "Processing complete."
