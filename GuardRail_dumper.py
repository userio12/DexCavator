#!/usr/bin/env python3
import zlib
import sys
import os
import argparse
import zipfile

def decrypt_arsc(input_file, output_file):
    try:
        with open(input_file, 'rb') as f:
            encrypted_data = f.read()
        try:
            decompressed_data = zlib.decompress(encrypted_data)
        except zlib.error:
            decompressed_data = zlib.decompress(encrypted_data, -zlib.MAX_WBITS)
        with open(output_file, 'wb') as f:
            f.write(decompressed_data)
        print(f"[+] Saved to: {output_file}")
    except FileNotFoundError:
        print(f"[-] Error: File {input_file} not found")
        sys.exit(1)
    except Exception as e:
        print(f"[-] Error during processing: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Extract and decrypt RizalProtect ARSC from APK')
    parser.add_argument('-i', '--input', required=True, help='Path to APK file')
    args = parser.parse_args()
    apk_path = args.input
    output_dir = "/sdcard/DexCavator/dump/"
    if not os.path.exists(apk_path):
        print(f"[-] File {apk_path} not found")
        sys.exit(1)
    if not apk_path.lower().endswith('.apk'):
        print(f"[!] Warning: File may not be an APK (extension not .apk)")
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            print(f"[-] Failed to create directory {output_dir}: {e}")
            sys.exit(1)
    dex_index = 1
    while True:
        output_file = os.path.join(output_dir, f"classes{dex_index}.dex")
        if not os.path.exists(output_file):
            break
        dex_index += 1
    try:
        print(f"[*] Opening APK: {apk_path}")
        with zipfile.ZipFile(apk_path, 'r') as apk_zip:
            arsc_path = "assets/rizalprotect/rizalprotect.arsc"
            if arsc_path not in apk_zip.namelist():
                print(f"[-] Error: {arsc_path} not found in APK")
                sys.exit(1)
            print(f"[*] Extracting {arsc_path} from APK")
            temp_arsc = "rizalprotect.arsc"
            with open(temp_arsc, 'wb') as f:
                f.write(apk_zip.read(arsc_path))
            decrypt_arsc(temp_arsc, output_file)
            if os.path.exists(temp_arsc):
                os.remove(temp_arsc)
    except Exception as e:
        print(f"[-] Error extracting from APK: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
