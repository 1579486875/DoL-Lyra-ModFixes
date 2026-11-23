# -*- coding: utf-8 -*-
"""第7轮：严格繁体检查（排除简体通用字）+ 模组英文残留深挖。"""
import base64
import io
import json
import re
import zipfile
from collections import Counter

raw = open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace")
m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m.group(1))

# 真繁体字（简体中绝不使用的）
TRAD = re.compile(r"[\u4e00-\u9fff]*[們個為與這那麼誰會實現點兒裡邊還讓給對從沒發現當後時間問題應該樣條設計變處東頭長門問間聽寫讀語言認識記憶飽攝額類據選擇開關閉發聲體轉觀縣嗎嗎]")
# 更精确：只认这些字
TRAD_CHARS = set("們個為與這那麼誰會實現點兒裡邊還讓給對從沒發現當後時間問題應該樣條設計變處東頭長門問間聽寫讀語言認識記憶飽攝額類據選擇開關閉發聲體轉觀縣嗎嗎")

# 简体也通用的字（排除）
COMMON = set("那言理加突氛")

found = []
for s in parts:
    try:
        d = base64.b64decode(re.sub(r"\s+", "", s))
    except Exception:
        continue
    if d[:2] != b"PK":
        continue
    try:
        zz = zipfile.ZipFile(io.BytesIO(d))
        bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
    except Exception:
        continue
    nm = bj.get("name") or "?"
    for info in zz.infolist():
        if info.file_size > 3 * 1024 * 1024:
            continue
        if not re.search(r"\.(twee|js|json)$", info.filename, re.I):
            continue
        try:
            t = zz.read(info).decode("utf-8", "replace")
        except Exception:
            continue
        cnt = Counter(ch for ch in t if ch in TRAD_CHARS and ch not in COMMON)
        if cnt:
            found.append((nm, info.filename, cnt))

print("真繁体残留:", len(found))
for nm, f, c in found[:20]:
    print("  %-28s %-44s %s" % (nm, f, dict(c.most_common(4))))
