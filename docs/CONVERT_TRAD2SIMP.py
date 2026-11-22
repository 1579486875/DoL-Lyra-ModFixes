# -*- coding: utf-8 -*-
"""把 index 里所有模组 ZIP 的繁体中文转成简体（只动中文，不碰代码/变量）。"""
import base64
import io
import json
import re
import sys
import zipfile

import opencc

cc = opencc.OpenCC("t2s")

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))

m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m.group(1))

# 只处理这些扩展名的文本文件
TEXT_EXT = re.compile(r"\.(twee|js|json|json5|html|css|txt|md)$", re.I)
# 繁体特征字（用于判断是否需要转换）
TRAD = re.compile(r"[飽攝額類據選擇開關閉發聲體們個為與這那麼誰會實現點兒裡邊還讓給對從沒發現當後時間問題應該樣條設計變處東頭長門問間聽寫讀語言認識記憶]")

converted_mods = []
total_files = 0
total_chars = 0

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
    name = bj.get("name") or "?"

    changed = 0
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
        for info in zz.infolist():
            data = zz.read(info.filename)
            if info.filename.endswith(".twee") and re.search(r"\.(twee)$", info.filename, re.I):
                pass
            if TEXT_EXT.search(info.filename) and info.file_size < 5 * 1024 * 1024:
                try:
                    t = data.decode("utf-8")
                except UnicodeDecodeError:
                    t = None
                if t is not None and TRAD.search(t):
                    nt = cc.convert(t)
                    if nt != t:
                        data = nt.encode("utf-8")
                        changed += 1
                        total_chars += len(t)
            zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
            zi.compress_type = info.compress_type
            zi.external_attr = info.external_attr
            zo.writestr(zi, data)
    if changed:
        new_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        raw = raw.replace(s, new_b64, 1)
        converted_mods.append((name, changed))
        total_files += changed

print("转换的模组：")
for n, c in converted_mods:
    print("  %-32s %d 个文件" % (n, c))
print("\n合计：%d 个模组 / %d 个文件 / %d 字符" % (len(converted_mods), total_files, total_chars))

npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
m2 = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
cnt2 = len(re.findall(r'"[A-Za-z0-9+/=\s]{200,}"', m2.group(1)))
print("passage:", npass, "->", npass2, "| 模组数:", cnt2)
if npass2 != npass:
    print("❌ passage 变化")
    sys.exit(1)
open(HTML, "wb").write(raw.encode("utf-8"))
print("✅ 写入")
