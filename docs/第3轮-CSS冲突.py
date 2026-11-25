# -*- coding: utf-8 -*-
"""第3轮：审计模组添加的 CSS，找同一选择器被多个模组定义的情况。"""
import base64
import io
import json
import re
import zipfile
from collections import defaultdict

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")
mz = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", h, re.S)

# 收集每个模组注入的 CSS 选择器
sel_mods = defaultdict(set)

for s in re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', mz.group(1)):
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

    # styleFileList
    css_texts = []
    for f in (bj.get("styleFileList") or []):
        if isinstance(f, str) and f in zz.namelist():
            try:
                css_texts.append(zz.read(f).decode("utf-8", "replace"))
            except Exception:
                pass
    # scriptFileList 里内联的 CSS（$('<style>') / cssText / addStyle）
    for f in (bj.get("scriptFileList") or []):
        if not isinstance(f, str) or f not in zz.namelist():
            continue
        try:
            if zz.getinfo(f).file_size > 3_000_000:
                continue
            t = zz.read(f).decode("utf-8", "replace")
        except Exception:
            continue
        if "style" in t.lower() or "css" in t.lower():
            css_texts.append(t)

    # 只提取「选择器 { 」里的选择器（简化：找 `.xxx {` 或 `#xxx {`）
    for css in css_texts:
        for mm in re.finditer(r"(?m)^\s*([.#][\w\-]+(?:\s*[>+~]\s*[.#\w\-]+)?)\s*(?:,|\{)", css):
            sel = mm.group(1).strip()
            if len(sel) > 3:
                sel_mods[sel].add(nm)

conf = {k: v for k, v in sel_mods.items() if len(v) >= 2}
print("=== 同一 CSS 选择器被多个模组定义 ===")
print("共 %d 个" % len(conf))
if not conf:
    print("  ✅ 无冲突")
for k in sorted(conf, key=lambda x: -len(conf[x]))[:30]:
    print("  %-42s %s" % (k, sorted(conf[k])))

print("\n=== 统计 ===")
print("选择器总数: %d" % len(sel_mods))
print("冲突: %d" % len(conf))
