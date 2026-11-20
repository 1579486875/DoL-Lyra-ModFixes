"""O04：修 combatperson 剩余的 $description 拼接。"""
import html as H
import re

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

FIXES = [
    # role 分支
    ('<<set _text_output to $description +  setup.NPC_CN_TITLE(',
     '<<set _text_output to ($description_CN || $description) +  setup.NPC_CN_TITLE('),
    # 男人
    ('<<set _text_output to $description + "男人">>',
     '<<set _text_output to ($description_CN || $description) + "男人">>'),
    # 女人
    ('<<set _text_output to "" + $description + "女人">>',
     '<<set _text_output to ($description_CN || $description) + "女人">>'),
]

total = 0
print("=" * 90)
print("修复")
print("=" * 90)
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
        print(f"  OK {hit}x {old[:70]!r}")
    else:
        print(f"  MISS {old[:70]!r}")

if total:
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"\n共修 {total} 处")

# 校验：combatperson widget 里不应有裸 $description
g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
PASSAGES = {}
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', g, re.S):
    PASSAGES[m.group(1)] = m.group(2)

print("\n" + "=" * 90)
print("校验 combatperson")
print("=" * 90)
for pname, body in PASSAGES.items():
    m = re.search(r'<<widget "combatperson">>(.*?)<</widget>>', body, re.S)
    if not m:
        continue
    wb = m.group(1)
    # 找裸 $description（不带 _CN 且不带 ||）
    bare = []
    for mm in re.finditer(r"\$description(?!_CN)", wb):
        ctx = wb[max(0, mm.start() - 30):mm.start() + 40]
        if "|| $description" in ctx:
            continue
        bare.append(ctx)
    print(f"  裸 $description: {len(bare)}")
    for b in bare:
        print(f"    {b!r}")
    break

print(f"\n  passage: {len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML,'rb').read().decode('utf-8','replace')))}")
