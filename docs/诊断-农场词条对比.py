# -*- coding: utf-8 -*-
"""对比原版与当前的 farm_text_many / farm_text，列出所有词条差异。"""
import html as H
import re
import zipfile

# 原版
z = zipfile.ZipFile(r"E:\TAML\_dol\apk\DoL-Lyra-besc-hikari-ucb-0.5.12.13.apk")
g_en = H.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))

# 当前
g_zh = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

for wname in ("farm_text_many", "farm_text"):
    print("=" * 70)
    print("widget:", wname)
    print("=" * 70)
    for tag, g in (("原版", g_en), ("当前", g_zh)):
        m = re.search(r'<<widget\s+"%s"[^>]*>>(.*?)<</widget>>' % wname, g, re.S)
        if not m:
            print("  [%s] 未找到" % tag)
            continue
        body = m.group(1)
        # 提取所有 _text_output 赋值
        vals = re.findall(r'_text_output to "([^"]*)"', body)
        print("  [%s] len=%d 输出值: %s" % (tag, len(body), vals))
    print()
