# arvanplayer-dl
Downloads videos from arvan player.

# how it works?

Arvan Cloud uses AES-128-CBC to encrypt m3u8 ts files. The following script can decrypt these encrypted videos.

You can achieve the same result using "ffmpeg".

# Prerequisites
Install required python and linux packages.
```bash
# install jq linux package to parse json files
sudo apt install jq -y
# create virtual environment
python3 -m venv .vnev
# install pip packages packages
pip3 install requests
pip3 install pycryptodome
```

# Usage :
Create links.txt and add config.json video links that are like below.
```text
https://mongard.arvanvod.ir/zzzzzzzzzz/xxxxxxxxxxx/origin_config.json
```

Run below to download all links.
```bash
./dl.sh links.txt path/to/download
```
