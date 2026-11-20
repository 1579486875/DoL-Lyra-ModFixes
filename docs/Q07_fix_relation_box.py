"""Q07：修 relation-box 里 NPC_CN_NAME 的宏嵌套错误（幂等）。"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[Q07] index 形态异常")
    sys.exit(1)

CMP = "_npcData.nam"
SHOW = "<<print setup.NPC_CN_NAME(_npcData.nam)>>"

FIXES = [
    ('<<if (<<NPC_CN_NAME _npcData.nam>>>>>> is ("Ivory Wraith") or ($wraith.mimic is <<NPC_CN_NAME _npcData.nam>>>>>> and $wraith.revealed))>>',
     '<<if (_npcData.nam is "Ivory Wraith") or ($wraith.mimic is _npcData.nam and $wraith.revealed)>>'),
    ('<<if <<NPC_CN_NAME _npcData.nam>>>>>> is ("Ivory Wraith") and',
     '<<if _npcData.nam is "Ivory Wraith" and'),
    ('<<elseif $wraithIntro and $wraith.mimic is <<NPC_CN_NAME _npcData.nam>>>>>> and',
     '<<elseif $wraithIntro and $wraith.mimic is _npcData.nam and'),
    ('<<npcrelationship <<NPC_CN_NAME _npcData.nam>>>>>>>>',
     '<<npcrelationship setup.NPC_CN_NAME(_npcData.nam)>>'),
    ('<<NPC_CN_NAME _npcData.nam>>>>>>>>？', SHOW + '？'),
    ('<<NPC_CN_NAME _npcData.nam>>>>>>', SHOW),
]

total = 0
for old, new in FIXES:
    hit = 0
    for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
        if a in data:
            c = data.count(a)
            data = data.replace(a, b)
            hit += c
            break
    total += hit

if total:
    open(HTML, "wb").write(data.encode("utf-8"))

# 校验：relation-box 的 <<if>> 里不能有 <
g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
m = re.search(r'<<widget "relation-box">>(.*?)<</widget>>', g, re.S)
bad = 0
if m:
    for mm in re.finditer(r"<<if\b(.*?)>>", m.group(1)):
        body = mm.group(1)
        s = re.sub(r'"[^"]*"', lambda x: " " * len(x.group(0)), body)
        s = re.sub(r"'[^']*'", lambda x: " " * len(x.group(0)), s)
        s = re.sub(r"`[^`]*`", lambda x: " " * len(x.group(0)), s)
        if "<" in s:
            bad += 1

print("[Q07] 修 %d 处  passage=%d  relation-box if含< = %d  %s" % (
    total, len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML, 'rb').read().decode('utf-8', 'replace'))),
    bad, "OK" if bad == 0 else "FAIL"))
sys.exit(0 if bad == 0 else 1)
