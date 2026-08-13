import sys
import zipfile
from pathlib import Path

KEY = "ହରେକୃଷ୍ଣରାଧେରାଧେ".encode('utf-8')

def decrypt_data(encrypted_data):
    decrypted_data = bytearray()
    key_len = len(KEY)
    for i, byte in enumerate(encrypted_data):
        decrypted_data.append(byte ^ KEY[i % key_len])
    return decrypted_data

def extract_and_decrypt(apk_path):
    apk_path = Path(apk_path)
    if not apk_path.exists():
        print(f"❌ File not found: {apk_path}")
        return False
    output_dir = Path("/sdcard/DexCavator/dump/")
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(apk_path, 'r') as apk:
            efy_files = [f for f in apk.namelist() 
                        if f.startswith('res/color/') and f.endswith('.efy')]
            if not efy_files:
                print("❌ .efy files not found in res/color/")
                return False
            for efy_file in efy_files:
                base_name = Path(efy_file).stem
                if base_name == 'dmbttft':
                    dex_name = 'classes.dex'
                else:
                    num = base_name.replace('dmbttft', '')
                    dex_name = f'classes{num}.dex'
                with apk.open(efy_file) as f:
                    encrypted_data = f.read()
                decrypted_data = decrypt_data(encrypted_data)
                output_path = output_dir / dex_name
                with open(output_path, 'wb') as f:
                    f.write(decrypted_data)
                print(f"✅ {efy_file} -> {output_path}")
            print(f"\n🎉 Done! Files saved to: {output_dir}")
            return True
    except zipfile.BadZipFile:
        print("❌ Error: file is not an APK archive")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    if len(sys.argv) < 2 or sys.argv[1] != '-i':
        print("Usage:")
        print(f"  python {Path(__file__).name} -i <path_to_apk_file>")
        print()
        print("Example:")
        print(f"  python {Path(__file__).name} -i app.apk")
        sys.exit(1)
    success = extract_and_decrypt(sys.argv[2])
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()