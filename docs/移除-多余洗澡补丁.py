# -*- coding: utf-8 -*-
"""移除「系统联动补全」里多余的 BATH_EXIT_FIX（已改为直接修 BasicNeeds）。"""
import re

P = r"E:\TAML\_dol\work\联动模组\系统联动补全\scripts\core.js"
s = open(P, encoding="utf-8").read()

if "BATH_EXIT_FIX" not in s:
    print("⚠ 没有 BATH_EXIT_FIX，无需移除")
    raise SystemExit(0)

# 定位整段：从「附加：跨地点洗澡后回错浴室修复」注释开始，到 window.系统联动 = { 之前
START = "\t/* ============ 附加：跨地点洗澡后回错浴室修复 ============ */"
END = "\twindow.系统联动 = {"

i = s.find(START)
j = s.find(END)
if i < 0 or j < 0 or j < i:
    raise SystemExit("❌ 未找到完整段落")

removed = j - i
s2 = s[:i] + s[j:]

assert "BATH_EXIT_FIX" not in s2, "移除不完整"
open(P, "w", encoding="utf-8").write(s2)
print("✅ 已移除 %d 字符，长度 %d -> %d" % (removed, len(s), len(s2)))
