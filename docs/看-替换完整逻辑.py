# -*- coding: utf-8 -*-
"""看 NPC 类型名替换的完整逻辑（含所有格处理）。"""
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")

i = 94618000
print(h[i:i + 3000])
