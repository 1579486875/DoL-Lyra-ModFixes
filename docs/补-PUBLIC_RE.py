# -*- coding: utf-8 -*-
"""第3轮修：补全 PUBLIC_RE 的公共场所覆盖。

原正则：
  street|alley|park|road|high street|shopping|market|beach|lake|forest|farm|
  school|shop|cafe|pub|club|brothel|prison

缺失的常见公共场景：医院 / 教堂 / 车站 / 地铁 / 商场外的游乐场 / 影院 /
工厂 / 仓库 / 办公楼 / 澡堂 / 沙滩外的码头等。

注意不能误伤：
  Bathroom（浴室）—— 不含 bath 关键词，安全
  Bedroom（卧室）—— 不含 bed，安全
"""
import re

P = r"E:\TAML\_dol\work\联动模组\系统联动补全\scripts\core.js"
s = open(P, encoding="utf-8").read()

if "PUBLIC_RE_V2" in s:
    print("⚠ 已补过，跳过")
    raise SystemExit(0)

OLD = r'PUBLIC_RE = /street|alley|park|road|high street|shopping|market|beach|lake|forest|farm|school|shop|cafe|pub|club|brothel|prison/i;'
NEW = r'''PUBLIC_RE_V2 = /street|alley|park|\broad\b|high street|shopping|market|beach|lake|forest|farm|school|shop|cafe|pub|club|brothel|prison|hospital|church|chapel|station|subway|metro|arcade|cinema|theatre|theater|office|factory|warehouse|dock|harbour|harbor|pier|plaza|square|gym|bathhouse|sauna|inn|hotel|motel|bar\b|restaurant|diner|bakery|library|museum|gallery|zoo|aquarium|stadium|arena/i;'''

if OLD not in s:
    # 宽松匹配
    m = re.search(r"PUBLIC_RE\s*=\s*/[^;]+;", s)
    if not m:
        raise SystemExit("❌ 未找到 PUBLIC_RE")
    print("原:", m.group(0))
    s2 = s[:m.start()] + NEW + s[m.end():]
else:
    print("原:", OLD)
    s2 = s.replace(OLD, NEW, 1)

print("新:", NEW[:120], "...")

# 校验不误伤关键场景
import re as _re
pat = _re.compile(NEW.split("=", 1)[1].strip().rstrip(";"))
for name in ("Bathroom", "Bedroom", "Bath", "Orphanage Bedroom", "Cottage Interior",
             "Flats Own Room", "Inn Room", "High Street", "Park", "School",
             "Shopping Centre", "Hospital", "Church", "Station"):
    hit = bool(pat.search(name))
    print("  %-22s %s" % (name, "公共" if hit else "非公共"))

open(P, "w", encoding="utf-8").write(s2)
print("\n✅ 已更新，长度 %d -> %d" % (len(s), len(s2)))
