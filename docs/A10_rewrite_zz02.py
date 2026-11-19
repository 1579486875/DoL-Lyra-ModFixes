"""A10：确认 index 状态 + 重写 ZZ02 / Z03（不转义整文件）。"""
import html as H
import os
import re

WORK = r"E:\TAML\_dol\work"
HTML = os.path.join(WORK, "index_modded6.html")

raw = open(HTML, "rb").read().decode("utf-8", "replace")
n_raw = len(re.findall(r"<tw-passagedata", raw))
n_esc = len(re.findall(r"&lt;tw-passagedata", raw))
print("=" * 90)
print(f"index 当前状态")
print("=" * 90)
print(f"  明文 passage: {n_raw}")
print(f"  转义 passage: {n_esc}")
print(f"  开头: {raw[:70]!r}")
print(f"  判定: {'✅ 明文（正确）' if n_raw > 10000 else '❌ 转义（错误）'}")

# 检查本轮的翻译修复是否还在
print("\n" + "=" * 90)
print("本轮修复是否还在（在 0A316E37 基线里可能没有）")
print("=" * 90)
for kw in ["Tendrils of 深色ness", "黑暗的触须", "curvy: \"Curvy\"", "curvy: \"曲线\""]:
    print(f"  {kw!r}: {raw.count(kw)}")

# 重写 ZZ02（不转义整文件）
print("\n" + "=" * 90)
print("重写 ZZ02_residue_fix.py（明文直接替换，不 escape）")
print("=" * 90)

NEW_ZZ02 = r'''"""ZZ02：截图残留修复（幂等，明文直接替换，不 escape 整文件）。"""
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")
n = 0

# 安全阀：index 必须是明文形态
if len(re.findall(r"<tw-passagedata", data)) < 10000:
    print("[ZZ02] ❌ index 不是明文形态，拒绝修改")
    sys.exit(1)

# 1) Tendrils of 深色ness
for old, new in [
    ("Tendrils of 深色ness whip and writhe against your skin as",
     "黑暗的触须抽打着你的皮肤，缠绕扭动，同时"),
    ("Tendrils of 深色ness writhe against your skin as",
     "黑暗的触须缠绕扭动着你的皮肤，同时"),
]:
    if old in data:
        c = data.count(old); data = data.replace(old, new); n += c

# 2) You've gained <<moneyGain
for pat in (re.compile(r"You\\'ve gained (?=<<moneyGain)"),
            re.compile(r"You\\'ve gained (?=&lt;&lt;moneyGain)")):
    c = len(pat.findall(data))
    if c:
        data = pat.sub("你获得了 ", data); n += c

# 3) textMap 身形
Q = chr(34)
for a, b in [
    ("{ 0: " + Q + "Slender" + Q + ", 1: " + Q + "Slim" + Q + ", 2: " + Q + "Modest" + Q + ", 3: " + Q + "Cushioned" + Q + ", 4: " + Q + "Soft" + Q + ", 5: " + Q + "Round" + Q + ", 6: " + Q + "Plump" + Q + ", 7: " + Q + "Large" + Q + ", 8: " + Q + "Huge" + Q + " }",
     "{ 0: " + Q + "纤细" + Q + ", 1: " + Q + "瘦削" + Q + ", 2: " + Q + "适中" + Q + ", 3: " + Q + "丰满" + Q + ", 4: " + Q + "柔软" + Q + ", 5: " + Q + "圆润" + Q + ", 6: " + Q + "丰腴" + Q + ", 7: " + Q + "硕大" + Q + ", 8: " + Q + "巨大" + Q + " }"),
    ("{ 0: " + Q + "Slender" + Q + ", 1: " + Q + "Slim" + Q + ", 2: " + Q + "Modest" + Q + ", 3: " + Q + "Cushioned" + Q + " }",
     "{ 0: " + Q + "纤细" + Q + ", 1: " + Q + "瘦削" + Q + ", 2: " + Q + "适中" + Q + ", 3: " + Q + "丰满" + Q + " }"),
    ('textMap: { classic: "Classic", slender: "Slender", curvy: "Curvy", soft: "Soft" }',
     'textMap: { classic: "经典", slender: "瘦长", curvy: "曲线", soft: "柔软" }'),
]:
    c = data.count(a)
    if c:
        data = data.replace(a, b); n += c

# 4) 兽人类型（EXTRA 表补键）—— 直接在明文上做
m = re.search(r"var EXTRA = \{(.*?)\};", data, re.S)
if m:
    body = m.group(1)
    have = set(re.findall(r'"([a-z]+)"\s*:', body))
    ADD = {
        "doggirl": "狗娘", "dogboy": "狗男", "catgirl": "猫娘", "catboy": "猫男",
        "wolfgirl": "狼娘", "wolfboy": "狼男", "beargirl": "熊娘", "bearboy": "熊男",
        "pigboy": "猪男", "piggirl": "猪娘", "foxgirl": "狐娘", "foxboy": "狐男",
        "dolphingirl": "海豚娘", "dolphinboy": "海豚男", "horsegirl": "马娘", "horseboy": "马男",
        "harpygirl": "鹰身女妖", "harpyboy": "鹰身男妖", "slimegirl": "史莱姆娘", "slimeboy": "史莱姆男",
        "plantgirl": "植物娘", "plantboy": "植物男",
    }
    add = ['            "' + k + '": "' + v + '",' for k, v in ADD.items() if k not in have]
    if add:
        nb = body.rstrip()
        if not nb.endswith(","):
            nb += ","
        nb += "\n" + "\n".join(add) + "\n        "
        data = data[:m.start(1)] + nb + data[m.end(1):]
        n += len(add)

if n:
    open(HTML, "wb").write(data.encode("utf-8"))

# 校验（安全阀：必须仍是明文）
g = open(HTML, "rb").read().decode("utf-8", "replace")
ok_pass = len(re.findall(r"<tw-passagedata", g)) > 10000
bad = {
    "Tendrils 深色ness": g.count("Tendrils of 深色ness"),
    "Youve gained+money": len(re.findall(r"You\\'ve gained (?=(?:<<|&lt;&lt;)moneyGain)", g)),
    "curvy:Curvy": g.count('curvy: "Curvy"'),
}
print("[ZZ02] 修 %d 处  passage=%d %s  %s" % (
    n, len(re.findall(r"<tw-passagedata", g)),
    "OK" if ok_pass else "BROKEN",
    "  ".join("%s=%d" % (k, v) for k, v in bad.items())))
sys.exit(0 if (ok_pass and all(v == 0 for v in bad.values())) else 1)
'''
open(os.path.join(WORK, "ZZ02_residue_fix.py"), "w", encoding="utf-8").write(NEW_ZZ02)
print("  ✅ ZZ02 已重写（不 escape）")
