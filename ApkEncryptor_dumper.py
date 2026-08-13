import sys
import os
import json
import hashlib
import zipfile
import tempfile
import shutil

def xor_decrypt(data, key):
    key_bytes = key.encode('utf-8')
    result = bytearray(len(data))
    for i in range(len(data)):
        result[i] = data[i] ^ key_bytes[i % len(key_bytes)]
    return bytes(result)

def get_next_filename(output_dir):
    base_name = "classes.dex"
    if not os.path.exists(os.path.join(output_dir, base_name)):
        return base_name
    counter = 2
    while True:
        name = f"classes{counter}.dex"
        if not os.path.exists(os.path.join(output_dir, name)):
            return name
        counter += 1

def decrypt_file(input_path, key, output_dir):
    if not os.path.exists(input_path):
        print(f"❌ File not found: {input_path}")
        return False
    with open(input_path, 'rb') as f:
        encrypted_data = f.read()
    filename = os.path.basename(input_path)
    print(f"📁 Input: {filename}")
    print(f"📊 Size: {len(encrypted_data)} bytes")
    if filename == "3676d55f84497cbeadfc614c1b1b62fc":
        print(f"⏭️ Skipping config file: {filename}")
        return True
    decrypted_data = xor_decrypt(encrypted_data, key)
    os.makedirs(output_dir, exist_ok=True)
    output_name = get_next_filename(output_dir)
    output_path = os.path.join(output_dir, output_name)
    with open(output_path, 'wb') as f:
        f.write(decrypted_data)
    print(f"💾 Saved as: {output_path}")
    print(f"📊 Decrypted size: {len(decrypted_data)} bytes")
    return True

def process_apk(apk_path, key):
    if not os.path.exists(apk_path):
        print(f"❌ APK file not found: {apk_path}")
        return
    temp_dir = tempfile.mkdtemp()
    output_dir = "/sdcard/DexCavator/dump/"
    try:
        print(f"📦 Extracting APK: {apk_path}")
        with zipfile.ZipFile(apk_path, 'r') as apk:
            apk.extractall(temp_dir)
        src_dir = os.path.join(temp_dir, "src")
        if not os.path.exists(src_dir):
            print(f"❌ /src/ directory not found in APK")
            return
        files = os.listdir(src_dir)
        dex_files = []
        for filename in files:
            file_path = os.path.join(src_dir, filename)
            if os.path.isfile(file_path):
                if filename == "3676d55f84497cbeadfc614c1b1b62fc":
                    print(f"⏭️ Skipping config file: {filename}")
                    continue
                dex_files.append(file_path)
        print(f"📁 Found {len(dex_files)} DEX files to decrypt in /src/")
        for file_path in dex_files:
            print(f"\n{'='*50}")
            decrypt_file(file_path, key, output_dir)
    except Exception as e:
        print(f"❌ Error processing APK: {e}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Decrypt APK Encryptor files from /src/ folder')
    parser.add_argument('-i', '--input', required=True, help='Input APK file path')
    parser.add_argument('-k', '--key', required=True, help='Decryption key (Package name)')
    args = parser.parse_args()
    if not args.key:
        print("❌ Key is required. Use -k to specify decryption key")
        return
    process_apk(args.input, args.key)

if __name__ == "__main__":
    main()