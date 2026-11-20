"""U01（第3轮）：与黄金基线逐项对比 —— 确认没把「基线本来就有的问题」扩大。

对比项：
  1. 宏配对（未闭合的 <<if>> / <</if>> 等）
  2. <<link>> 目标缺失
  3. <<include>> 目标缺失
  4. 变量名清单差异（存档兼容）
  5. widget 名清单差异
"""
import html as H
import re
import zipfile
from collections import Counter

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
GOOD = r"E:\TAML\_dol\archive\DoL-Lyra-0.5.12.13-CHS-modded_20261120-061313_修复arsc可安装.apk"

z = zipfile.ZipFile(APK)
zg = zipfile.ZipFile(GOOD)
raw = z.read("assets/www/index.html").decode("utf-8", "replace")
rawb = zg.read("assets/www/index.html").decode("utf-8", "replace")
g = H.unescape(raw)
gb = H.unescape(rawb)


def passages(t):
    d = {}
    for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', t, re.S):
        d[m.group(1)] = H.unescape(m.group(2))
    return d


PA = passages(raw)
PB = passages(rawb)
print(f"passage: 基线 {len(PB)} / 当前 {len(PA)}")

# ---- 1. 宏配对 ----
print("\n" + "=" * 95)
print("1. 宏配对（未闭合）")
print("=" * 95)


def unpaired(text):
    """简单配对：统计 <<if>>/<<elseif>>/<<else>> 与 <</if>> 的平衡"""
    opens = Counter()
    for m in re.finditer(r"<<(if|for|switch|widget|link|button|capture|silently|nobr|for|while|until)\b", text):
        opens[m.group(1)] += 1
    closes = Counter()
    for m in re.finditer(r"<</(if|for|switch|widget|link|button|capture|silently|nobr|while|until)>>", text):
        closes[m.group(1)] += 1
    # <<if>> 与 <</if>>（<<elseif>>/<<else>> 不配对）
    n_if = len(re.findall(r"<<if\b", text))
    n_endif = len(re.findall(r"<</if>>", text))
    return n_if, n_endif


for label, d in (("基线", PB), ("当前", PA)):
    tot_if = tot_end = 0
    bad = []
    for p, body in d.items():
        a, b = unpaired(body)
        tot_if += a
        tot_end += b
        if a != b:
            bad.append(p)
    print(f"  [{label}] <<if>> {tot_if} / <</if>> {tot_end} / 不平衡的 passage {len(bad)}")

# ---- 2. link 目标缺失 ----
print("\n" + "=" * 95)
print("2. <<link>> 目标缺失")
print("=" * 95)
for label, d in (("基线", PB), ("当前", PA)):
    names = set(d.keys())
    miss = Counter()
    for p, body in d.items():
        for m in re.finditer(r'<<link\s+\[\[\s*[^\]|]*\|\s*([^\]|]+?)\s*\]\]', body):
            t = m.group(1).strip()
            if t.startswith("$") or t.startswith("_") or "<<" in t:
                continue
            if t not in names:
                miss[t] += 1
    print(f"  [{label}] 缺失 {len(miss)} 个目标")
    for k, v in miss.most_common(8):
        print(f"      {k!r} ×{v}")

# ---- 3. include 目标缺失 ----
print("\n" + "=" * 95)
print("3. <<include>> 目标缺失")
print("=" * 95)
for label, d in (("基线", PB), ("当前", PA)):
    names = set(d.keys())
    miss = Counter()
    for p, body in d.items():
        for m in re.finditer(r'<<include\s+\[\[\s*([^\]|]+?)\s*\]\]', body):
            t = m.group(1).strip()
            if t not in names:
                miss[t] += 1
    print(f"  [{label}] 缺失 {len(miss)} 个目标")
    for k, v in miss.most_common(10):
        print(f"      {k!r} ×{v}")

# ---- 4. widget 名清单差异 ----
print("\n" + "=" * 95)
print("4. widget 名清单差异")
print("=" * 95)
wa = set(re.findall(r'<<widget\s+"([^"]+)"', g))
wb = set(re.findall(r'<<widget\s+"([^"]+)"', gb))
print(f"  基线 {len(wb)} / 当前 {len(wa)}")
print(f"  新增: {sorted(wa - wb)}")
print(f"  丢失: {sorted(wb - wa)}")

# ---- 5. 顶层变量名差异（存档兼容）----
print("\n" + "=" * 95)
print("5. $变量名差异（存档兼容）")
print("=" * 95)
va = set(re.findall(r"\$([A-Za-z_][A-Za-z0-9_]{2,})", g))
vb = set(re.findall(r"\$([A-Za-z_][A-Za-z0-9_]{2,})", gb))
print(f"  基线 {len(vb)} / 当前 {len(va)}")
added = sorted(va - vb)
lost = sorted(vb - va)
print(f"  新增 {len(added)}: {added[:20]}")
print(f"  丢失 {len(lost)}: {lost[:20]}")

# ---- 6. passage 名差异 ----
print("\n" + "=" * 95)
print("6. passage 名差异")
print("=" * 95)
sa, sb = set(PA.keys()), set(PB.keys())
print(f"  新增: {sorted(sa - sb)}")
print(f"  丢失: {sorted(sb - sa)}")
