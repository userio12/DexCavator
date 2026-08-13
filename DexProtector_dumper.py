import os
import zlib
import sys
import zipfile
import argparse
from pathlib import Path

def derive_key(xcode):
    chars = [ord(c) for c in xcode]
    arr = [0] * 4
    arr[0] = chars[0] | (chars[1] << 16)
    arr[1] = chars[2] | (chars[3] << 16)
    arr[2] = chars[4] | (chars[5] << 16)
    arr[3] = chars[6] | (chars[7] << 16)
    result = [0] * 27
    result[0] = arr[0]
    state = [arr[1], arr[2], arr[3]]
    key = arr[0]
    for i in range(26):
        idx = i % 3
        state[idx] = (((state[idx] >> 8) | (state[idx] << 24)) & 0xFFFFFFFF) + key
        state[idx] = (state[idx] ^ i) & 0xFFFFFFFF
        key = (((key >> 29) | (key << 3)) & 0xFFFFFFFF) ^ state[idx]
        key = key & 0xFFFFFFFF
        result[i + 1] = key
    return result

def update_state(arr, state):
    a0 = state[0] & 0xFFFFFFFF
    a1 = state[1] & 0xFFFFFFFF
    for i in range(27):
        a1 = (((a1 << 24) | (a1 >> 8)) & 0xFFFFFFFF) + a0
        a1 = (a1 ^ arr[i]) & 0xFFFFFFFF
        a0 = (((a0 << 3) | (a0 >> 29)) & 0xFFFFFFFF) ^ a1
        a0 = a0 & 0xFFFFFFFF
    state[0] = a0
    state[1] = a1

def decrypt_stream(data, xcode):
    arr = derive_key(xcode)
    chars = [ord(c) for c in xcode]
    state = [0, 0]
    state[0] = chars[8] | (chars[9] << 16)
    state[1] = chars[10] | (chars[11] << 16)
    buffer = bytearray(data)
    i = 0
    pos = 0
    while pos < len(buffer):
        if i % 8 == 0:
            update_state(arr, state)
        idx = (i % 8) // 4
        shift = (i % 4) * 8
        xor_byte = (state[idx] >> shift) & 0xFF
        buffer[pos] ^= xor_byte
        i += 1
        pos += 1
    return bytes(buffer)

def decrypt_data(data, xcode):
    decrypted = decrypt_stream(data, xcode)
    try:
        return zlib.decompress(decrypted)
    except zlib.error:
        pass
    try:
        return zlib.decompress(decrypted, -zlib.MAX_WBITS)
    except zlib.error:
        pass
    return decrypted

DEFAULT_KEY = "34373A32623D3D62623C68303A643A62"

def process_apk(apk_path, xcode):
    if not os.path.exists(apk_path):
        print(f"Error: APK file not found: {apk_path}")
        return False
    output_dir = "/sdcard/DexCavator/dump/"
    try:
        os.makedirs(output_dir, exist_ok=True)
    except Exception as e:
        print(f"Error creating output directory: {e}")
        return False
    try:
        with zipfile.ZipFile(apk_path, 'r') as apk:
            dp_lib_files = []
            for info in apk.infolist():
                if info.filename.startswith("assets/dp-lib/") and not info.is_dir():
                    dp_lib_files.append(info)
            if not dp_lib_files:
                print("Error: No files found in assets/dp-lib/")
                return False
            print(f"Found {len(dp_lib_files)} file(s) in assets/dp-lib/")
            dp_lib_files.sort(key=lambda x: x.filename)
            success_count = 0
            for idx, info in enumerate(dp_lib_files):
                filename = info.filename
                print(f"\nProcessing [{idx+1}/{len(dp_lib_files)}]: {filename}")
                encrypted_data = apk.read(filename)
                print(f"  Size: {len(encrypted_data)} bytes")
                try:
                    decrypted_data = decrypt_data(encrypted_data, xcode)
                    output_file = os.path.join(output_dir, f"classes{idx+1}.dex")
                    with open(output_file, 'wb') as f:
                        f.write(decrypted_data)
                    print(f"  → Saved: {output_file} ({len(decrypted_data)} bytes)")
                    success_count += 1
                except Exception as e:
                    print(f"  ✗ Decryption failed: {e}")
            print(f"\nCompleted: {success_count}/{len(dp_lib_files)} files decrypted successfully")
            return success_count > 0
    except zipfile.BadZipFile:
        print("Error: Invalid APK file (not a valid ZIP archive)")
        return False
    except Exception as e:
        print(f"Error processing APK: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Decrypt dex files from APK assets/dp-lib/",
        usage="python %(prog)s -i <apk_path> [-k <key>]"
    )
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Path to APK file"
    )
    parser.add_argument(
        "-k", "--key",
        required=False,
        default=DEFAULT_KEY,
        help=f"Decryption key (Xcode string). Default: {DEFAULT_KEY}"
    )
    args = parser.parse_args()
    print("=" * 50)
    print("DexProtector MPK Decryptor")
    print("=" * 50)
    if args.key == DEFAULT_KEY:
        print(f"Default decryption key: {DEFAULT_KEY}")
    else:
        print(f"Custom decryption key: {args.key}")
    success = process_apk(args.input, args.key)
    if success:
        print("\n[✓] Decryption completed successfully")
        print(f"Output directory: /sdcard/DexCavator/dump/")
    else:
        print("\n[✗] Decryption failed")
        sys.exit(1)

if __name__ == "__main__":
    main()