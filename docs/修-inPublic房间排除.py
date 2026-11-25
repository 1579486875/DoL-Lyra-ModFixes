# -*- coding: utf-8 -*-
"""修 inPublic：先排除「房间类」passage，避免 Inn Room / Flats Own Room 被判公共。"""
import re

P = r"E:\TAML\_dol\work\联动模组\系统联动补全\scripts\core.js"
s = open(P, encoding="utf-8").read()

if "PUBLIC_RE_V3" in s:
    print("⚠ 已修过，跳过")
    raise SystemExit(0)

OLD = '''function inPublic() {
		// 先排除自家 —— $exposed 是"暴露程度"不是"地点"，不能拿它判公共
		if (inOwnHome()) return false;
		return PUBLIC_RE_V2.test(currentPassage());
	}'''

NEW = '''function inPublic() {
		/* PUBLIC_RE_V3
		 * 先排除自家 —— $exposed 是"暴露程度"不是"地点"，不能拿它判公共。
		 * 再排除「房间类」passage —— Inn Room / Flats Own Room / Hospital Room
		 * 这类是私密空间，虽然名字里带 inn/hospital 但不该判公共。 */
		if (inOwnHome()) return false;
		var p = currentPassage();
		if (/\\b(Room|Bedroom|Bathroom|Bath|Shower|Cell|Cabin|Interior|Lounge)\\b/i.test(p)) return false;
		return PUBLIC_RE_V2.test(p);
	}'''

if OLD not in s:
    # 宽松匹配
    m = re.search(r"function inPublic\(\)\s*\{[^}]*\}", s)
    if not m:
        raise SystemExit("❌ 未找到 inPublic")
    print("原函数:", m.group(0)[:300])
    s2 = s[:m.start()] + NEW + s[m.end():]
else:
    s2 = s.replace(OLD, NEW, 1)

open(P, "w", encoding="utf-8").write(s2)
print("\n✅ 已更新，长度 %d -> %d" % (len(s), len(s2)))

# 校验
import re as _re
pub = _re.compile(r"street|alley|park|\broad\b|high street|shopping|market|beach|lake|forest|farm|school|shop|cafe|pub|club|brothel|prison|hospital|church|chapel|station|subway|metro|arcade|cinema|theatre|theater|office|factory|warehouse|dock|harbour|harbor|pier|plaza|square|gym|bathhouse|sauna|inn|hotel|motel|bar\b|restaurant|diner|bakery|library|museum|gallery|zoo|aquarium|stadium|arena", _re.I)
room = _re.compile(r"\b(Room|Bedroom|Bathroom|Bath|Shower|Cell|Cabin|Interior|Lounge)\b", _re.I)

print("\n=== 校验 ===")
for name in ("Bathroom", "Bedroom", "Bath", "Orphanage Bedroom", "Cottage Interior",
             "Flats Own Room", "Inn Room", "Inn", "High Street", "Park", "School",
             "Shopping Centre", "Hospital", "Church", "Station", "Hospital Room"):
    if room.search(name):
        r = "私密(房间)"
    elif pub.search(name):
        r = "公共"
    else:
        r = "非公共"
    print("  %-22s %s" % (name, r))
