# -*- coding: utf-8 -*-
"""查剩下 5 个未确认来源的模组：Clothes / LocationsExt / CombatSkills / CombatActionsExt / Toilet Addon"""
import base64
import io
import json
import re
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")
m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)

WANT = {"Clothes", "LocationsExt", "CombatSkills", "CombatActionsExt", "Toilet Addon", "BasicNeeds"}

for s in re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m.group(1)):
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
    nm = bj.get("name") or ""
    if nm not in WANT:
        continue

    print("\n" + "=" * 70)
    print("【%s】v%s" % (nm, bj.get("version")))
    print("=" * 70)
    print("boot.json 全部字段:")
    for k, v in bj.items():
        sv = json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v
        print("  %-28s %s" % (k, str(sv)[:160]))

    # 文件树
    tops = {}
    for f in zz.namelist():
        top = f.split("/")[0] if "/" in f else f
        tops[top] = tops.get(top, 0) + 1
    print("  顶层结构:", dict(sorted(tops.items(), key=lambda x: -x[1])[:8]))

    # 找任何含作者/链接的文本
    for f in zz.namelist():
        if not f.lower().endswith((".md", ".txt", ".js", ".twee", ".json")):
            continue
        try:
            if zz.getinfo(f).file_size > 200_000:
                continue
            t = zz.read(f)[:3000].decode("utf-8", "replace")
        except Exception:
            continue
        for pat in (r"https?://[^\s\"'<>]{10,80}", r"(?:作者|Author|by)\s*[:：]?\s*([^\n]{2,40})"):
            for mm in list(re.finditer(pat, t))[:2]:
                line = mm.group(0).strip()[:110]
                if any(x in line.lower() for x in ("github", "gitgud", "discord", "tieba", "qq.com", "作者", "author")):
                    print("  [%s] %s" % (f[:40], line))
