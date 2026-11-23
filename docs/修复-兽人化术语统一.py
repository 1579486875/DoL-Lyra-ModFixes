# -*- coding: utf-8 -*-
"""统一兽人化术语：「犬人」→「狗人」（与「猪人」「奶牛人」同风格）。"""
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))

n = raw.count("犬人")
print("「犬人」出现:", n, "处")
if n == 0:
    print("无需修改")
    sys.exit(0)

raw2 = raw.replace("犬人", "狗人")
print("已全部替换为「狗人」")

npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
print("passage:", npass, "->", npass2)
if npass2 != npass:
    sys.exit(1)
open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写入")
