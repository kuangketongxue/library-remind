"""
Scan Desktop + Start Menu .lnk files for broken shortcuts.
Outputs CSV-style list of broken shortcuts.
"""
import os
import win32com.client

shell = win32com.client.Dispatch("WScript.Shell")

locations = {
    "Desktop": os.path.join(os.environ["USERPROFILE"], "Desktop"),
    "StartMenu_User": os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu"),
    "StartMenu_All": os.path.join(os.environ["PROGRAMDATA"], r"Microsoft\Windows\Start Menu"),
}

broken = []

for loc_name, loc_path in locations.items():
    if not os.path.exists(loc_path):
        continue
    for root, dirs, files in os.walk(loc_path):
        for f in files:
            if f.lower().endswith(".lnk"):
                lnk_path = os.path.join(root, f)
                try:
                    shortcut = shell.CreateShortcut(lnk_path)
                    target = shortcut.Targetpath
                    if target and not os.path.exists(target):
                        broken.append({
                            "location": loc_name,
                            "name": f,
                            "full_path": lnk_path,
                            "target": target,
                        })
                except Exception as e:
                    broken.append({
                        "location": loc_name,
                        "name": f,
                        "full_path": lnk_path,
                        "target": f"(error: {e})",
                    })

# Output results
print(f"BROKEN SHORTCUTS: {len(broken)}")
print("=" * 80)
for b in broken:
    print(f"[{b['location']}] {b['name']}")
    print(f"  Path:   {b['full_path']}")
    print(f"  Target: {b['target']}")
    print()

# Also output as JSON for downstream processing
import json
print("---JSON---")
print(json.dumps(broken, ensure_ascii=False, indent=2))
