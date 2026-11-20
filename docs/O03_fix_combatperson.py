"""O03：修 <<combatperson>> 的英文 description。"""
import html as H
import re

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")
g = H.unescape(data)

print("=" * 95)
print("<<combatperson>> 完整定义")
print("=" * 95)
PASSAGES = {}
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', g, re.S):
    PASSAGES[m.group(1)] = m.group(2)

for pname, body in PASSAGES.items():
    m = re.search(r'<<widget "combatperson">>(.*?)<</widget>>', body, re.S)
    if m:
        print(f"[{pname}]")
        print(m.group(1))
        break

print("\n" + "=" * 95)
print("修复")
print("=" * 95)
# 把 $description 换成 description_CN 优先
FIXES = [
    ('<<set _text_output to  $description>>',
     '<<set _text_output to $description_CN || $description>>'),
    ('<<set _text_output to $description>>',
     '<<set _text_output to $description_CN || $description>>'),
]

total = 0
for old, new in FIXES:
    hit = 0
    for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
        if a in data:
            c = data.count(a)
            data = data.replace(a, b)
            hit += c
    if hit:
        total += hit
        print(f"  OK {hit}x {old!r}")

if total:
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"\n共修 {total} 处")

g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
print("\n" + "=" * 95)
print("校验")
print("=" * 95)
print(f"  $description_CN || $description: {g2.count('$description_CN || $description')}")
print(f"  passage: {len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML,'rb').read().decode('utf-8','replace')))}")
