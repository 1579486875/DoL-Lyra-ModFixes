"""第 23 轮：验证候选漏翻在 i18n 表里是否有近似匹配。"""
import json
import os
import re

I18N = r"E:\TAML\_dol\work\i18n_dict.json"

CANDIDATES = [
    "It exits with a pop, prompting Gwylan to slowly moan.",
    "You're free to explore the building during the day.",
    "Don't enter any doors marked for staff, and make sure to follow instructions.",
    "They turn to regard you.",
    "You've been displaying your body in inappropriate ways, then claiming others stripped you.",
    "You both stop for a moment.",
    "Its wooden face is the last thing you see as the gloom envelops you.",
    "Smart thinking, with the light.",
    "You open your eyes to see the Black Wolf curling up beside you.",
    "The Black Wolf drops some by your side before moving away.",
    "A single white light turns on above you, and the din of the dark room falls quiet.",
    "You can't see beyond the edge of the stage, but you can feel the eyes on you.",
    "Paper flies everywhere as both of you tumble to the ground.",
    "Your heart continues to beat rapidly.",
    "You hear a whistle blow behind you.",
    "You hear a tear.",
    "It's a look you've seen before.",
    "Everything will be fine,\" you say.",
    "The key to the belt is long lost.",
]


def load():
    import pickle
    cache = I18N + ".pkl"
    d = None
    try:
        if os.path.exists(cache) and os.path.getmtime(cache) > os.path.getmtime(I18N):
            with open(cache, "rb") as f:
                d = pickle.load(f)
    except Exception:
        d = None
    if d is None:
        with open(I18N, "r", encoding="utf-8") as f:
            d = json.load(f)
    return d.get("typeB", {}).get("TypeBInputStoryScript", [])


items = load()
print(f"i18n {len(items):,} 条")

# 建索引：小写去标点 -> (f, t)
index = {}
for it in items:
    f = it.get("f")
    if not f:
        continue
    k = re.sub(r"[^a-z0-9]+", "", f.lower())[:80]
    if k:
        index.setdefault(k, []).append(it)


def normkey(s):
    return re.sub(r"[^a-z0-9]+", "", s.lower())[:80]


print("\n" + "=" * 90)
print("逐条验证")
print("=" * 90)

found = []
notfound = []
for c in CANDIDATES:
    k = normkey(c)
    hits = index.get(k, [])
    if hits:
        it = hits[0]
        print(f"\n✅ 找到: {c[:70]!r}")
        print(f"   i18n f: {it.get('f','')[:100]!r}")
        print(f"   i18n t: {str(it.get('t',''))[:100]!r}")
        found.append((c, it))
    else:
        # 前缀模糊找
        pref = k[:40]
        fuzzy = [kk for kk in index if kk.startswith(pref)]
        if fuzzy:
            it = index[fuzzy[0]][0]
            print(f"\n⚠️ 近似: {c[:70]!r}")
            print(f"   i18n f: {it.get('f','')[:100]!r}")
            print(f"   i18n t: {str(it.get('t',''))[:100]!r}")
            found.append((c, it))
        else:
            print(f"\n❌ 未找到: {c[:80]!r}")
            notfound.append(c)

print("\n" + "=" * 90)
print(f"结果：找到 {len(found)} / 未找到 {len(notfound)}")
print("=" * 90)
if notfound:
    print("\n真正需要翻译的:")
    for c in notfound:
        print(f"  {c!r}")
