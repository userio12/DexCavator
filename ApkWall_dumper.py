import os
import zipfile
import struct
import argparse
from pathlib import Path
from typing import Optional
import sys


class AdvancedDexDumper:
    def __init__(self, apk_path: str, package_name: str):
        self.apk_path = Path(apk_path)
        self.pkg_name = package_name
        self.dex_count = 0
        self.DEX_HEADER = b'dex\n'
        self.XOR_KEY_FF = b'\xff'

    def run(self) -> str:
        try:
            if not self.apk_path.exists():
                return "❌ APK not found!"
            output_dir = self.apk_path.parent / "dump"
            output_dir.mkdir(parents=True, exist_ok=True)
            self._process_apk(output_dir)
            return f"──────────────────────────────\n✅ Success! Saved {self.dex_count} DEX files.\n📂 Path: {output_dir}"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def _process_apk(self, output_dir: Path):
        with zipfile.ZipFile(self.apk_path, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                if file_info.is_dir():
                    continue
                filename = file_info.filename
                if filename.endswith(('.xml', '.png')):
                    continue
                try:
                    data = zip_ref.read(filename)
                except:
                    continue
                if len(data) < 100:
                    continue
                dex_data = self._extract_dex(data)
                if dex_data:
                    self.dex_count += 1
                    if self.dex_count == 1:
                        dex_name = "classes.dex"
                    else:
                        dex_name = f"classes{self.dex_count}.dex"
                    dex_file = output_dir / dex_name
                    dex_file.write_bytes(dex_data)
                    print(f"✅ Found: {filename} → {dex_name}")
    
    def _extract_dex(self, data: bytes) -> Optional[bytes]:
        if data[:3] == b'dex':
            return data
        pkg_bytes = self.pkg_name.encode('utf-8')
        if self._check_xor(data, pkg_bytes):
            return self._do_xor(data, pkg_bytes)
        if self._check_xor(data, self.XOR_KEY_FF):
            return self._do_xor(data, self.XOR_KEY_FF)
        return self._find_internal_dex(data)
    
    def _check_xor(self, data: bytes, key: bytes) -> bool:
        if len(data) < 4:
            return False
        return ((data[0] ^ key[0 % len(key)]) == ord('d') and
                (data[1] ^ key[1 % len(key)]) == ord('e'))
    
    def _do_xor(self, data: bytes, key: bytes) -> bytes:
        result = bytearray(len(data))
        key_len = len(key)
        for i in range(len(data)):
            result[i] = data[i] ^ key[i % key_len]
        return bytes(result)
    
    def _find_internal_dex(self, data: bytes) -> Optional[bytes]:
        pos = data.find(self.DEX_HEADER)
        if pos == -1:
            return None
        if pos + 36 > len(data):
            return None
        try:
            size = struct.unpack('<I', data[pos + 32:pos + 36])[0]
            if size > 0 and pos + size <= len(data):
                return data[pos:pos + size]
        except:
            pass
        return None


def main():
    parser = argparse.ArgumentParser(
        description='ApkWall - extracts DEX files from APK',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python ApkWall_dumper.py -i app.apk -p com.example.app
        '''
    )
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Path to APK file'
    )
    parser.add_argument(
        '-p', '--package',
        required=True,
        help='Package name (e.g., com.example.app)'
    )
    args = parser.parse_args()
    if not os.path.exists(args.input):
        print(f"❌ Error: APK file not found: {args.input}")
        sys.exit(1)
    dumper = AdvancedDexDumper(args.input, args.package)
    result = dumper.run()
    print(result)


if __name__ == "__main__":
    main()