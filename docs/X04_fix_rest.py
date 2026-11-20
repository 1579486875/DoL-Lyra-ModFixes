"""X04：修剩余 7 处 _args 泄漏（逐个精确）。"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[X04] index 形态异常")
    sys.exit(1)

MARK = "[X04]"
g0 = H.unescape(data)
if MARK in g0:
    print("[X04] 已存在，跳过")
    sys.exit(0)

FIXES = [
    # 1. 裸 _args[0] 单独一行
    ('<<if $drugged gte 1>>药物抑制了你的声音，你的哭泣软弱无力。<</if>>\n\t\t<<else>>\n\t\t\t_args[0]\n\t\t<</if>>',
     '<<if $drugged gte 1>>药物抑制了你的声音，你的哭泣软弱无力。<</if>>\n\t\t<<else>>\n\t\t\t<<= _args[0]>>\n\t\t<</if>>'),
    # 2. + _args[0]%通过率
    ('<span class="green">+ _args[0]%通过率</span>',
     '<span class="green">+ <<= _args[0]>>%通过率</span>'),
    # 3. _args[0]不足.
    ('<<print _icon>><</if>> _args[0]不足.</span>',
     '<<print _icon>><</if>> <<= _args[0]>>不足.</span>'),
    # 4. 错误：无效动作_args[0]（两处，靠后的那条更完整）
    ('<span class="red">错误：无效动作_args[0]: $shopHunt.actors[_args[0]].state。请报告这个问题！</span>',
     '<span class="red">错误：无效动作<<= _args[0]>>: <<= $shopHunt.actors[_args[0]].state>>。请报告这个问题！</span>'),
    # 5. <<default>>_args[0].name
    ('<<default>>_args[0].name',
     '<<default>><<= _args[0].name>>'),
    # 6. 选项无效：_args[0]
    ('<span class="red">选项无效：_args[0]</span>',
     '<span class="red">选项无效：<<= _args[0]>></span>'),
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
        print(f"  OK {hit}x  {old[:65]!r}")
    else:
        print(f"  MISS     {old[:65]!r}")

data = data.replace(
    H.escape('<<widget "generateshoppage">>', quote=False),
    H.escape('<!-- [X04] ==== -->' + '<<widget "generateshoppage">>', quote=False), 1)

open(HTML, "wb").write(data.encode("utf-8"))
print(f"\n共修 {total} 处")

# ---- 改进判据后的校验 ----
print("\n" + "=" * 90)
print("校验（改进判据：排除属性/注释/宏内）")
print("=" * 90)
g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))

left = []
for m in re.finditer(r"_args\[(\d+)\]", g):
    pos = m.start()
    pre = g[max(0, pos - 600):pos]
    # 在宏里
    if pre.rfind("<<") > pre.rfind(">>"):
        continue
    # 在 HTML 属性里（@xxx="..." 或 xxx="..."）
    lt = pre.rfind("<")
    gt = pre.rfind(">")
    in_tag = lt > gt
    # 在 HTML 注释里
    if g.rfind("<!--", 0, pos) > g.rfind("-->", 0, pos):
        continue
    # 在 JS 注释里
    if g.rfind("/*", 0, pos) > g.rfind("*/", 0, pos):
        continue
    # 前后有中文
    ctx = g[max(0, pos - 40):pos + 50]
    if not re.search(r"[\u4e00-\u9fff]", ctx):
        continue
    # 在标签内但不在引号属性里 → 可能是文本
    if in_tag:
        seg = pre[lt:]
        if '"' in seg or "'" in seg:
            continue    # 属性值里
    left.append((pos, m.group(0), ctx))

print(f"  正文 _args 残留: {len(left)} 处")
for pos, v, ctx in left:
    print(f"    @{pos}  {v}  {ctx[:90]!r}")

print(f"\n  passage: {len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML,'rb').read().decode('utf-8','replace')))}")
sys.exit(0 if len(left) == 0 else 1)
