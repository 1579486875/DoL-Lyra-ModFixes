"""第 18 轮：HTML 标签配对 v2 —— 先剥离所有 <<宏>> 再检查。

剥离策略：反复用 <<...>> 非贪婪替换，直到不再减少（处理嵌套）。
"""
import html
import re
import sys
import zipfile
from collections import Counter

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"

VOID = {"br", "hr", "img", "input", "meta", "link", "source", "track",
        "wbr", "area", "base", "col", "embed", "param"}


def strip_macros(s):
    """剥离所有 <<...>>，反复直到稳定。"""
    prev = None
    for _ in range(6):
        if s == prev:
            break
        prev = s
        s = re.sub(r"<<[^<>]*(?:<[^<>]*>[^<>]*)*>>", " ", s)
    return s


def load_blocks(p):
    z = zipfile.ZipFile(p)
    raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    out = {}
    for m in re.finditer(r'<tw-passagedata([^>]*)>(.*?)</tw-passagedata>', raw, re.S):
        nm = re.search(r'name="([^"]+)"', m.group(1))
        if nm:
            out[html.unescape(nm.group(1))] = html.unescape(m.group(2))
    return out


def check(blocks, label, verbose=True):
    problems = Counter()
    details = []

    for pn, body in blocks.items():
        b = strip_macros(body)
        b = re.sub(r"<script\b.*?</script>", " ", b, flags=re.S | re.I)
        b = re.sub(r"<style\b.*?</style>", " ", b, flags=re.S | re.I)
        b = re.sub(r"<!--.*?-->", " ", b, flags=re.S)

        stack = []
        for m in re.finditer(r"<(/?)([a-zA-Z][a-zA-Z0-9]*)((?:[^>\"']|\"[^\"]*\"|'[^']*')*)>", b):
            closing, tag, attrs = m.group(1), m.group(2).lower(), m.group(3)
            if tag in VOID:
                continue
            if attrs.rstrip().endswith("/"):
                continue
            if closing:
                if stack and stack[-1][0] == tag:
                    stack.pop()
                else:
                    idx = -1
                    for i in range(len(stack) - 1, -1, -1):
                        if stack[i][0] == tag:
                            idx = i
                            break
                    if idx >= 0:
                        for _ in range(len(stack) - idx - 1):
                            t, pos = stack.pop()
                            problems[t] += 1
                            if len(details) < 12:
                                details.append((pn, f"未闭合 <{t}>", b[max(0, pos - 50):pos + 50]))
                        stack.pop()
                    else:
                        problems[f"多闭合:{tag}"] += 1
            else:
                stack.append((tag, m.start()))

        for tag, pos in stack:
            problems[tag] += 1
            if len(details) < 12:
                details.append((pn, f"未闭合 <{tag}>", b[max(0, pos - 50):pos + 50]))

    if verbose:
        print("=" * 90)
        print(f"{label}  ({len(blocks)} passage)")
        print("=" * 90)
        if problems:
            print(f"  ❌ {sum(problems.values())} 处，标签: {dict(problems.most_common(8))}")
            for pn, why, ctx in details[:8]:
                print(f"    [{pn}] {why}: {ctx!r}")
        else:
            print("  ✅ 全部配对")
    return problems, details


mb = load_blocks(APK)
vb = load_blocks(VAN)

mp, md = check(mb, "modded")
vp, vd = check(vb, "vanilla")

print("\n" + "=" * 90)
print("结论")
print("=" * 90)
m_only = {k: v for k, v in mp.items() if v > vp.get(k, 0)}
print(f"  modded 问题 {sum(mp.values())} 处 / vanilla {sum(vp.values())} 处")
print(f"  modded 独有标签: {m_only if m_only else '无'}")

if m_only:
    print("\n  modded 独有问题的具体位置:")
    shown = set()
    for pn, why, ctx in md:
        tag = why.replace("未闭合 <", "").replace(">", "").replace("多闭合:", "")
        if tag in m_only and tag not in shown:
            shown.add(tag)
            print(f"    [{pn}] {why}")
            print(f"      {ctx!r}")

sys.exit(1 if m_only else 0)
