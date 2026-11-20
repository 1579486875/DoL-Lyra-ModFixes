"""V11：修 npcexposetext 的中英混杂（幂等）。"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[V11] index 形态异常")
    sys.exit(1)

MARK = "[V11]"
g0 = H.unescape(data)
if MARK in g0:
    print("[V11] 已存在，跳过  passage=%d" % len(re.findall(r'<tw-passagedata[^>]*name=', data)))
    sys.exit(0)

FIXES = [
    ('<<set _text_output to "The " + _person + " 掀起 " + _his + " skirt, ">>',
     '<<set _text_output to _person + "掀起" + _his + "的裙子，">>'),
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
    H.escape('<!-- [V11] npcexposetext 中英混杂 -->' + '<<widget "generateshoppage">>', quote=False), 1)

open(HTML, "wb").write(data.encode("utf-8"))

g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
# npcexposetext 里不应再有 "The " + ... + " skirt, "
m = re.search(r'<<widget "npcexposetext">>(.*?)<</widget>>', g, re.S)
bad = 0
if m:
    bad = m.group(1).count('"The "') + m.group(1).count(" skirt, ")

ok = bad == 0
print("[V11] 修 %d 处  npcexposetext 残留=%d  passage=%d  %s" % (
    total, bad,
    len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML, 'rb').read().decode('utf-8', 'replace'))),
    "OK" if ok else "FAIL"))
sys.exit(0 if ok else 1)
