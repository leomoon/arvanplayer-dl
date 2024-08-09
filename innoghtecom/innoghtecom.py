import sys
import json
import requests
import time
import random
import os
import string
import shutil
from Crypto.Cipher import AES
from urllib.parse import urljoin

def debug_print(message):
    print(f"DEBUG: {message}")

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def decrypt(cipherbyte, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.decrypt(cipherbyte)

def download_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            debug_print(f"Error downloading {url}: {e}")
            if attempt < max_retries - 1:
                wait_time = random.uniform(1, 5)
                debug_print(f"Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            else:
                raise

def get_m3u8_content(url):
    debug_print(f"Fetching m3u8 content from: {url}")
    return download_with_retry(url).decode()

def get_highest_resolution_m3u8(m3u8_content, base_url):
    debug_print("Parsing master m3u8 for highest resolution")
    lines = m3u8_content.splitlines()
    for i, line in enumerate(lines):
        if "#EXT-X-STREAM-INF" in line and "RESOLUTION=1280x720" in line:
            return urljoin(base_url, lines[i+1].strip())
    raise ValueError("No 1280x720 resolution found in the m3u8 file")

def parse_m3u8(content):
    debug_print("Parsing m3u8 for key URI and segments")
    key_uri = None
    segments = []
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("#EXT-X-KEY"):
            key_uri = line.split('URI="')[1].split('"')[0]
        elif line.startswith("#EXTINF"):
            segments.append(lines[i+1])
    return key_uri, segments

def download_and_decrypt(config_url, output_name):
    debug_print(f"Starting download process with config URL: {config_url}")

    # Get config JSON
    config_response = requests.get(config_url)
    config = json.loads(config_response.text)
    debug_print(f"Config JSON parsed: {json.dumps(config, indent=2)}")

    # Get master m3u8 URL
    master_m3u8_url = config['source'][0]['src']
    base_url = '/'.join(master_m3u8_url.split('/')[:-1]) + '/'
    debug_print(f"Master m3u8 URL: {master_m3u8_url}")
    debug_print(f"Base URL: {base_url}")

    # Get master m3u8 content
    master_m3u8_content = get_m3u8_content(master_m3u8_url)

    # Get highest resolution m3u8 URL
    highest_res_m3u8_url = get_highest_resolution_m3u8(master_m3u8_content, base_url)
    debug_print(f"Highest resolution m3u8 URL: {highest_res_m3u8_url}")

    # Get content of highest resolution m3u8
    highest_res_m3u8_content = get_m3u8_content(highest_res_m3u8_url)

    # Parse m3u8 for key and segments
    key_uri, segments = parse_m3u8(highest_res_m3u8_content)
    debug_print(f"Key URI: {key_uri}")
    debug_print(f"Number of segments: {len(segments)}")

    # Download key
    debug_print(f"Downloading encryption key from: {key_uri}")
    key = download_with_retry(key_uri)
    debug_print(f"Encryption key downloaded. Length: {len(key)} bytes")
    iv = b"\x00" * 15 + b"\x01"  # IV from the m3u8 file
    debug_print(f"Using IV: {iv.hex()}")

    # Create a temporary directory with a random name for downloaded TS files
    temp_dir = f"temp_{generate_random_string()}"
    os.makedirs(temp_dir, exist_ok=True)
    debug_print(f"Created temporary directory: {temp_dir}")

    try:
        # Download TS files
        downloaded_files = []
        for i, segment in enumerate(segments, 1):
            segment_url = urljoin(base_url, segment)
            filename = os.path.join(temp_dir, f"segment_{i:04d}.ts")
            debug_print(f"Downloading segment {i}/{len(segments)}: {segment_url}")

            segment_content = download_with_retry(segment_url)
            with open(filename, "wb") as f:
                f.write(segment_content)
            downloaded_files.append(filename)

            debug_print(f"Segment {i} downloaded. Size: {len(segment_content)} bytes")

            # Random wait between downloads
            wait_time = random.uniform(0.5, 2.0)
            debug_print(f"Waiting {wait_time:.2f} seconds before next download...")
            time.sleep(wait_time)

        # Decrypt and combine segments
        debug_print("All segments downloaded. Starting decryption...")
        with open(output_name, "wb") as outfile:
            for i, filename in enumerate(downloaded_files, 1):
                debug_print(f"Decrypting segment {i}/{len(downloaded_files)}")
                with open(filename, "rb") as infile:
                    segment_content = infile.read()
                decrypted = decrypt(segment_content, key, iv)
                outfile.write(decrypted)

        debug_print(f"All segments decrypted. Output written to {output_name}")
        print("Your File Downloaded and Decrypted.")

    finally:
        # Clean up: remove temporary directory and all its contents
        debug_print(f"Cleaning up temporary directory: {temp_dir}")
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python download_script.py <config_json_url> <output_name>")
        sys.exit(1)

    config_json_url = sys.argv[1]
    output_name = sys.argv[2]
    download_and_decrypt(config_json_url, output_name)