"""列出所有剩余英文 displayName，生成待翻译清单。"""
import html
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
CJK = re.compile(r"[\u4e00-\u9fff]")

z = zipfile.ZipFile(APK)
g = html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))

allDn = re.findall(r'displayName:\s*"([^"]{1,70})"', g)
en = sorted(set(x for x in allDn if not CJK.search(x)))

print(f"剩余纯英文 displayName: {len(en)}")
print("=" * 88)
for i, x in enumerate(en, 1):
    print(f"{i:>3}. {x}")
