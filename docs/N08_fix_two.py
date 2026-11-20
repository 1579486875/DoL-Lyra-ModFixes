"""N08：修 The <<person>> masturbates + description_CN 赋英文 title（幂等）。"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[N08] index 形态异常")
    sys.exit(1)

FIXES = [
    ("The <<person>> masturbates.", "<<person>>自慰着。"),
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

# 通用：description_CN 赋英文 title -> 走 NPC_CN_TITLE
PAT2 = re.compile(r'<<set (\$(?:description_CN|NPCList\[[^\]]+\]\.description_CN)) to (\$(?:NPCName\[[^\]]+\]|NPCList\[[^\]]+\])\.title)>>')
cnt = len(PAT2.findall(data))
if cnt:
    def _sub(m):
        return '<<set %s to setup.NPC_CN_TITLE(%s) || %s>>' % (m.group(1), m.group(2), m.group(2))
    data = PAT2.sub(_sub, data)
    total += cnt

if total:
    open(HTML, "wb").write(data.encode("utf-8"))

g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
BAD = {
    "The person masturbates": g.count("The <<person>> masturbates"),
}
ok = all(v == 0 for v in BAD.values())
print("[N08] 修 %d 处  passage=%d  %s  %s" % (
    total, len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML, 'rb').read().decode('utf-8', 'replace'))),
    "  ".join("%s=%d" % (k, v) for k, v in BAD.items()),
    "OK" if ok else "FAIL"))
sys.exit(0 if ok else 1)
