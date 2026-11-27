# -*- coding: utf-8 -*-
"""对比原版包与我们的包：Peach Heart 相关定义。"""
import re
import zipfile

OURS = r"E:\TAML\_dol\out\育都孤儿-GNH个人整合版-2026.11.26.apk"
BASE = r"E:\TAML\_dol\apk\对照-基础版-无美化.apk"

for label, apk in (("原版", BASE), ("我们", OURS)):
    z = zipfile.ZipFile(apk)
    h = z.read("assets/www/index.html").decode("utf-8", "replace")
    names = z.namelist()
    print("\n" + "=" * 66)
    print("【%s】" % label)
    print("=" * 66)
    print("  index 里 'Peach Heart' 出现: %d 次" % h.count("Peach Heart"))
    print("  index 里 'peach heart' 出现: %d 次" % h.count("peach heart"))
    print("  index 里 'peachheart'   出现: %d 次" % h.lower().count("peachheart"))
    # 图片路径
    imgs = [n for n in names if "Peach Heart" in n or "peach heart" in n.lower()]
    print("  相关图片: %d 张" % len(imgs))
    for n in imgs[:8]:
        print("     ", n.replace("assets/www/", ""))
    # 搜索 pattern 里含 "peach heart"
    for pat in (r'"peach heart"', r'"Peach Heart"', r"peach-heart"):
        print("  pattern 形式 %-16s: %d 次" % (pat, len(re.findall(pat, h, re.I))))
