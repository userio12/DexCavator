#!/usr/bin/env python3
import zipfile
import os
import sys
import argparse

OUTPUT_DIR = "/sdcard/DexCavator/dump"

def xor_decrypt(encrypted_data, key=0xFF):
    decrypted_data = bytearray()
    for byte in encrypted_data:
        decrypted_data.append(byte ^ key)
    return bytes(decrypted_data)


def extract_encrypted_data(zip_file_path, out_dir):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        file_list = zip_ref.namelist()
        classes_files = [f for f in file_list if f.startswith('assets/classes') and f.endswith('.dex')]
        if not classes_files:
            print("No classes*.dex files found in assets/")
            return
        for classes_file in classes_files:
            encrypted_data = zip_ref.read(classes_file)
            decrypted_data = xor_decrypt(encrypted_data)
            output_file_path = os.path.join(out_dir, os.path.basename(classes_file))
            with open(output_file_path, 'wb') as output_file:
                output_file.write(decrypted_data)
            print(f"Dump {classes_file} Save Path => '{output_file_path}'")

def main():
    parser = argparse.ArgumentParser(description="Decrypt Arm加固 protected classes.dex files")
    parser.add_argument('-i', '--input', required=True, help='Path to input APK file')
    args = parser.parse_args()
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found")
        sys.exit(1)
    if not args.input.lower().endswith('.apk'):
        print("Warning: Input file does not have .apk extension")
    extract_encrypted_data(args.input, OUTPUT_DIR)
    print(f"\nAll decrypted files saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()