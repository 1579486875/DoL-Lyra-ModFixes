# -*- coding: utf-8 -*-
"""查 NPC_CN_TYPE / 词对替换函数，看它怎么处理 's 所有格。"""
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")

print("=== NPC_CN_TYPE 定义 ===")
for m in re.finditer(r"NPC_CN_TYPE\s*[=:]\s*function|function\s+NPC_CN_TYPE", h):
    print("\n@%d:" % m.start())
    print(h[m.start():m.start() + 2000])

print("\n\n=== 搜替换所有格 's 的逻辑 ===")
for kw in ("'s", "\\'s", "replace.*'s", "possessive", "所有格"):
    hits = list(re.finditer(kw, h)) if kw not in ("replace.*'s", "possessive", "所有格") else []
    if not hits:
        continue
    print("\n%s: %d 处" % (kw, len(hits)))
    for mm in hits[:3]:
        seg = h[max(0, mm.start() - 250):mm.start() + 250]
        if "NPC" in seg or "CN" in seg or "replace" in seg:
            print("  @%d: %s" % (mm.start(), seg.replace("\n", " ")[:450]))
