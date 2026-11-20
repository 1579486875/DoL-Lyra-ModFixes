"""T10：修 Template.add 的三类问题（幂等）。

1. 模板名被翻译：Template.add("欣赏着" → Template.add("admires"
2. 20 条英文残留（用 T08 提取的实际文本，含 \\' 转义）
3. 之前 P09 的块定位似有失效，这里改用「独特文本全局替换」——这些串不会误伤
"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[T10] index 形态异常")
    sys.exit(1)

MARK = "[T10]"
g0 = H.unescape(data)
if MARK in g0:
    print("[T10] 已存在，跳过")
    sys.exit(0)

total = 0


def rep(old, new, label=""):
    """精确替换（同时尝试转义/未转义两种形态）。"""
    global data, total
    hit = 0
    for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
        if a in data:
            c = data.count(a)
            data = data.replace(a, b)
            hit += c
            break
    if hit:
        total += hit
        print(f"  OK {hit}x  {label or old[:55]!r}")
    return hit


print("=" * 90)
print("1. 恢复被翻译的模板名")
print("=" * 90)
rep('Template.add("欣赏着"', 'Template.add("admires"', 'Template.add("欣赏着" -> "admires"')

print("\n" + "=" * 90)
print("2. ?garden（5 条）")
print("=" * 90)
for en, cn in (("prune flowers", "修剪花朵"), ("prune trees", "修剪树木"),
               ("prune bushes", "修剪灌木"), ("water flowers", "浇花"),
               ("remove weeds", "除草")):
    rep('"' + en + '"', '"' + cn + '"', en)

print("\n" + "=" * 90)
print("3. ?admires 残留")
print("=" * 90)
rep('"eyes up"', '"上上下下打量"', "eyes up")

print("\n" + "=" * 90)
print("4. ?gwylanItem（3 条）")
print("=" * 90)
for en, cn in (("baseball bat", "棒球棍"), ("snow globe", "雪花球"),
               ("magic 8-ball", "魔法八号球")):
    rep('"' + en + '"', '"' + cn + '"', en)

print("\n" + "=" * 90)
print("5. ?chatter1（6 条，注意 \\' 转义）")
print("=" * 90)
C1 = [
    ("If you think about it, neither of us are really here.",
     "你仔细想想，其实我们俩谁都不在这里。"),
    ("Hey, listen. You hear that? It\\'s nothing.",
     "嘿，听着。你听到了吗？什么也没有。"),
    ("Don\\'t knock it \\'till you try it. Jazz metal just works.",
     "别没试过就贬低它。爵士金属就是行。"),
    ("Winter\\'s actually kinda hot, in a fossil kinda way.",
     "冬天其实挺性感的，有种化石般的美。"),
    ("I\\'d let a wolf knot me, to be honest.",
     "老实说，我倒愿意让狼给我打个结。"),
    ("Someone said they saw a whale that had, like, tentacles, like a squid. Think squids and whales finally put their differences aside and got busy?",
     "有人说他们看到过一头长着触手的鲸鱼，跟鱿鱼似的。你说鱿鱼和鲸鱼最后是不是放下分歧、忙起来了？"),
]
for en, cn in C1:
    # data 里是字面 \" 形式（反引号 + 单引号），所以直接拼引号
    if rep('"' + en + '"', '"' + cn + '"', en[:50]):
        continue
    # 再试未转义形态
    rep('"' + en.replace("\\'", "'") + '"', '"' + cn + '"', en[:50] + " (plain)")

print("\n" + "=" * 90)
print("6. ?chatter2（5 条）")
print("=" * 90)
C2 = [
    ("Pretty sure you\\'re not supposed to come to school drunk.",
     "我很确定你不该喝醉了来上学。"),
    ("I\\'m calling the police.", "我要报警了。"),
    ("I gotta get that restraining order. For real, this time.",
     "我得去申请那份限制令了。这次是认真的。"),
    ("Can I peg you?", "我能用假阳具操你吗？"),
    ("Can you make like a tree and die for the winter?",
     "你能不能像树一样，冬天就死掉？"),
]
for en, cn in C2:
    if rep('"' + en + '"', '"' + cn + '"', en[:50]):
        continue
    rep('"' + en.replace("\\'", "'") + '"', '"' + cn + '"', en[:50] + " (plain)")

# 打标记
data = data.replace(H.escape('<<widget "generateshoppage">>', quote=False),
                    H.escape('<!-- [T10] Template.add 英文清理 -->' + '<<widget "generateshoppage">>', quote=False), 1)

open(HTML, "wb").write(data.encode("utf-8"))
print(f"\n共修 {total} 处")

# ---- 校验 ----
g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
print("\n" + "=" * 90)
print("校验")
print("=" * 90)

names = re.findall(r'Template\.add\(\s*"([^"]+)"', g)
cn_names = [n for n in names if re.search(r"[\u4e00-\u9fff]", n)]
print(f"  模板名含中文: {len(cn_names)}  {cn_names}")

# 重新提取英文
BLOCKS = []
for m in re.finditer(r'Template\.add\(\s*"([^"]+)"\s*,\s*', g):
    start = m.end()
    i = start
    depth = 1
    while i < len(g) and depth > 0:
        if g[i] == "(":
            depth += 1
        elif g[i] == ")":
            depth -= 1
        i += 1
    BLOCKS.append((m.group(1), start, i))

left = []
for name, s, e in BLOCKS:
    blk = g[s:e]
    for raw in re.findall(r'"((?:[^"\\]|\\.)*)"', blk):
        plain = raw.replace("\\'", "'").replace('\\"', '"')
        if re.search(r"[\u4e00-\u9fff]", plain):
            continue
        if len(re.findall(r"[A-Za-z]{2,}", plain)) < 2:
            continue
        if re.fullmatch(r"[a-z_]+", plain):
            continue
        left.append(f"?{name}: {plain[:80]}")

print(f"  剩余英文: {len(left)}")
for x in left:
    print(f"    {x}")

print(f"\n  passage: {len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML,'rb').read().decode('utf-8','replace')))}")
sys.exit(0 if (not cn_names and len(left) == 0) else 1)
