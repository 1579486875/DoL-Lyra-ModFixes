"""查 i18n 里把 flesh_text 翻成 f浅色_text 的条目，并修复。"""
import html as H
import json
import os
import re
import sys

I18N = r"E:\TAML\_dol\work\i18n_dict.json"
HTML = r"E:\TAML\_dol\work\index_modded6.html"

d = json.load(open(I18N, "r", encoding="utf-8"))
items = d["typeB"]["TypeBInputStoryScript"]

print("=" * 94)
print("i18n 里含 flesh_text / f浅色 的条目")
print("=" * 94)
n = 0
for it in items:
    f, t = it.get("f") or "", it.get("t") or ""
    if "flesh_text" in f or "f浅色" in t or "flesh" in f.lower():
        n += 1
        if n <= 8:
            print(f"\n  pN={it.get('pN')} pos={it.get('pos')}")
            print(f"    f={f[:200]!r}")
            print(f"    t={t[:200]!r}")
print(f"\n共 {n} 条")

# 直接修当前 index
print("\n" + "=" * 94)
print("直接修复 index")
print("=" * 94)
data = open(HTML, "rb").read().decode("utf-8", "replace")
cnt = data.count("f浅色_text")
if cnt:
    data = data.replace("f浅色_text", "flesh_text")
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"✅ f浅色_text -> flesh_text : {cnt} 处")
else:
    print("（无）")

g = H.unescape(data)
names = re.findall(r'<<widget\s+"([^"]+)"', g)
bad = [x for x in names if re.search(r"[^\x00-\x7f]", x)]
print(f"\nwidget 总数 {len(names)}，含非 ASCII {len(bad)}")
if bad:
    print(f"  ❌ {bad}")
else:
    print("  ✅ 全部 ASCII")
