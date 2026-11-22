# -*- coding: utf-8 -*-
"""移除无效的 NoTraumaClamp 模组，直接改 index 里的 traumaClamp 逻辑（高创伤不减容貌）。"""
import base64
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
MOD = r"E:\TAML\_dol\work\_downloads\NoTraumaClamp_0.2.1.zip"

raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))

# 1) 移除模组
m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
block = m.group(1)
b64 = base64.b64encode(open(MOD, "rb").read()).decode("ascii")
if b64 in block:
    pat = re.compile(r',?\s*"' + re.escape(b64) + r'"')
    block, cnt = pat.subn("", block, count=1)
    print("移除 NoTraumaClamp:", cnt)
    raw = raw[:m.start(1)] + block + raw[m.end(1):]

# 2) 直接改 traumaClamp 的 beauty 扣减
OLD = "V.beauty -= overflow * 0.2;"
NEW = "V.beauty -= 0; /* [DoL-Lyra] 高创伤不减容貌 */"
c = raw.count(OLD)
print("beauty 扣减出现:", c)
if c != 1:
    print("⚠ 出现次数异常，拒绝修改")
    sys.exit(1)
raw = raw.replace(OLD, NEW, 1)

npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
m2 = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
cnt2 = len(re.findall(r'"[A-Za-z0-9+/=\s]{200,}"', m2.group(1)))
print("passage:", npass, "->", npass2, "| 模组数:", cnt2)
if npass2 != npass:
    print("❌ passage 变化")
    sys.exit(1)
open(HTML, "wb").write(raw.encode("utf-8"))
print("✅ 写入")
