"""查 i18n 里哪条翻译会产生 ch一个racteristics / 滑行 / 爬动。"""
import json
import re

I18N = r"E:\TAML\_dol\work\i18n_dict.json"
d = json.load(open(I18N, "r", encoding="utf-8"))
items = d["typeB"]["TypeBInputStoryScript"]

print("=" * 94)
print("1) t 里含「一个」但与 characteristics 有关的")
print("=" * 94)
for it in items:
    t = it.get("t") or ""
    f = it.get("f") or ""
    if "一个" in t and ("racte" in t or "aracte" in t or "character" in f.lower()):
        print(f"  pN={it.get('pN')} pos={it.get('pos')}")
        print(f"    f={f[:150]!r}")
        print(f"    t={t[:150]!r}")

print("\n" + "=" * 94)
print("2) f 里含 'aracte' 的条目")
print("=" * 94)
n = 0
for it in items:
    f = it.get("f") or ""
    if "aracte" in f:
        n += 1
        if n <= 10:
            print(f"  pN={it.get('pN')} pos={it.get('pos')}")
            print(f"    f={f[:180]!r}")
            print(f"    t={(it.get('t') or '')[:180]!r}")
print(f"  共 {n} 条")

print("\n" + "=" * 94)
print("3) t 是 '滑行' 或 '爬动' 的条目")
print("=" * 94)
for it in items:
    t = (it.get("t") or "").strip()
    if t in ("滑行", "爬动"):
        print(f"  pN={it.get('pN')} pos={it.get('pos')}")
        print(f"    f={it.get('f')!r}")
        print(f"    t={t!r}")

print("\n" + "=" * 94)
print("4) f 是 characteristics 或 flesh_text 的条目")
print("=" * 94)
for it in items:
    f = (it.get("f") or "").strip()
    if f in ("characteristics", "flesh_text"):
        print(f"  pN={it.get('pN')} pos={it.get('pos')}")
        print(f"    f={f!r}")
        print(f"    t={(it.get('t') or '')!r}")
