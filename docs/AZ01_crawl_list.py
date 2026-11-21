"""AZ01（第14轮）：生成 passage 遍历名单 —— vanilla 与整合包都有的普通 passage（排除 widget / script / init / 特殊 passage）。"""
import json
import re
import sys

sys.path.insert(0, r"E:\TAML\_dol\work")
import scan_lib as L

V = {n: t for n, t, b in L.passages(open(r"E:\TAML\_dol\work\index.html", "rb").read().decode("utf-8", "replace"))}
rt = {}
for line in open(r"E:\TAML\_dol\work\_rt_gate_passages.jsonl", encoding="utf-8"):
    t, tg, b = json.loads(line)
    rt[t] = tg
SPECIAL = {"StoryInit", "StoryCaption", "StoryMenu", "StoryBanner", "StoryAuthor", "StorySubtitle", "StoryTitle",
           "StoryShare", "PassageReady", "PassageDone", "PassageHeader", "PassageFooter", "StoryInterface", "Start"}
names = []
for n, tags in V.items():
    tl = (tags or "").split()
    if n in SPECIAL or any(x in tl for x in ("widget", "script", "stylesheet", "init", "Twine.image", "nobr-skip")):
        continue
    if n not in rt or "widget" in (rt[n] or "").split():
        continue
    names.append(n)
names.sort()
json.dump(names, open(r"E:\TAML\_dol\work\_crawl_names.json", "w", encoding="utf-8"), ensure_ascii=False)
print("遍历名单 %d 个 passage（vanilla %d）" % (len(names), len(V)))
