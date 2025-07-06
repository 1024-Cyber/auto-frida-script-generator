import os

class FridaGenerator:
    def __init__(self, output_file="output/bypass.js"):
        self.output_file = output_file
        self.script_lines = []

    def add_header(self):
        self.script_lines.append('// === Auto-Generated Frida Script ===')
        self.script_lines.append('Java.perform(function () {')

    def add_footer(self):
        self.script_lines.append('});')

    def smali_to_classname(self, smali_path, project_root):
        # Convert smali file path to Java class name
        relative_path = os.path.relpath(smali_path, project_root)
        class_path = relative_path.replace(".smali", "").replace("/", ".").replace("\\", ".")
        return class_path

    def add_root_hooks(self, root_matches, smali_root):
        for entry in root_matches:
            class_name = self.smali_to_classname(entry['file'], smali_root)
            for match in entry['matches']:
                if 'method' in match['line']:
                    continue  # skip method definitions for now
                method_guess = self.guess_method_name(match['line'])
                if method_guess:
                    self.script_lines.append(f"    var Target = Java.use('{class_name}');")
                    self.script_lines.append(f"    Target.{method_guess}.implementation = function () {{")
                    self.script_lines.append(f"        console.log('[Bypass] Hooked {method_guess}');")
                    self.script_lines.append(f"        return false;")
                    self.script_lines.append("    };")

    def add_ssl_hooks(self, ssl_matches, smali_root):
        for entry in ssl_matches:
            class_name = self.smali_to_classname(entry['file'], smali_root)
            for match in entry['matches']:
                if "checkServerTrusted" in match['pattern']:
                    self.script_lines.append(f"    var SSL = Java.use('{class_name}');")
                    self.script_lines.append(f"    SSL.checkServerTrusted.implementation = function (chain, authType) {{")
                    self.script_lines.append("        console.log('[Bypass] SSL Pinning Bypassed');")
                    self.script_lines.append("        return;")
                    self.script_lines.append("    };")

    def guess_method_name(self, line):
        """
        Try to guess the method name from a smali invoke line.
        e.g., invoke-virtual {v0}, Lcom/example;->isDeviceRooted()Z
        """
        match = None
        try:
            match = line.split("->")[1].split("(")[0]
        except:
            pass
        return match

    def generate(self, root_matches, ssl_matches, smali_root):
        print(f"[+] Generating Frida script at: {self.output_file}")
        self.script_lines.clear()
        self.add_header()
        self.add_root_hooks(root_matches, smali_root)
        self.add_ssl_hooks(ssl_matches, smali_root)
        self.add_footer()

        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.script_lines))
        print("[+] Frida script written successfully.")
