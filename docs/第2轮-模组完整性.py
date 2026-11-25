# -*- coding: utf-8 -*-
"""第2轮：模组完整性审计。

检测三类「半成品」：
1) 声明了 addonPlugin 但 tweeFileList 为空 → 插件没东西可补
2) 声明了 scriptFileList 但依赖 TweeReplacer 且 addonPlugin 为空 → 脚本可能没被调用
3) boot.json 里文件列表指向不存在的文件
"""
import base64
import io
import json
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")
mz = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", h, re.S)

mods = []
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
    mods.append((bj.get("name") or "?", bj, zz))

print("模组数:", len(mods))

print("\n" + "=" * 70)
print("=== 1) boot.json 声明的文件是否存在 ===")
print("=" * 70)
missing = []
for nm, bj, zz in mods:
    names = set(zz.namelist())
    for field in ("scriptFileList", "tweeFileList", "styleFileList", "imgFileList",
                  "scriptFileList_earlyload", "scriptFileList_inject_early",
                  "scriptFileList_preload", "additionFile"):
        for f in (bj.get(field) or []):
            if isinstance(f, str) and f not in names:
                missing.append((nm, field, f))
if missing:
    for m in missing:
        print("  ❌ %-28s %-28s %s" % m)
else:
    print("  ✅ 全部存在")

print("\n" + "=" * 70)
print("=== 2) 疑似半成品（有脚本但没接入点）===")
print("=" * 70)
suspect = []
for nm, bj, zz in mods:
    scripts = (bj.get("scriptFileList") or []) + (bj.get("scriptFileList_earlyload") or []) + (bj.get("scriptFileList_preload") or [])
    twee = bj.get("tweeFileList") or []
    addon = bj.get("addonPlugin") or []
    deps = [x.get("modName", "") for x in (bj.get("dependenceInfo") or []) if isinstance(x, dict)]
    # 有脚本、依赖 TweeReplacer、但没有 addonPlugin 也没有 twee
    if scripts and not addon and not twee and any("TweeReplacer" in d for d in deps):
        suspect.append((nm, len(scripts), deps))
    # boot.json 里 self-described 修复性但无接入
    desc = str(bj.get("description") or "")
    if ("修复" in desc or "改为" in desc) and not addon and not twee and scripts:
        suspect.append((nm + "（描述宣称修复但无接入）", len(scripts), deps))

if suspect:
    for s in suspect:
        print("  ⚠️ %-40s 脚本=%d 依赖=%s" % s)
else:
    print("  ✅ 无")

print("\n" + "=" * 70)
print("=== 3) 各模组接入方式一览 ===")
print("=" * 70)
print("%-30s %6s %6s %6s %s" % ("模组", "脚本", "twee", "插件", "插件类型"))
for nm, bj, zz in sorted(mods, key=lambda x: x[0]):
    sc = len((bj.get("scriptFileList") or []) + (bj.get("scriptFileList_earlyload") or []) + (bj.get("scriptFileList_preload") or []))
    tw = len(bj.get("tweeFileList") or [])
    ad = len(bj.get("addonPlugin") or [])
    types = ",".join(sorted({p.get("modName", "?") for p in (bj.get("addonPlugin") or []) if isinstance(p, dict)}))[:40]
    flag = ""
    if sc == 0 and tw == 0 and ad == 0:
        flag = "  ⚠ 无任何内容"
    print("%-30s %6d %6d %6d %s%s" % (nm[:28], sc, tw, ad, types, flag))
