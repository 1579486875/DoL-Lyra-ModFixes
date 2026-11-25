# -*- coding: utf-8 -*-
"""查 cdp_suite.js 的 evalJs / send 超时处理，找 __timeout 的来源。"""
import re

P = r"E:\TAML\_dol\work\cdp_suite.js"
s = open(P, encoding="utf-8").read()

print("=== __timeout 出现处 ===")
for mm in re.finditer(r"__timeout", s):
    print("@%d: %s" % (mm.start(), s[max(0, mm.start() - 400):mm.start() + 200].replace("\n", " ")[:600]))

print("\n\n=== send 函数定义 ===")
m = re.search(r"const send\s*=", s)
if m:
    print(s[m.start():m.start() + 1200])

print("\n\n=== evalJs 函数定义 ===")
m2 = re.search(r"const evalJs\s*=", s)
if m2:
    print(s[m2.start():m2.start() + 1200])
