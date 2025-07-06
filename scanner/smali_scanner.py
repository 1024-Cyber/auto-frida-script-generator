import os
import json
import re

class SmaliScanner:
    def __init__(self, signatures_folder):
        self.signatures_folder = signatures_folder
        self.root_patterns = self.compile_patterns(
            self.load_patterns('root_patterns.json', 'root_detection')
        )
        self.ssl_patterns = self.compile_patterns(
            self.load_patterns('ssl_patterns.json', 'ssl_pinning')
        )

    def load_patterns(self, filename, key):
        path = os.path.join(self.signatures_folder, filename)
        with open(path, 'r') as f:
            data = json.load(f)
        return data.get(key, [])

    def compile_patterns(self, patterns):
        compiled = []
        for pattern in patterns:
            try:
                compiled.append(re.compile(pattern, re.IGNORECASE))
            except re.error as e:
                print(f"[!] Invalid regex pattern skipped: {pattern} ({e})")
        return compiled


    def scan_folder(self, smali_folder):
        print(f"[+] Scanning folder: {smali_folder}")
        results = {
            'root_detections': [],
            'ssl_pinnings': []
        }

        all_smali_files = []
        for root, _, files in os.walk(smali_folder):
            for file in files:
                if file.endswith('.smali'):
                    all_smali_files.append(os.path.join(root, file))

        total_files = len(all_smali_files)
        print(f"[+] Found {total_files} smali files to scan.\n")

        for idx, file_path in enumerate(all_smali_files, start=1):
            if idx % 50 == 0 or idx == 1 or idx == total_files:
                print(f"    [Progress] Scanning file {idx}/{total_files}: {os.path.basename(file_path)}")
            
            hits_root, hits_ssl = self.scan_file(file_path)
            if hits_root:
                print(f"    [!] Root detection patterns found in: {file_path}")
                results['root_detections'].append({
                    'file': file_path,
                    'matches': hits_root
                })
            if hits_ssl:
                print(f"    [!] SSL pinning patterns found in: {file_path}")
                results['ssl_pinnings'].append({
                    'file': file_path,
                    'matches': hits_ssl
                })

        print("\n[+] Scan complete.")
        print(f"[+] Files with root detections : {len(results['root_detections'])}")
        print(f"[+] Files with SSL pinning    : {len(results['ssl_pinnings'])}\n")

        return results


    def scan_file(self, file_path):
        hits_root = []
        hits_ssl = []
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        for idx, line in enumerate(lines):
            for regex in self.root_patterns:
                if regex.search(line):
                    hits_root.append({
                        'line_number': idx + 1,
                        'line': line.strip(),
                        'pattern': regex.pattern
                    })
            for regex in self.ssl_patterns:
                if regex.search(line):
                    hits_ssl.append({
                        'line_number': idx + 1,
                        'line': line.strip(),
                        'pattern': regex.pattern
                    })
        return hits_root, hits_ssl
