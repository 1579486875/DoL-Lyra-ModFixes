"""查角色创建界面的 Body / Head / Personality / Genitals / Condoms 标题。"""
import html
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
z = zipfile.ZipFile(APK)
g = html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))

print("=" * 94)
print("settingsHeader 里的英文标题")
print("=" * 94)
heads = re.findall(r'<div class="settingsHeader[^"]*">([^<]{1,60})</div>', g)
from collections import Counter
c = Counter(h.strip() for h in heads if h.strip())
for name, n in c.most_common(40):
    has_cjk = bool(re.search(r"[\u4e00-\u9fff]", name))
    print(f"  {n:>4}  {name!r}  {'✅中文' if has_cjk else '❌英文'}")

print("\n" + "=" * 94)
print("Body / Head / Personality 的上下文")
print("=" * 94)
for kw in ("Body", "Head", "Personality", "Genitals"):
    print(f"\n--- {kw} ---")
    for m in list(re.finditer(r'<div class="settingsHeader[^"]*">\s*' + kw + r'\s*</div>', g))[:3]:
        print(f"  @{m.start()}: {g[max(0,m.start()-200):m.start()+150]!r}")
