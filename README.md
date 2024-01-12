# ArvanPlayer-DL
this tool uses to download arvanplayer m3u8 links.

ArvanPlayer(R1Player). <https://player.arvancloud.ir/>

# how it works?

Arvan Cloud uses AES-128-CBC to encrypt m3u8 ts files. The following script can decrypt these encrypted videos. 

You can achieve the same result using "ffmpeg".

# Usage :
first install cryptography library
```bash
pip3 install pycryptodome
```
you can import file in your project
```python3
from ArvanPlayer_DL import download

download("m3u8 link","my_video.mp4")
```
or run the file simple.

```bash
python3 ArvanPlayer_DL.py
```
