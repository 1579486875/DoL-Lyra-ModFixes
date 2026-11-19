"""找角色创建界面「仪态」列表的来源。"""
import html
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
z = zipfile.ZipFile(APK)
g = html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))

print("=" * 94)
print("1) 「仪态」出现的上下文")
print("=" * 94)
for m in list(re.finditer("仪态", g))[:5]:
    print(f"\n@{m.start()}: {g[max(0, m.start() - 500):m.start() + 700]!r}")

print("\n" + "=" * 94)
print("2) faceVariantOptions widget")
print("=" * 94)
m2 = re.search(r'<<widget\s+"faceVariantOptions"\s*>>(.*?)<</widget>>', g, re.S)
if m2:
    print(m2.group(1)[:1200])
else:
    print("未找到")

print("\n" + "=" * 94)
print("3) 所有读取 setup.faceVariantOptions 的地方")
print("=" * 94)
for m in list(re.finditer(r"setup\.faceVariantOptions", g))[:12]:
    print(f"@{m.start()}: {g[max(0, m.start() - 130):m.start() + 200]!r}")
    print()
