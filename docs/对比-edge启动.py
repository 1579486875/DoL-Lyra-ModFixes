# -*- coding: utf-8 -*-
"""对比 诊断-index加载.js 与 cdp_suite.js 的 Edge 启动方式，找差异。"""
import re

for path, label in [
    (r"E:\TAML\_dol\work\诊断-index加载.js", "诊断-index加载.js（能用）"),
    (r"E:\TAML\_dol\work\cdp_suite.js", "cdp_suite.js（失败）"),
]:
    s = open(path, encoding="utf-8", errors="replace").read()
    print("\n" + "=" * 72)
    print(label)
    print("=" * 72)

    # 找 spawn / execFile / launch
    for pat in (r"spawn\s*\(", r"execFile\s*\(", r"edgePath", r"EDGE", r"msedge", r"headless", r"remote-debugging-port", r"user-data-dir"):
        for mm in list(re.finditer(pat, s))[:2]:
            seg = s[max(0, mm.start() - 200):mm.start() + 500]
            print("\n--- %s @%d ---" % (pat, mm.start()))
            print(seg[:650])
            break
