"""X03：修两类真问题（幂等）。

1. widget 里的 _args[N] 泄漏到正文（24 处）
   <<widget "combatpromiscuous1">><span @class="_classList">露出癖 _args[0]</span>
   → 必须用 <<= _args[0]>> 才会求值

2. 双重转义 &amp;lt;&amp;lt; （20 处）
   会显示字面 <<link [[...]]>> 而不是可点击链接
"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[X03] index 形态异常")
    sys.exit(1)

MARK = "[X03]"
g0 = H.unescape(data)
if MARK in g0:
    print("[X03] 已存在，跳过")
    sys.exit(0)

total = 0

# ============================================================
# 1. _args[N] 泄漏 —— 精确定位「不在 << >> 里」的
# ============================================================
print("=" * 90)
print("1. 修 _args[N] 泄漏")
print("=" * 90)

# 先找出所有位置
g = g0
targets = []
for m in re.finditer(r"_args\[(\d+)\]", g):
    pre = g[max(0, m.start() - 600):m.start()]
    if pre.rfind("<<") > pre.rfind(">>"):
        continue          # 在宏里，正常
    # 前后必须有中文（说明在正文里）
    ctx = g[max(0, m.start() - 40):m.start() + 50]
    if not re.search(r"[\u4e00-\u9fff]", ctx):
        continue
    targets.append((m.start(), m.group(0), ctx))

print(f"  正文里的 _args[N]: {len(targets)} 处")
for pos, v, ctx in targets:
    print(f"    @{pos}  {v}  {ctx[:80]!r}")

# 替换策略：把「正文里的 _args[N]」替换成 `<<=_args[N]>>`（在 raw 上做要 escape）
# 由于 raw 与 g 的偏移不同，这里在 g 上改，最后重新 escape 整份？
# ❌ 危险！不能重 escape 整份。
# 所以：改用「唯一上下文替换」的方式。

FIXES_ARGS = [
    ('<span @class="_color">意识 _args[0]</span>',
     '<span @class="_color">意识 <<= _args[0]>></span>'),
    ('<span @class="_classList">露出癖 _args[0]</span>',
     '<span @class="_classList">露出癖 <<= _args[0]>></span>'),
    ('<span @class="_classList">淫乱 _args[0]</span>',
     '<span @class="_classList">淫乱 <<= _args[0]>></span>'),
    ('<span @class="_classList">异种癖_args[0]</span>',
     '<span @class="_classList">异种癖<<= _args[0]>></span>'),
    ('<<print ($enemytype is "man" ? "- 淫乱" : "- 异种癖")>> _args[0]</span>',
     '<<print ($enemytype is "man" ? "- 淫乱" : "- 异种癖")>> <<= _args[0]>></span>'),
    ('<<He>>握住你的_args[1]臂。',
     '<<He>>握住你的<<= _args[1]>>臂。'),
    ('食材"_args[0]"不包含在可烹饪配方中！请上报此问题！',
     '食材"<<= _args[0]>>"不包含在可烹饪配方中！请上报此问题！'),
    ('食物"_args[0]"缺少考核描述！',
     '食物"<<= _args[0]>>"缺少考核描述！'),
]

for old, new in FIXES_ARGS:
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

# ============================================================
# 2. 双重转义 &amp;lt; -> &lt;
# ============================================================
print("\n" + "=" * 90)
print("2. 修双重转义 &amp;lt; / &amp;gt;")
print("=" * 90)
n_lt = data.count("&amp;lt;")
n_gt = data.count("&amp;gt;")
print(f"  修前: &amp;lt; = {n_lt} 处, &amp;gt; = {n_gt} 处")
data = data.replace("&amp;lt;", "&lt;")
data = data.replace("&amp;gt;", "&gt;")
total += n_lt + n_gt
print(f"  已替换 {n_lt + n_gt} 处")

# 打标记
data = data.replace(
    H.escape('<<widget "generateshoppage">>', quote=False),
    H.escape('<!-- [X03] _args 泄漏 + 双重转义 -->' + '<<widget "generateshoppage">>', quote=False), 1)

open(HTML, "wb").write(data.encode("utf-8"))
print(f"\n共修 {total} 处")

# ============================================================
# 校验
# ============================================================
print("\n" + "=" * 90)
print("校验")
print("=" * 90)
g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
raw2 = open(HTML, "rb").read().decode("utf-8", "replace")

# 复扫正文 _args
left_args = 0
for m in re.finditer(r"_args\[(\d+)\]", g2):
    pre = g2[max(0, m.start() - 600):m.start()]
    if pre.rfind("<<") > pre.rfind(">>"):
        continue
    ctx = g2[max(0, m.start() - 40):m.start() + 50]
    if re.search(r"[\u4e00-\u9fff]", ctx):
        left_args += 1

n_lt2 = raw2.count("&amp;lt;")
n_gt2 = raw2.count("&amp;gt;")

print(f"  正文 _args 残留: {left_args}")
print(f"  &amp;lt; 残留: {n_lt2}")
print(f"  &amp;gt; 残留: {n_gt2}")
print(f"  passage: {len(re.findall(r'<tw-passagedata[^>]*name=', raw2))}")

ok = (left_args == 0 and n_lt2 == 0 and n_gt2 == 0)
print(f"\n  {'✅ 全部通过' if ok else '❌ 仍有残留'}")
sys.exit(0 if ok else 1)
