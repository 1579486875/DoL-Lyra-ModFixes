# -*- coding: utf-8 -*-
"""对比补 BESC 前后的服装变体覆盖。"""
import re
import zipfile
from collections import defaultdict

BEFORE = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
AFTER = r"E:\TAML\_dol\work\signed_besc2\build_besc-aligned-signed.apk"

SLOTS = ["upper", "lower", "under-upper", "under-lower"]


def stat(path):
    z = zipfile.ZipFile(path)
    out = {}
    for slot in SLOTS:
        prefix = "assets/www/img/clothes/%s/" % slot
        groups = defaultdict(set)
        for n in z.namelist():
            if not n.startswith(prefix) or not n.endswith(".png"):
                continue
            rel = n[len(prefix):]
            parts = rel.split("/")
            item = parts[0] if len(parts) >= 2 else "(根)"
            fn = parts[-1][:-4]
            groups[item].add(fn)
        full = part = none = 0
        for item, fns in groups.items():
            nums = [int(x) for x in fns if re.fullmatch(r"\d+", str(x))]
            if set(range(0, 7)).issubset(set(nums)):
                full += 1
            elif nums:
                part += 1
            else:
                none += 1
        out[slot] = (len(groups), full, part, none)
    return out


b = stat(BEFORE)
a = stat(AFTER)

print("槽位           | 补前(总数/完整/部分/无) | 补后")
print("-" * 70)
for slot in SLOTS:
    print("%-14s | %3d/%2d/%3d/%3d       | %3d/%2d/%3d/%3d" % (
        slot, *b[slot], *a[slot]))

# body/breasts 检查
z = zipfile.ZipFile(AFTER)
print("\n=== body/breasts 文件 ===")
for i in range(0, 7):
    k = "assets/www/img/body/breasts/breasts%d.png" % i
    print("  breasts%d.png: %s" % (i, "✅" if k in z.namelist() else "❌"))
