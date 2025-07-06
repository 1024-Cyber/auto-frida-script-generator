auto-frida-script-generator is an automated toolkit that scans an Android APK's Smali code for known root detection and SSL pinning patterns, then auto-generates a Frida script to bypass them.

---

## ✅ Features

- Scans APK's Smali code for root-detection and SSL-pinning signatures
- Uses advanced regex patterns to detect obfuscated code
- Automatically generates a Frida script ( bypass.js) to hook and bypass these checks
- Fully customizable signature patterns in JSON

---

## 🚀 How It Works

1) Decompile your APK using Apktool:

apktool d my_app.apk -o my_app_folder


2) Run auto-frida-script-generator script

python main.py --input my_app_folder --output output/bypass.js


3) Load the generated script with frida

frida -U -f com.target.app -l output/bypass.js --pause




