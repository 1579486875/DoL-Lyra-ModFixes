"""精确查「变量路径后紧跟全角标点」的非法 JS。

判据：$var.xxx 后面紧跟 。，、；：！？ 且再往后是 >> / 空格 / ) / ] / }
     —— 说明全角标点被当成了属性名的一部分。
"""
import html as H
import re
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"

data = open(HTML, "rb").read().decode("utf-8", "replace")
g = H.unescape(data)

BAD = re.compile(r"(\$[\w$]+(?:\.[\w$]+)*)([。，、；：！？])(?=\s*(?:>>|\)|\]|\}|,|\||\s))")

print("=" * 90)
print("变量路径后紧跟全角标点（非法 JS）")
print("=" * 90)
hits = []
for m in BAD.finditer(g):
    hits.append((m.group(1), m.group(2), m.start()))

print(f"共 {len(hits)} 处")
seen = set()
for var, punct, pos in hits[:30]:
    key = (var, punct)
    if key in seen:
        continue
    seen.add(key)
    print(f"\n  {var}{punct}")
    print(f"    {g[max(0,pos-120):pos+120]!r}")
