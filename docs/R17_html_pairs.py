"""第 17 轮：HTML 标签配对（只查 passage 内容区，排除 script/style）。

自闭合：br hr img input meta link source track wbr area base col embed param
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


def load_blocks(p):
    z = zipfile.ZipFile(p)
    raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    out = {}
    for m in re.finditer(r'<tw-passagedata([^>]*)>(.*?)</tw-passagedata>', raw, re.S):
        nm = re.search(r'name="([^"]+)"', m.group(1))
        if nm:
            out[html.unescape(nm.group(1))] = html.unescape(m.group(2))
    return out


def check(blocks, label):
    print("=" * 90)
    print(f"{label}  ({len(blocks)} passage)")
    print("=" * 90)
    problems = Counter()
    details = []

    for pn, body in blocks.items():
        # 排除 script / style 块
        b = re.sub(r"<script\b.*?</script>", " ", body, flags=re.S | re.I)
        b = re.sub(r"<style\b.*?</style>", " ", b, flags=re.S | re.I)
        b = re.sub(r"<!--.*?-->", " ", b, flags=re.S)

        stack = []
        for m in re.finditer(r"<(/?)([a-zA-Z][a-zA-Z0-9]*)([^>]*)>", b):
            closing, tag, attrs = m.group(1), m.group(2).lower(), m.group(3)
            if tag in VOID:
                continue
            selfclose = attrs.rstrip().endswith("/")
            if selfclose:
                continue
            if closing:
                if stack and stack[-1][0] == tag:
                    stack.pop()
                else:
                    # 找最近匹配
                    idx = -1
                    for i in range(len(stack) - 1, -1, -1):
                        if stack[i][0] == tag:
                            idx = i
                            break
                    if idx >= 0:
                        # 中间有未闭合
                        for _ in range(len(stack) - idx - 1):
                            t, pos = stack.pop()
                            problems[t] += 1
                            if len(details) < 15:
                                details.append((pn, f"未闭合 <{t}>", b[max(0, pos - 60):pos + 60]))
                        stack.pop()
                    else:
                        problems[f"多闭合:{tag}"] += 1
                        if len(details) < 15:
                            details.append((pn, f"多闭合 </{tag}>", b[max(0, m.start() - 60):m.start() + 60]))
            else:
                stack.append((tag, m.start()))

        for tag, pos in stack:
            problems[tag] += 1
            if len(details) < 15:
                details.append((pn, f"未闭合 <{tag}>", b[max(0, pos - 60):pos + 60]))

    if problems:
        print(f"  ❌ 问题 {sum(problems.values())} 处，涉及标签: {dict(problems.most_common(10))}")
        for pn, why, ctx in details[:10]:
            print(f"    [{pn}] {why}")
            print(f"      {ctx!r}")
    else:
        print("  ✅ 全部配对")
    return problems, details


mb = load_blocks(APK)
vb = load_blocks(VAN)

mp, md = check(mb, "modded")
vp, vd = check(vb, "vanilla")

print("\n" + "=" * 90)
print("结论（只看 modded 独有）")
print("=" * 90)
m_only = {k: v for k, v in mp.items() if v > vp.get(k, 0)}
print(f"  modded 问题: {sum(mp.values())}   vanilla 问题: {sum(vp.values())}")
print(f"  modded 独有标签: {m_only if m_only else '无'}")

# 只看 modded 独有 passage 里的问题
m_only_passages = set(mb) - set(vb)
print(f"  modded 独有 passage: {len(m_only_passages)} 个")
if m_only_passages:
    sub = {k: mb[k] for k in m_only_passages}
    sp, sd = check(sub, "modded 独有 passage")
    for pn, why, ctx in sd[:5]:
        print(f"    [{pn}] {why}: {ctx!r}")

sys.exit(1 if m_only else 0)
