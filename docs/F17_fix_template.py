"""F17：模板字符串里「变量名+中文」粘连修复（幂等）。"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r"<tw-passagedata[^>]*name=", data)) < 16000:
    print("[F17] ❌ index 形态异常，拒绝修改")
    sys.exit(1)

FIXES = [
    ("`用$_valueGucket.nameText浇灭 (0:01)`",
     "`用${$_valueGucket.nameText}浇灭 (0:01)`"),
    ("`在$_valueGucket.nameText中清洗 (0:05)`",
     "`在${$_valueGucket.nameText}中清洗 (0:05)`"),
    ("用_stick.state火把和它玩拔河游戏 (0:15)",
     "用${_stick.state}火把和它玩拔河游戏 (0:15)"),
]

total = 0
for old, new in FIXES:
    hit = 0
    for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
        if a in data:
            c = data.count(a)
            data = data.replace(a, b)
            hit += c
            break
    if hit:
        total += hit
        print(f"  ✅ {hit}x {old[:50]!r}")

if total:
    open(HTML, "wb").write(data.encode("utf-8"))

g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
TICK = chr(96)
BAD = {
    "nameText浇灭": g.count("nameText浇灭"),
    "nameText中清洗": g.count("nameText中清洗"),
}
ok = all(v == 0 for v in BAD.values())
print(f"[F17] 修 {total} 处  passage={len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML,'rb').read().decode('utf-8','replace')))}  " +
      "  ".join(f"{k}={v}" for k, v in BAD.items()) + f"  {'OK' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
