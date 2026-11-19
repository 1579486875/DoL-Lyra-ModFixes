"""抓出 i18n 破坏的 either() 参数（反引号缺失）+ Wraith 的字符串内嵌宏。"""
import html
import re

HTML = r"E:\TAML\_dol\work\index_modded6.html"
g = html.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))

print("=" * 94)
print("A) <<print either(...)>> 里缺反引号的参数")
print("=" * 94)
n = 0
for m in re.finditer(r"<<print\s+either\(", g):
    i = m.end()
    depth = 1
    while i < len(g) and depth > 0:
        if g[i] == "(":
            depth += 1
        elif g[i] == ")":
            depth -= 1
        i += 1
    body = g[m.end():i - 1]
    # 按顶层逗号切分
    parts, buf, depth2, in_str, q = [], "", 0, False, ""
    for ch in body:
        if in_str:
            buf += ch
            if ch == q:
                in_str = False
            continue
        if ch in "`'\"":
            in_str, q = True, ch
            buf += ch
            continue
        if ch in "([{":
            depth2 += 1
        elif ch in ")]}":
            depth2 -= 1
        if ch == "," and depth2 == 0:
            parts.append(buf.strip())
            buf = ""
            continue
        buf += ch
    if buf.strip():
        parts.append(buf.strip())

    bad = [p for p in parts if p and not p.startswith("`") and not p.startswith('"') and not p.startswith("'")]
    if bad:
        n += 1
        print(f"\n[{n}] @{m.start()}")
        print(f"    either(\n        " + "\n        ".join(repr(p[:110]) for p in parts) + "\n    )")
print(f"\n合计 {n} 处")

print("\n" + "=" * 94)
print("B) <<set>> 字符串里含 <<= 或 <<macro>>")
print("=" * 94)
m2 = 0
for mm in re.finditer(r"<<set\s+[\w$_.\[\]]+\s+to\s+(\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*')", g):
    s = mm.group(1)
    if "<<" in s:
        m2 += 1
        print(f"\n[{m2}] @{mm.start()}")
        print(f"    {mm.group(0)[:250]!r}")
print(f"\n合计 {m2} 处")
