# -*- coding: utf-8 -*-
"""查 look() 函数的匹配逻辑，看它怎么处理 dogboy's。"""
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")

# 找 look 定义（在 NPC_CN_TYPE 附近）
i = h.find("NPC_CN_TYPE = function")
print("NPC_CN_TYPE @", i)
seg = h[max(0, i - 6000):i + 500]
print("\n=== 前面 6000 字符（找 look 定义）===")
m = re.search(r"function look\s*\([^)]*\)\s*\{", seg)
if m:
    start = seg.index("{", m.start())
    depth = 0
    j = start
    while j < len(seg):
        if seg[j] == "{":
            depth += 1
        elif seg[j] == "}":
            depth -= 1
            if depth == 0:
                break
        j += 1
    print(seg[m.start():j + 1])
else:
    print("未找到 look 定义，打印 NPC_CN_TYPE 前 3000 字符：")
    print(seg[:3000])
