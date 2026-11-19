"""查 i18n 里是否有 Pain: / Arousal: 等条目，以及为什么没应用。"""
import json
import re

I18N = r"E:\TAML\_dol\work\i18n_dict.json"
d = json.load(open(I18N, "r", encoding="utf-8"))
items = d["typeB"]["TypeBInputStoryScript"]

TARGETS = ["Pain:", "Arousal:", "Fatigue:", "Stress:", "Trauma:", "Control:", "Allure:",
           "Condoms:", "Genitals:", "Body", "Head", "Personality", "Makeup"]

print("=" * 94)
print("i18n 里的对应条目")
print("=" * 94)
for t in TARGETS:
    hits = []
    for it in items:
        f = it.get("f") or ""
        if f.strip() == t or f.strip() == t + " ":
            hits.append(it)
    if hits:
        print(f"\n  {t!r}: {len(hits)} 条")
        for it in hits[:2]:
            print(f"    pN={it.get('pN')} pos={it.get('pos')}")
            print(f"    f={it.get('f')!r}")
            print(f"    t={it.get('t')!r}")
    else:
        # 模糊找
        fuzzy = [it for it in items if (it.get("f") or "").strip().startswith(t)]
        print(f"\n  {t!r}: 精确无；前缀匹配 {len(fuzzy)} 条")
        for it in fuzzy[:2]:
            print(f"    pN={it.get('pN')} f={it.get('f')[:80]!r} t={(it.get('t') or '')[:80]!r}")

print("\n" + "=" * 94)
print("所有 f 里含 'Pain:' 的条目")
print("=" * 94)
n = 0
for it in items:
    f = it.get("f") or ""
    if "Pain:" in f:
        n += 1
        if n <= 6:
            print(f"\n  pN={it.get('pN')} pos={it.get('pos')}")
            print(f"    f={f[:200]!r}")
            print(f"    t={(it.get('t') or '')[:200]!r}")
print(f"\n共 {n} 条")
