# -*- coding: utf-8 -*-
"""找 toothbrush 配置的父级名字，并对比原版。"""
import re
import zipfile

APKS = [
    ("原版", r"E:\TAML\_dol\apk\对照-基础版-无美化.apk"),
    ("我们", r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"),
]

for label, path in APKS:
    z = zipfile.ZipFile(path)
    h = z.read("assets/www/index.html").decode("utf-8", "replace")
    print("\n" + "=" * 62)
    print("【%s】" % label)
    print("=" * 62)

    # 找 toothbrush: 的位置，往前找父级
    for mm in re.finditer(r"\btoothbrush\s*:\s*\{", h):
        i = mm.start()
        before = h[max(0, i - 3000):i]
        # 找最近的 xxx: { 形式
        parents = list(re.finditer(r"(\w+)\s*:\s*\{", before))
        print("\n@%d  toothbrush 定义:" % i)
        print("  ", h[i:i + 300].replace("\n", " ")[:300])
        print("  往前最近的几个父级 key:")
        for pm in parents[-6:]:
            print("     %-24s @%d" % (pm.group(1), pm.start()))
        break
