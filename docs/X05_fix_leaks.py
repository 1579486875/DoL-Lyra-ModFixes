"""X05：修 _args 泄漏 + 双重转义（幂等）。"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[X05] index 形态异常")
    sys.exit(1)

MARK = "[X05]"
g0 = H.unescape(data)
# 兼容已打过的 X03/X04 标记
if MARK in g0:
    print("[X05] 已存在，跳过  passage=%d" % len(re.findall(r'<tw-passagedata[^>]*name=', data)))
    sys.exit(0)

total = 0

# ===== 1. _args[N] 泄漏 =====
FIXES = [
    # --- 第一批 ---
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
    # --- 第二批 ---
    ('<<if $drugged gte 1>>药物抑制了你的声音，你的哭泣软弱无力。<</if>>\n\t\t<<else>>\n\t\t\t_args[0]\n\t\t<</if>>',
     '<<if $drugged gte 1>>药物抑制了你的声音，你的哭泣软弱无力。<</if>>\n\t\t<<else>>\n\t\t\t<<= _args[0]>>\n\t\t<</if>>'),
    ('<span class="green">+ _args[0]%通过率</span>',
     '<span class="green">+ <<= _args[0]>>%通过率</span>'),
    ('<<print _icon>><</if>> _args[0]不足.</span>',
     '<<print _icon>><</if>> <<= _args[0]>>不足.</span>'),
    ('<span class="red">错误：无效动作_args[0]: $shopHunt.actors[_args[0]].state。请报告这个问题！</span>',
     '<span class="red">错误：无效动作<<= _args[0]>>: <<= $shopHunt.actors[_args[0]].state>>。请报告这个问题！</span>'),
    ('<<default>>_args[0].name',
     '<<default>><<= _args[0].name>>'),
    ('<span class="red">选项无效：_args[0]</span>',
     '<span class="red">选项无效：<<= _args[0]>></span>'),
]

for old, new in FIXES:
    for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
        if a in data:
            c = data.count(a)
            data = data.replace(a, b)
            total += c
            break

# ===== 2. 双重转义 =====
n_lt = data.count("&amp;lt;")
n_gt = data.count("&amp;gt;")
data = data.replace("&amp;lt;", "&lt;")
data = data.replace("&amp;gt;", "&gt;")
total += n_lt + n_gt

data = data.replace(
    H.escape('<<widget "generateshoppage">>', quote=False),
    H.escape('<!-- [X05] _args 泄漏 + 双重转义 -->' + '<<widget "generateshoppage">>', quote=False), 1)

open(HTML, "wb").write(data.encode("utf-8"))

# ===== 校验 =====
raw2 = open(HTML, "rb").read().decode("utf-8", "replace")
g = H.unescape(raw2)

# 正文 _args（排除属性/注释/宏内）
left = 0
for m in re.finditer(r"_args\[(\d+)\]", g):
    pos = m.start()
    pre = g[max(0, pos - 600):pos]
    if pre.rfind("<<") > pre.rfind(">>"):
        continue
    if g.rfind("<!--", 0, pos) > g.rfind("-->", 0, pos):
        continue
    if g.rfind("/*", 0, pos) > g.rfind("*/", 0, pos):
        continue
    ctx = g[max(0, pos - 40):pos + 50]
    if not re.search(r"[\u4e00-\u9fff]", ctx):
        continue
    lt = pre.rfind("<")
    gt = pre.rfind(">")
    if lt > gt:
        seg = pre[lt:]
        if '"' in seg or "'" in seg:
            continue
    # 排除在 <<set ... >> 里（内含 "<<" 字符串会让判据失效）
    if re.search(r"<<set\s+[^\n]{0,400}$", pre):
        continue
    left += 1

n_lt2 = raw2.count("&amp;lt;")
n_gt2 = raw2.count("&amp;gt;")

ok = (left == 0 and n_lt2 == 0 and n_gt2 == 0)
print("[X05] 修 %d 处  正文_args=%d  amp_lt=%d  amp_gt=%d  passage=%d  %s" % (
    total, left, n_lt2, n_gt2,
    len(re.findall(r'<tw-passagedata[^>]*name=', raw2)),
    "OK" if ok else "FAIL"))
if left:
    print("   剩余:", left)
sys.exit(0 if ok else 1)
