# -*- coding: utf-8 -*-
"""对比 AU-F 版 vs 我们的包：身形规格 + 服装变体覆盖 + 是否配套。"""
import hashlib
import io
import os
import zipfile
from collections import Counter, defaultdict

AU = r"E:\TAML\_dol\apk\对照-AU-F立绘版.apk"
OURS = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
BASE = r"E:\TAML\_dol\apk\对照-基础版-无美化.apk"

from PIL import Image


def probe(apk, label):
    z = zipfile.ZipFile(apk)
    names = {n.replace("\\", "/"): n for n in z.namelist()}
    print("=" * 66)
    print(label)
    print("=" * 66)
    # 身形图规格
    for rel in ("img/body/base-curvy.png", "img/body/breasts/breasts-4.png", "img/body/breasts/breasts-6.png"):
        key = "assets/www/" + rel
        if key in names:
            d = z.read(names[key])
            try:
                im = Image.open(io.BytesIO(d))
                print("  %-34s %-11s %7d bytes" % (rel, "%dx%d" % im.size, len(d)))
            except Exception:
                print("  %-34s 读取失败" % rel)
        else:
            print("  %-34s 缺失" % rel)

    # 服装变体覆盖
    cloth = defaultdict(set)
    for n in names:
        import re
        m = re.match(r"assets/www/img/clothes/([^/]+)/([^/]+)/(\d+)\.png$", n)
        if m:
            cloth[(m.group(1), m.group(2))].add(int(m.group(3)))
    print("  有数字变体的服装目录: %d" % len(cloth))
    cov = Counter(tuple(sorted(v)) for v in cloth.values())
    print("  完整 0-6 的服装: %d" % sum(c for combo, c in cov.items() if 0 in combo and 6 in combo))
    print("  缺 0 的: %d" % sum(1 for v in cloth.values() if 0 not in v))
    print("  缺 6 的: %d" % sum(1 for v in cloth.values() if 6 not in v))

    # 总数
    n_img = sum(1 for n in names if n.startswith("assets/www/img/") and n.lower().endswith((".png", ".webp", ".jpg", ".gif")))
    print("  图片总数: %d" % n_img)
    print()


probe(BASE, "基础版（无美化，256x128）")
probe(AU, "AU-F 立绘版")
probe(OURS, "我们的包（BEEESSS，512x256）")

# 服装贴图是否按 AU 重绘：比 AU 与基础版的服装差异
print("=" * 66)
print("AU-F 与基础版的服装图差异")
print("=" * 66)


def imgs(apk):
    z = zipfile.ZipFile(apk)
    m = {}
    for n in z.namelist():
        if n.startswith("assets/www/img/clothes/") and n.lower().endswith(".png"):
            try:
                m[n] = hashlib.md5(z.read(n)).hexdigest()
            except Exception:
                pass
    return m


b = imgs(BASE)
a = imgs(AU)
common = set(b) & set(a)
diff = [k for k in common if b[k] != a[k]]
print("服装图 基础版 %d / AU %d / 共有 %d" % (len(b), len(a), len(common)))
print("内容不同（AU 重画过）: %d" % len(diff))
print("AU 独有: %d" % len(set(a) - set(b)))
