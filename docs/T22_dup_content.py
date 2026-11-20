"""T22：查重复 widget 的内容是否一致 + CafeFoodList 丢词。"""
import html as H
import re

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

PASSAGES = {}
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', g, re.S):
    PASSAGES[m.group(1)] = m.group(2)


def get_widget(pname, wname):
    body = PASSAGES.get(pname, "")
    m = re.search(r'<<widget\s+"' + re.escape(wname) + r'"[^>]*>>(.*?)<</widget>>', body, re.S)
    return m.group(1) if m else None


WRAITH = ["effectsWraith", "chastityBreakWraith", "apologyWraith", "rescueWraith",
          "ejacW", "ejaculation-wraith", "kissWraith", "wHunt", "wPersist",
          "exitWraith", "rngWraith", "rngWraithSocial", "wraithEventStreet",
          "wraithEventSewers", "wraithIntro", "wraithCaught"]

print("=" * 95)
print("1. Wraith 系：Widgets Repair vs Widgets Wraith 内容对比")
print("=" * 95)
same = 0
diff = 0
for w in WRAITH:
    a = get_widget("Widgets Repair", w)
    b = get_widget("Widgets Wraith", w)
    if a is None or b is None:
        print(f"  ?? {w}: Repair={'有' if a is not None else '无'} Wraith={'有' if b is not None else '无'}")
        continue
    if a.strip() == b.strip():
        same += 1
    else:
        diff += 1
        print(f"  ❌ {w}: 长度 Repair={len(a)} Wraith={len(b)}")
        # 找差异
        if len(a) > 30 and len(b) > 30:
            print(f"     Repair 前 100: {a[:100]!r}")
            print(f"     Wraith 前 100: {b[:100]!r}")
print(f"\n  相同: {same}  不同: {diff}")

print("\n" + "=" * 95)
print("2. blackjackCaughtCheatingSurrender（同 passage ×2）")
print("=" * 95)
body = PASSAGES.get("Widgets Blackjack", "")
ms = list(re.finditer(r'<<widget\s+"blackjackCaughtCheatingSurrender"[^>]*>>(.*?)<</widget>>', body, re.S))
print(f"  出现 {len(ms)} 次")
for i, m in enumerate(ms):
    print(f"  [{i}] 长度 {len(m.group(1))}")
    print(f"      {m.group(1)[:200]!r}")

print("\n" + "=" * 95)
print("3. setup.CafeFoodList_cn_name 两次赋值")
print("=" * 95)
for m in re.finditer(r'<<set\s+setup\.CafeFoodList_cn_name\s+to\s+"([^"]*)"', g):
    v = m.group(1)
    print(f"  @{m.start()}  长度 {len(v)}")
    print(f"    {v[:250]!r}")

print("\n" + "=" * 95)
print("4. cards_naked_end / cards_oral_options（跨 passage）")
print("=" * 95)
for w in ("cards_naked_end", "cards_oral_options"):
    a = get_widget("Widgets Blackjack", w)
    b = get_widget("Widgets High Low", w)
    if a is None or b is None:
        print(f"  ?? {w}")
        continue
    print(f"  {w}: Blackjack={len(a)} HighLow={len(b)}  相同={a.strip() == b.strip()}")
