"""M03：列出所有字符串里的 <<br>>。"""
import html as H
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
g = H.unescape(zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace"))

print("=" * 95)
print("1. 所有字符串字面量里的 <<br>>")
print("=" * 95)
for m in re.finditer(r'["\'`][^"\'`\n]{0,200}<<br[^"\'`\n]{0,100}["\'`]', g):
    seg = m.group(0)
    print(f"\n@{m.start()}")
    print(f"  {seg[:300]!r}")
    # 上下文
    print(f"  上下文: {g[max(0,m.start()-150):m.start()+200]!r}")

print("\n" + "=" * 95)
print("2. 所有裸 <<br>>（含 HTML 里）")
print("=" * 95)
for m in re.finditer(r"<<br\s*>>", g):
    print(f"\n@{m.start()}")
    print(f"  {g[max(0,m.start()-200):m.start()+150]!r}")
