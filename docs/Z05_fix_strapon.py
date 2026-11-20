"""Z05：翻译假阳具尺寸选项（幂等）。"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[Z05] index 形态异常")
    sys.exit(1)

MARK = "[Z05]"
g0 = H.unescape(data)
if MARK in g0:
    print("[Z05] 已存在，跳过  passage=%d" % len(re.findall(r'<tw-passagedata[^>]*name=', data)))
    sys.exit(0)

# <<option "显示文本" 值>> —— 只翻显示文本，值（数字）不变
FIXES = [
    ('<<option "regular" 2>>', '<<option "普通" 2>>'),
    ('<<option "large" 3>>', '<<option "大" 3>>'),
    ('<<option "massive" 4>>', '<<option "巨大" 4>>'),
]

total = 0
for old, new in FIXES:
    for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
        if a in data:
            c = data.count(a)
            data = data.replace(a, b)
            total += c
            break

data = data.replace(
    H.escape('<<widget "generateshoppage">>', quote=False),
    H.escape('<!-- [Z05] 假阳具尺寸选项 -->' + '<<widget "generateshoppage">>', quote=False), 1)

open(HTML, "wb").write(data.encode("utf-8"))

g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
bad = (g.count('<<option "regular" 2>>')
       + g.count('<<option "large" 3>>')
       + g.count('<<option "massive" 4>>'))
ok = bad == 0
print("[Z05] 修 %d 处  残留=%d  passage=%d  %s" % (
    total, bad,
    len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML, 'rb').read().decode('utf-8', 'replace'))),
    "OK" if ok else "FAIL"))
sys.exit(0 if ok else 1)
