#!/bin/bash

# Check if a directory argument is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

# Directory containing MP4 files
input_dir="$1"

# Iterate over all MP4 files in the input directory
for file in "$input_dir"/*.mp4; do
    # Check if there are any MP4 files
    if [ ! -e "$file" ]; then
        echo "No MP4 files found in the specified directory."
        exit 1
    fi

    # Extract the base name of the file (without extension)
    base_name=$(basename "$file" .mp4)

    # Define the output file path
    output_file="$input_dir/$base_name.mp3"

    # Convert the MP4 file to MP3 with a bitrate of 256 kbps
    ffmpeg -i "$file" -b:a 256k "$output_file"
done

echo "Conversion complete!"
