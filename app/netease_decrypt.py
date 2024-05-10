# [尝鲜抓包工具Reqable，巧用脚本解密网易云音乐 - 易姐的博客](https://shakaianee.top/archives/944/comment-page-1)

import base64, json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

EAPI_KEY = b"e82ckenh8dichen8"
EAPI_CRYPTOR = AES.new(EAPI_KEY, AES.MODE_ECB)

def decrypt(enc_data):
    message = unpad(EAPI_CRYPTOR.decrypt(base64.b16decode(enc_data)), 16).decode()
    path, json_val, hash = message.split("-36cd479b6b5-")
    return path, json.loads(json_val)

if __name__ == "__main__":
    encrypted = input("Input content to decrypt: ")
    print(decrypt(encrypted))
