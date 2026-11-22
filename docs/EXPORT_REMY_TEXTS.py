# -*- coding: utf-8 -*-
"""导出 Remy Love actions-text.twee 的唯一英文文本到 JSON，供批量翻译。"""
import json
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\mods4\Remy.Love.Mod.mod.zip")
t = z.read("game/base-combat/actions-text.twee").decode("utf-8", "replace")

texts = []
for line in t.split("\n"):
    s = line.strip()
    if not s or s.startswith(("::", "<<", "/*", "//", "<!--")):
        continue
    if not re.search(r"[A-Za-z]{3,}", s):
        continue
    if re.search(r"[\u4e00-\u9fff]", s):
        continue
    texts.append(s)

uniq = sorted(set(texts))
json.dump(uniq, open(r"E:\TAML\_dol\work\_remy_texts.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("导出", len(uniq), "条 -> _remy_texts.json")

# 分批文件，每批 100 条
BATCH = 100
for i in range(0, len(uniq), BATCH):
    chunk = uniq[i:i + BATCH]
    json.dump(chunk, open(r"E:\TAML\_dol\work\_remy_batch_%02d.json" % (i // BATCH), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("批次:", (len(uniq) + BATCH - 1) // BATCH)
