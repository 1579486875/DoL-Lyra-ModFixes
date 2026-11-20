"""T25：合并 CafeFoodList + 修三重尖括号（幂等）。"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[T25] index 形态异常")
    sys.exit(1)

MARK = "[T25]"
g0 = H.unescape(data)
if MARK in g0:
    print("[T25] 已存在，跳过  passage=%d" % len(re.findall(r'<tw-passagedata[^>]*name=', data)))
    sys.exit(0)

total = 0
g = g0
notes = []

# ---- 1. CafeFoodList 合并 ----
ms = list(re.finditer(r'<<set\s+setup\.CafeFoodList_cn_name\s+to\s+"([^"]*)"', g))
if len(ms) >= 2:
    def parse(s):
        d = {}
        for item in s.split("|"):
            if "," in item:
                k, v = item.split(",", 1)
                d[k.strip()] = v.strip()
        return d

    merged = {}
    for m in ms:
        for k, v in parse(m.group(1)).items():
            merged.setdefault(k, v)
    new_val = "|".join("%s,%s" % (k, v) for k, v in merged.items())
    old1, old2 = ms[0].group(0), ms[1].group(0)
    new2 = '<<set setup.CafeFoodList_cn_name to "' + new_val + '"'
    for o in (H.escape(old1, quote=False), old1):
        if o in data:
            data = data.replace(o, "", 1)
            break
    for o, n in ((H.escape(old2, quote=False), H.escape(new2, quote=False)), (old2, new2)):
        if o in data:
            data = data.replace(o, n, 1)
            break
    total += 2
    notes.append("CafeFoodList -> %d 词" % len(merged))

# ---- 2. 三重尖括号 ----
for old, new in (
    ('<<tending 5>><</if>>>', '<<tending 5>><</if>>'),
    ('<<upperwear "oversized button-down" "white">>>', '<<upperwear "oversized button-down" "white">>'),
):
    for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
        if a in data:
            c = data.count(a)
            data = data.replace(a, b)
            total += c
            break

data = data.replace(
    H.escape('<<widget "generateshoppage">>', quote=False),
    H.escape('<!-- [T25] ' + "; ".join(notes) + ' -->' + '<<widget "generateshoppage">>', quote=False), 1)

open(HTML, "wb").write(data.encode("utf-8"))

# 校验
g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
cs = re.findall(r'<<set\s+setup\.CafeFoodList_cn_name\s+to\s+"([^"]*)"', g2)
n_items = len([x for x in cs[0].split("|") if "," in x]) if cs else 0
ok = (len(cs) == 1 and n_items >= 25)
print("[T25] 修 %d 处  CafeFoodList: %d 次 / %d 词  passage=%d  %s" % (
    total, len(cs), n_items,
    len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML, 'rb').read().decode('utf-8', 'replace'))),
    "OK" if ok else "FAIL"))
sys.exit(0 if ok else 1)
