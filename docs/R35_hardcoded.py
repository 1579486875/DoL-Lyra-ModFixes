"""第 35 轮：查 22 种硬编码英文标签的上下文，判断是否玩家可见。"""
import html
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
z = zipfile.ZipFile(APK)
g = html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))

LABELS = ["Pros", "Cons", "Materials", "Double combat actions", "DEBUG",
          "No dancing if", "Enable or disable it", "Position", "Front leg",
          "Back leg", "Frames", "Speed", "State", "Tools"]

for lab in LABELS:
    print("=" * 88)
    print(f"{lab!r}")
    print("=" * 88)
    # 找「引号包裹的完整标签」
    pats = [
        rf'>\s*{re.escape(lab)}\s*<',
        rf'"{re.escape(lab)}"',
        rf"'{re.escape(lab)}'",
        rf'`{re.escape(lab)}`',
    ]
    n = 0
    for pat in pats:
        for m in re.finditer(pat, g):
            n += 1
            if n <= 3:
                print(f"  {g[max(0,m.start()-150):m.start()+150]!r}")
    print(f"  共 {n} 处\n")
