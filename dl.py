import sys
from Crypto.Cipher import AES
import requests

def decrypt(cipherbyte, key):
    cipher = AES.new(key, AES.MODE_CBC, b"\x00" * 16)
    videobyte = cipher.decrypt(cipherbyte)
    return videobyte

def _get_encryption_key(content):
    return content.split('METHOD=AES-128,URI="')[1].split('"')[0]

def _get_chunks(content):
    return list(filter(lambda x: "seg-" in x, content.splitlines()))

def download(url, output_name):
    open(output_name, "wb").write(b"")

    url_path = url.split("/")
    del url_path[-1]
    url_path = "/".join(url_path) + "/"  # output: https://mongard.arvanvod.ir/zzzzzzzzzz/xxxxxxxxxxx/h_,1080_1200,k.mp4.list/

    r = requests.get(url)
    key_file_name = _get_encryption_key(r.text)
    key: bytes = requests.get(url_path + key_file_name).content
    chunks = _get_chunks(r.text)
    for chunk in chunks:
        print(url_path + chunk)
        result = requests.get(url_path + chunk)
        decrypted = decrypt(result.content, key)
        open(output_name, 'ab').write(decrypted)

    print("Your File Downloaded.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python download_script.py <download_link> <output_name>")
        sys.exit(1)

    download_link = sys.argv[1]
    output_name = sys.argv[2]
    download(download_link, output_name)  # example: "https://mongard.arvanvod.ir/zzzzzzzzzz/xxxxxxxxxxx/h_,1080_1200,k.mp4.list/index-f1-v1-a1.m3u8"
