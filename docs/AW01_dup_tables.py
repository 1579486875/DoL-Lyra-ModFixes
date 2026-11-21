"""AW01：模板 §5.20 扫描口径 —— 所有 <<set setup.XXX to "..."> 字符串表，赋值 ≥2 次的逐个对比（官方 i18n 原值 vs 我们注入的）。"""
import html as H
import json
import re
from collections import defaultdict

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))
d = json.load(open(r"E:\TAML\_dol\work\_mods\23_ModI18N\i18n.json", encoding="utf-8"))
official = defaultdict(list)
for v in d["typeB"]["TypeBInputStoryScript"]:
    for m in re.finditer(r'<<set setup\.(\w+) to "([^"]*)"', v["t"]):
        official[m.group(1)].append(m.group(2))
occ = defaultdict(list)
for m in re.finditer(r'<<set setup\.(\w+) to "([^"]*)">>', g):
    j = g.rfind("<tw-passagedata", 0, m.start())
    nm = re.search(r'name="([^"]*)"', g[j:j + 300]).group(1)
    occ[m.group(1)].append((m.start(), nm, m.group(2)))
for k, lst in occ.items():
    if len(lst) < 2:
        continue
    print("== setup.%s 赋值 %d 次（官方 i18n 里 %d 次）" % (k, len(lst), len(official.get(k, []))))
    for pos, nm, val in lst:
        tag = "官方" if val in official.get(k, []) else "非官方"
        print("   @%d [%s] %s 长度 %d  %s…" % (pos, nm, tag, len(val), val[:90]))
