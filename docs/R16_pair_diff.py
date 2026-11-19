"""第 16 轮：宏配对差值逐项对比 —— 只有 modded 独有的差异才是 bug。

同时标注哪些是「自闭合宏」（本来就不该有闭合）。
"""
import html
import re
import sys
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"

PAIRS = [
    ("if", "</if>", False),
    ("for", "</for>", False),
    ("switch", "</switch>", False),
    ("silently", "</silently>", False),
    ("capture", "</capture>", False),
    ("link", "</link>", False),
    ("button", "</button>", False),
    ("replace", "</replace>", False),
    ("append", "</append>", False),
    ("prepend", "</prepend>", False),
    ("widget", "</widget>", False),
    ("script", "</script>", False),
    ("stylesheet", "</stylesheet>", False),
    ("nobr", "</nobr>", False),
    ("done", "</done>", False),
    ("timed", "</timed>", False),
    ("textbox", "</textbox>", True),   # 自闭合
    ("listbox", "</listbox>", False),
    ("cycle", "</cycle>", False),
]


def load(p):
    z = zipfile.ZipFile(p)
    return html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))


def counts(g):
    out = {}
    for op, cl, selfclose in PAIRS:
        opens = len(re.findall(r"<<" + re.escape(op) + r"(?:>>|\s)", g))
        closes = g.count("<" + cl + ">")
        out[op] = (opens, closes, opens - closes, selfclose)
    return out


mg = load(APK)
vg = load(VAN)
mc = counts(mg)
vc = counts(vg)

print("=" * 100)
print(f"{'宏':<12} {'modded 开':>10} {'闭':>10} {'差':>6} | {'vanilla 开':>10} {'闭':>10} {'差':>6} | 判定")
print("=" * 100)

problems = []
for op, cl, selfclose in PAIRS:
    a, b, d, _ = mc[op]
    c, e, f, _ = vc[op]
    if selfclose:
        verdict = "自闭合，跳过"
        mark = "·"
    elif d == 0:
        verdict = "✅ 配对"
        mark = "✅"
    elif d == f:
        verdict = "⚪ 原版同样差（非我们引入）"
        mark = "⚪"
    else:
        verdict = f"❌ modded 独有差异（vanilla 差 {f}）"
        mark = "❌"
        problems.append((op, a, b, d, f))
    print(f"{mark} {op:<10} {a:>10} {b:>10} {d:>+6} | {c:>10} {e:>10} {f:>+6} | {verdict}")

print("\n" + "=" * 100)
print("结论")
print("=" * 100)
if problems:
    print(f"  ❌ modded 独有的配对差异 {len(problems)} 项:")
    for op, a, b, d, f in problems:
        print(f"     {op}: 开 {a} 闭 {b} 差 {d}  （vanilla 差 {f}）")
        # 显示未闭合的位置
        if op in ("widget", "script", "for", "replace", "timed"):
            opens = [m.start() for m in re.finditer(r"<<" + re.escape(op) + r"(?:>>|\s)", mg)]
            closes = [m.start() for m in re.finditer("<" + re.escape("</" + op + ">") + ">", mg)]
            print(f"       modded 开 {len(opens)} 闭 {len(closes)}")
            # 用栈找未闭合的
            stack = []
            for pos in sorted(opens + closes):
                if pos in opens:
                    stack.append(pos)
                elif stack:
                    stack.pop()
            if stack:
                print(f"       未闭合 {len(stack)} 个，最后 3 个位置: {stack[-3:]}")
                for p in stack[-3:]:
                    print(f"         @{p}: {mg[p:p+150]!r}")
else:
    print("  ✅ 无 modded 独有的配对差异")

sys.exit(1 if problems else 0)
