"""F42（第33轮）：查 NPC_CN_TYPE 包装器的完整源码。"""
import html as H
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
raw = zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace")
g = H.unescape(raw)

print("=" * 90)
print("1) 所有给 NPC_CN_TYPE 赋值的地方")
print("=" * 90)
for m in re.finditer(r"(?:st|setup)\.NPC_CN_TYPE\s*=", g):
    print(f"\n@{m.start()}")
    print(f"  {g[max(0,m.start()-150):m.start()+900]!r}")

print("\n" + "=" * 90)
print("2) 搜 h.orig 相关")
print("=" * 90)
for m in list(re.finditer(r"h\.orig", g))[:10]:
    print(f"\n@{m.start()}")
    print(f"  {g[max(0,m.start()-400):m.start()+400]!r}")

print("\n" + "=" * 90)
print("3) 搜 defineProperty 包装")
print("=" * 90)
for m in list(re.finditer(r"defineProperty\(\s*(?:st|setup)\s*,\s*[\"']NPC_CN_TYPE", g))[:5]:
    print(f"\n@{m.start()}")
    print(f"  {g[max(0,m.start()-300):m.start()+800]!r}")
