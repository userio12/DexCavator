#!/usr/bin/env python3
import os
import sys
import zipfile
import base64
import argparse
from pathlib import Path
from Crypto.Cipher import AES


# Script for decryption dex from protected by com.apkprotector.app
# open AndroidManifest.xml in protected app:
        # <meta-data
            # android:name="apkprotector.enc_key"
            # android:value="+7jRxRPk8TEN9dr0kTAjB2jrlCYf91NYkgxpg1Kirwo=" /> <-- here's Key
        # <meta-data
            # android:name="apkprotector.real_app"
            # android:value="android.app.Application" /> <-- here's global application name


KEY_B64 = "B4soIgn3ixlNzjKoISGU/qhN7UzI4IJw3L6uf/PFijQ="  # <-- paste here key from manifest


def decrypt_file(enc_data, key, out_path):
    iv = enc_data[:12]
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    decrypted = cipher.decrypt(enc_data[12:])
    with open(out_path, 'wb') as f:
        f.write(decrypted)

def main():
    parser = argparse.ArgumentParser(description='Decrypt protected DEX files from APK')
    parser.add_argument('-i', '--input', required=True, help='Path to the APK file')
    args = parser.parse_args()
    apk_path = args.input
    out_dir = Path("/sdcard/DexCavator/dump")
    out_dir.mkdir(parents=True, exist_ok=True)
    key = base64.b64decode(KEY_B64)
    with zipfile.ZipFile(apk_path, 'r') as apk:
        for f in apk.namelist():
            if f.startswith('assets/encrypted_dex/') and f.endswith('.enc'):
                name = os.path.basename(f).replace('.enc', '')
                data = apk.read(f)
                decrypt_file(data, key, out_dir / name)
                print(f"Decrypted: {name}")

if __name__ == "__main__":
    main()