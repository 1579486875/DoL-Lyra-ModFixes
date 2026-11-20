"""O02（第2轮）：查 person1-6 等 widget 是否用 description_CN。"""
import html as H
import re

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

PASSAGES = {}
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', g, re.S):
    PASSAGES[m.group(1)] = m.group(2)

print("=" * 95)
print("所有 person* 类 widget")
print("=" * 95)
WIDGETS = ["person", "person1", "person2", "person3", "person4", "person5", "person6",
           "persons", "personsimple", "combatperson", "beast", "beasttype"]
for w in WIDGETS:
    for pname, body in PASSAGES.items():
        m = re.search(r'<<widget "' + re.escape(w) + r'">>(.*?)<</widget>>', body, re.S)
        if not m:
            continue
        wb = m.group(1)
        has_cn = "description_CN" in wb
        has_en = re.search(r"\$description(?!_CN)", wb) is not None
        print(f"  [<<{w}>>]  用_CN={has_cn}  用英文desc={has_en}  长度={len(wb)}")
        if has_en and not has_cn:
            print(f"    ⚠️ 只用英文: {wb[:300]!r}")
        break
    else:
        print(f"  [<<{w}>>]  ❌ widget 不存在")
