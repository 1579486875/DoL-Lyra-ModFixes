import subprocess, sys, os

STEPS = [
    (r"E:\TAML\_dol\work\inject6.py", "重建 index（模组数组）"),
    (r"E:\TAML\_dol\work\U13_inject.py", "注入 i18n Widgets variablesStatic 缺失的 163 条"),
]

for path, desc in STEPS:
    print(f"\n=== {desc} ===")
    r = subprocess.run([sys.executable, path], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    out = (r.stdout or "").strip().split("\n")
    for line in out[-6:]:
        print("  " + line)
    if r.returncode != 0:
        print("  ❌ 失败:", (r.stderr or "")[:400])
        sys.exit(1)
print("\n✅ 全部完成")
