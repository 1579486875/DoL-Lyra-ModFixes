"""定位侧边栏状态栏里硬编码的英文名。"""
import html
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
z = zipfile.ZipFile(APK)
g = html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))

print("=" * 94)
print("1) 「你感觉良好」的上下文")
print("=" * 94)
for m in list(re.finditer("你感觉良好", g))[:3]:
    print(f"@{m.start()}: {g[max(0, m.start() - 400):m.start() + 200]!r}")
    print()

print("=" * 94)
print("2) 侧边栏状态行的生成（找含 Pain 且含 HTML 的地方）")
print("=" * 94)
# 截图里是 "Pain: 你感觉良好。" —— 冒号 + 中文
for m in list(re.finditer(r"Pain\s*:", g))[:5]:
    print(f"@{m.start()}: {g[max(0, m.start() - 250):m.start() + 250]!r}")
    print()

print("=" * 94)
print("3) displayName 里的英文（JS 配置）")
print("=" * 94)
for kw in ("Condoms:", "Genitals:", "Pain:", "Arousal:", "Fatigue:", "Stress:", "Trauma:", "Control:", "Allure:"):
    ms = list(re.finditer(r'displayName:\s*"' + re.escape(kw) + r'"', g))
    if ms:
        print(f"  displayName {kw!r}: {len(ms)} 处")
        for m in ms[:2]:
            print(f"    {g[max(0,m.start()-120):m.start()+200]!r}")
