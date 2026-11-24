# -*- coding: utf-8 -*-
"""给两个自研模组的 boot.json 加上 additionFile（引入 LICENSE.md）。"""
import json
import os

TARGETS = [
    r"E:\TAML\_dol\work\联动模组\系统联动补全\boot.json",
    r"E:\TAML\_dol\work\_mods\44_美化修正\boot.json",
]

for p in TARGETS:
    if not os.path.exists(p):
        print("❌ 不存在:", p)
        continue
    with open(p, encoding="utf-8-sig") as f:
        bj = json.load(f)
    before = sorted(bj.keys())
    # 确保 additionFile 存在且含 LICENSE.md
    arr = bj.get("additionFile")
    if not isinstance(arr, list):
        arr = []
    if "LICENSE.md" not in arr:
        arr.append("LICENSE.md")
    bj["additionFile"] = arr
    with open(p, "w", encoding="utf-8") as f:
        json.dump(bj, f, ensure_ascii=False, indent=2)
    print("✅ %s" % os.path.basename(os.path.dirname(p)))
    print("   additionFile:", arr)
    print("   字段数: %d -> %d" % (len(before), len(bj)))

# 校验回读
print("\n=== 回读校验 ===")
for p in TARGETS:
    with open(p, encoding="utf-8-sig") as f:
        bj = json.load(f)
    print("%-20s name=%s  additionFile=%s" % (
        os.path.basename(os.path.dirname(p)), bj.get("name"), bj.get("additionFile")))
