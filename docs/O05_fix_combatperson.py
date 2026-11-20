"""O05：修 <<combatperson>> 的英文 description（幂等）。"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[O05] index 形态异常")
    sys.exit(1)

FIXES = [
    ('<<set _text_output to  $description>>',
     '<<set _text_output to $description_CN || $description>>'),
    ('<<set _text_output to $description>>',
     '<<set _text_output to $description_CN || $description>>'),
    ('<<set _text_output to $description +  setup.NPC_CN_TITLE(',
     '<<set _text_output to ($description_CN || $description) +  setup.NPC_CN_TITLE('),
    ('<<set _text_output to $description + "男人">>',
     '<<set _text_output to ($description_CN || $description) + "男人">>'),
    ('<<set _text_output to "" + $description + "女人">>',
     '<<set _text_output to ($description_CN || $description) + "女人">>'),
]

total = 0
for old, new in FIXES:
    hit = 0
    for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
        if a in data:
            c = data.count(a)
            data = data.replace(a, b)
            hit += c
    total += hit

if total:
    open(HTML, "wb").write(data.encode("utf-8"))

# 校验：combatperson 里不应有裸 $description（显示用）
g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
bare = 0
m = re.search(r'<<widget "combatperson">>(.*?)<</widget>>', g, re.S)
if m:
    wb = m.group(1)
    for mm in re.finditer(r"\$description(?!_CN)", wb):
        ctx = wb[max(0, mm.start() - 30):mm.start() + 40]
        if "|| $description" in ctx or "isnot" in ctx or " is " in ctx:
            continue
        bare += 1

print("[O05] 修 %d 处  passage=%d  裸desc=%d  %s" % (
    total, len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML, 'rb').read().decode('utf-8', 'replace'))),
    bare, "OK" if bare == 0 else "FAIL"))
sys.exit(0 if bare == 0 else 1)
