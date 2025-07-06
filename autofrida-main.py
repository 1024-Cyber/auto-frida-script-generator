import argparse
import os
from scanner.smali_scanner import SmaliScanner
from generator.frida_generator import FridaGenerator

def main():
    parser = argparse.ArgumentParser(
        description="FridaForge: Auto-generate Frida bypass scripts from Smali code"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to decompiled APK Smali folder"
    )
    parser.add_argument(
        "--output",
        default="output/bypass.js",
        help="Output path for generated Frida script"
    )
    parser.add_argument(
        "--signatures",
        default="signatures",
        help="Path to signatures folder (default: ./signatures)"
    )

    args = parser.parse_args()

    smali_folder = os.path.abspath(args.input)
    output_file = os.path.abspath(args.output)
    signatures_folder = os.path.abspath(args.signatures)

    print(f"[+] Input Smali Folder : {smali_folder}")
    print(f"[+] Output Frida Script: {output_file}")
    print(f"[+] Signatures Folder  : {signatures_folder}")

    # Step 1: Scan smali for patterns
    scanner = SmaliScanner(signatures_folder)
    results = scanner.scan_folder(smali_folder)

    print("\n=== Detected Root Checks ===")
    for entry in results['root_detections']:
        print(f"File: {entry['file']}")
        for match in entry['matches']:
            print(f"  [Line {match['line_number']}] {match['line']}  --> Pattern: {match['pattern']}")

    print("\n=== Detected SSL Pinning ===")
    for entry in results['ssl_pinnings']:
        print(f"File: {entry['file']}")
        for match in entry['matches']:
            print(f"  [Line {match['line_number']}] {match['line']}  --> Pattern: {match['pattern']}")

    if not results['root_detections'] and not results['ssl_pinnings']:
        print("\n[!] No root detection or SSL pinning patterns found. Exiting.")
        return

    # Step 2: Generate Frida script
    generator = FridaGenerator(output_file=output_file)
    generator.generate(
        results['root_detections'],
        results['ssl_pinnings'],
        smali_root=smali_folder
    )

    print("\n[✔] Frida script generation complete!")
    print(f"[✔] Script written to: {output_file}")

if __name__ == "__main__":
    main()
