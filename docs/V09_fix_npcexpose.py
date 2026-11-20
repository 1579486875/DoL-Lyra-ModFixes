"""V09：修 npcexposetext 的中英混杂 + 查多出的那 1 处 /* */。"""
import html as H
import re
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[V09] index 形态异常")
    sys.exit(1)

MARK = "[V09]"
g0 = H.unescape(data)
if MARK in g0:
    print("[V09] 已存在，跳过")
    sys.exit(0)

total = 0

print("=" * 90)
print("1. 修 npcexposetext")
print("=" * 90)
FIXES = [
    ('<<set _text_output to "The " + _person + " 掀起 " + _his + " skirt, ">>',
     '<<set _text_output to _person + "掀起" + _his + "的裙子，">>'),
]
for old, new in FIXES:
    hit = 0
    for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
        if a in data:
            c = data.count(a)
            data = data.replace(a, b)
            hit += c
            break
    if hit:
        total += hit
        print(f"  OK {hit}x")
    else:
        print(f"  MISS  {old[:70]!r}")

# 同类：还有没有 "The " + xxx + " 英文"
print("\n" + "=" * 90)
print("2. 扫同类「中文 + 英文单词」拼接")
print("=" * 90)
g = H.unescape(data)
n2 = 0
for m in re.finditer(r'<<set\s+_text_output\s+to\s+"([^"]{0,80})"\s*\+', g):
    v = m.group(1)
    if re.search(r"[\u4e00-\u9fff]", v) or re.match(r"^(The|A|An)\s", v):
        n2 += 1
        if n2 <= 15:
            print(f"  {v!r}")

# 打标记
data = data.replace(
    H.escape('<<widget "generateshoppage">>', quote=False),
    H.escape('<!-- [V09] ==== -->' + '<<widget "generateshoppage">>', quote=False), 1)

open(HTML, "wb").write(data.encode("utf-8"))
print(f"\n共修 {total} 处")

# ---- 校验 ----
g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
print("\n" + "=" * 90)
print("校验")
print("=" * 90)
print(f"  _text_output \"The \": {len(re.findall(chr(34)+'The '+chr(34), g2))}")
print(f"  skirt, 残留: {g2.count(' skirt, ')}")

# ---- 查多出的 1 处 /* ----
print("\n" + "=" * 90)
print("3. 对比基线的 /* */ 集合差异")
print("=" * 90)
GOOD = r"E:\TAML\_dol\archive\DoL-Lyra-0.5.12.13-CHS-modded_20261120-061313_修复arsc可安装.apk"
gb = H.unescape(zipfile.ZipFile(GOOD).read("assets/www/index.html").decode("utf-8", "replace"))


def collect(t):
    P = {}
    for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', t, re.S):
        P[m.group(1)] = m.group(2)
    out = {}
    for pname, body in P.items():
        b = re.sub(r"<<script>>.*?<</script>>", "", body, flags=re.S)
        cs = re.findall(r"/\*[^*\n]{0,180}?\*/", b)
        if cs:
            out[pname] = cs
    return out


ca = collect(g2)
cb = collect(gb)
only_a = set(ca) - set(cb)
only_b = set(cb) - set(ca)
print(f"  只在当前: {sorted(only_a)[:10]}")
print(f"  只在基线: {sorted(only_b)[:10]}")

# 逐 passage 比数量
diff = []
for p in set(ca) & set(cb):
    if len(ca[p]) != len(cb[p]):
        diff.append((p, len(cb[p]), len(ca[p])))
print(f"\n  passage 内数量不同的: {len(diff)}")
for p, a, b in diff[:15]:
    print(f"    {p}: 基线 {a} -> 当前 {b}")

print(f"\n  passage: {len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML,'rb').read().decode('utf-8','replace')))}")
