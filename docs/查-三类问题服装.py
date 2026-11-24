# -*- coding: utf-8 -*-
"""定位三类问题服装：束腰 / 魅魔 / 水手服，并统计它们的文件结构。"""
import re
import zipfile
from collections import defaultdict

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
z = zipfile.ZipFile(APK)
names = z.namelist()

# 1) 找所有 upper/lower 目录名，匹配关键词
KEY = {
    "束腰": ["corset", "corselet", "bustier", "stays"],
    "魅魔": ["succubus", "succubi", "demon", "devil", "incubus"],
    "水手服": ["sailor", "serafuku", "seifuku", "school-uniform", "seifuku"],
}

for label, kws in KEY.items():
    print("\n" + "=" * 66)
    print("【%s】关键词: %s" % (label, kws))
    print("=" * 66)
    hits = set()
    for n in names:
        m = re.match(r"assets/www/img/clothes/(upper|lower|under-upper|under-lower|over-upper|over-lower)/([^/]+)/", n)
        if not m:
            continue
        item = m.group(2).lower()
        for kw in kws:
            if kw in item:
                hits.add((m.group(1), m.group(2)))
                break
    if not hits:
        print("  ❌ 未找到匹配目录")
        continue
    for slot, item in sorted(hits):
        prefix = "assets/www/img/clothes/%s/%s/" % (slot, item)
        files = [n[len(prefix):] for n in names if n.startswith(prefix) and n.endswith(".png")]
        # 提取数字变体
        nums = sorted(int(f[:-4]) for f in files if re.fullmatch(r"\d+", f[:-4]))
        others = sorted(f[:-4] for f in files if not re.fullmatch(r"\d+", f[:-4]))
        print("\n  %s/%s  (%d 个文件)" % (slot, item, len(files)))
        print("    数字变体:", nums if nums else "无")
        print("    其他:", others[:12] if others else "无")
        # 各尺寸大小
        for i in nums:
            k = prefix + "%d.png" % i
            print("      %d.png = %d 字节" % (i, z.getinfo(k).file_size))
