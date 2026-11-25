# -*- coding: utf-8 -*-
"""深挖1：扫所有模组里的硬编码 passage 跳转/兜底。

危险模式：
  Engine.play('XxxPassage')           —— 硬编码跳转，跨地点时会跳错
  goto('Xxx')                          —— 同上
  <<run Engine.play('Xxx')>>          —— Twee 里的硬编码

判据：如果一个模组硬编码跳到某个「特定地点」的 passage（如 Bath/Bedroom），
      而该模组本该支持多地点，就是同类风险。
"""
import base64
import io
import json
import re
import zipfile
from collections import Counter

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")
mz = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", h, re.S)

# 原版所有 passage 名（用于判断是否「特定地点」）
PS = set()
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"', h):
    PS.add(m.group(1))

ALL = []
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
    for f in zz.namelist():
        if not f.lower().endswith((".js", ".twee", ".tw")):
            continue
        try:
            if zz.getinfo(f).file_size > 5_000_000:
                continue
            t = zz.read(f).decode("utf-8", "replace")
        except Exception:
            continue
        # Engine.play('Xxx') / goto('Xxx')
        for pat, kind in (
            (r"Engine\.play\(\s*['\"]([^'\"]{2,50})['\"]", "Engine.play"),
            (r"(?<!\.)goto\(\s*['\"]([^'\"]{2,50})['\"]", "goto"),
            (r"<<run\s+Engine\.play\(\s*['\"]([^'\"]{2,50})['\"]", "twee-run"),
            (r"<<goto\s+['\"]([^'\"]{2,50})['\"]", "twee-goto"),
        ):
            for mm in re.finditer(pat, t):
                ALL.append((nm, f.split("/")[-1], kind, mm.group(1)))

print("硬编码跳转总数: %d" % len(ALL))

# 按模组聚合
by_mod = {}
for nm, f, kind, target in ALL:
    by_mod.setdefault(nm, []).append((f, kind, target))

print("\n" + "=" * 74)
print("=== 按模组汇总 ===")
print("=" * 74)
for nm in sorted(by_mod):
    items = by_mod[nm]
    targets = Counter(t for _, _, t in items)
    print("\n【%s】%d 处" % (nm, len(items)))
    for t, c in targets.most_common(12):
        mark = ""
        # 特定地点 passage（原版有，且名字像地点）
        if t in PS and re.search(r"Bath|Bedroom|Shower|Room|School|Shop|Inn|Hospital|Church|Park|Street|Orphanage|Cottage|Manor|Flats|Farm|Forest|Beach", t):
            mark = "  ← 特定地点"
        print("   %-38s x%d%s" % (t, c, mark))
