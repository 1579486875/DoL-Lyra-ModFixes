"""N07：修 description_CN 赋英文 title 的问题。"""
import html as H
import re

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    raise SystemExit("❌ index 形态异常")

FIXES = [
    # 命名 NPC：description_CN 应该是中文 title
    ('<<set $description to $NPCName[$npcnum[$npcrow.indexOf(_n)]].title>>\n\n'
     '<<set $description_CN to $NPCName[$npcnum[$npcrow.indexOf(_n)]].title>>',
     '<<set $description to $NPCName[$npcnum[$npcrow.indexOf(_n)]].title>>\n\n'
     '<<set $description_CN to setup.NPC_CN_TITLE($NPCName[$npcnum[$npcrow.indexOf(_n)]].title) || $NPCName[$npcnum[$npcrow.indexOf(_n)]].title>>'),
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
        print(f"  OK {hit}x")
    else:
        print(f"  MISS")

# 兜底：找所有 `<set $description_CN to X.title>>` 形式
PAT = re.compile(r'<<set \$description_CN to (\$NPCName\[[^\]]+\]\.title)>>')
found = PAT.findall(data)
if found:
    print(f"\n  兜底找到 {len(found)} 处只赋 title 的")
    for f in found[:3]:
        print(f"    {f!r}")

# 更通用：所有「description_CN to $xxx.title」的
PAT2 = re.compile(r'<<set (\$(?:description_CN|NPCList\[[^\]]+\]\.description_CN)) to (\$(?:NPCName\[[^\]]+\]|NPCList\[[^\]]+\])\.title)>>')
cnt = 0
for m in PAT2.finditer(data):
    old = m.group(0)
    new = f'<<set {m.group(1)} to setup.NPC_CN_TITLE({m.group(2)}) || {m.group(2)}>>'
    data = data.replace(old, new)
    cnt += 1
if cnt:
    total += cnt
    print(f"  OK 通用替换 {cnt} 处")

if total:
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"\n共修 {total} 处")

# 校验
g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
print("\n" + "=" * 90)
print("校验")
print("=" * 90)
print(f"  裸赋 title: {len(re.findall(r'description_CN to \\$NPCName\\[[^\\]]+\\]\\.title\\b(?! )', g))}")
print(f"  用 NPC_CN_TITLE: {g.count('setup.NPC_CN_TITLE($NPCName')}")
print(f"  passage: {len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML,'rb').read().decode('utf-8','replace')))}")
