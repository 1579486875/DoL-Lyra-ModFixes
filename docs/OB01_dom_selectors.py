"""第 7-12 轮：DOM 选择器验证。

 7) <<replace>> / <<append>> / <<prepend>> / <<remove>> 的 CSS 选择器
 8) index 里的 id/class 与 CSS 文件里的选择器
 9) jQuery $('#xxx') 引用的 id 是否存在
10) <<link>> 的 setter 里引用的 id
11) CSS 里定义了但 HTML 从未使用的 class（可能是翻译丢失）
12) 重复 id
"""
import html
import re
from collections import Counter, defaultdict

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")
g = html.unescape(raw)

print("=" * 94)
print("第 7 轮：<<replace>> / <<append>> 等选择器")
print("=" * 94)


def extract(text, pat):
    out = []
    for m in re.finditer(pat, text):
        i = m.end()
        depth = 1
        while i < len(text) and depth > 0:
            if text.startswith("<<", i):
                depth += 1
                i += 2
            elif text.startswith(">>", i):
                depth -= 1
                i += 2
            else:
                i += 1
        out.append(text[m.end():i - 2].strip())
    return out


sels = Counter()
for tag in ("replace", "append", "prepend", "remove"):
    for s in extract(g, r"<<" + tag + r"\b"):
        # 只取选择器部分（第一个参数）
        sel = s.split(">>")[0].strip()
        if sel:
            sels[sel] += 1

print(f"  选择器种类 {len(sels)}，总调用 {sum(sels.values())}")
# 找以 # 或 . 开头的选择器，检查目标是否存在
ids_defined = set(re.findall(r'\bid="([^"]+)"', g))
classes_defined = set()
for c in re.findall(r'\bclass="([^"]+)"', g):
    for x in c.split():
        classes_defined.add(x)

missing = []
for sel, c in sels.most_common():
    # 简单判断：单个 #id 或 .class
    m = re.fullmatch(r"#([\w\-]+)", sel)
    if m and m.group(1) not in ids_defined:
        missing.append((sel, c))
        continue
    m = re.fullmatch(r"\.([\w\-]+)", sel)
    if m and m.group(1) not in classes_defined:
        missing.append((sel, c))

print(f"  静态找不到目标的: {len(missing)}")
for sel, c in missing[:20]:
    print(f"    {c:>4}  {sel!r}")

print("\n" + "=" * 94)
print("第 8 轮：jQuery $('#id') 引用的 id")
print("=" * 94)
jq = Counter(re.findall(r"""\$\(\s*['"]#([\w\-]+)['"]\s*\)""", g))
print(f"  引用的 id: {len(jq)} 种")
miss_jq = [(i, c) for i, c in jq.items() if i not in ids_defined]
print(f"  id 未定义: {len(miss_jq)}")
for i, c in sorted(miss_jq, key=lambda x: -x[1])[:20]:
    print(f"    {c:>4}  #{i}")

print("\n" + "=" * 94)
print("第 9 轮：重复 id")
print("=" * 94)
all_ids = re.findall(r'\bid="([^"]+)"', g)
dup = {k: v for k, v in Counter(all_ids).items() if v > 1}
print(f"  重复 id: {len(dup)}")
for k, v in sorted(dup.items(), key=lambda x: -x[1])[:15]:
    print(f"    {v:>3}  #{k}")

print("\n" + "=" * 94)
print("第 10 轮：CSS 里定义但 HTML 从未使用的 class（抽样）")
print("=" * 94)
css_classes = set()
for m in re.finditer(r"<style[^>]*>(.*?)</style>", g, re.S):
    css = m.group(1)
    css_classes |= set(re.findall(r"\.([A-Za-z][\w\-]{1,40})\s*[,{:]", css))
html_classes = set()
for c in re.findall(r'\bclass="([^"]+)"', g):
    for x in c.split():
        html_classes.add(x)
# 也把 JS 里 addClass / classList 的算上
html_classes |= set(re.findall(r"""addClass\(\s*['"]([\w\-]+)['"]""", g))
html_classes |= set(re.findall(r"""classList\.(?:add|remove|toggle)\(\s*['"]([\w\-]+)['"]""", g))
html_classes |= set(re.findall(r"""@class="[^"]*?['"]([\w\-]+)['"]""", g))

unused = css_classes - html_classes
print(f"  CSS class {len(css_classes)}，HTML 用到的 {len(html_classes)}")
print(f"  CSS 有但未用: {len(unused)}（多为动态拼接，参考价值有限）")
for u in sorted(unused)[:15]:
    print(f"    .{u}")

print("\n" + "=" * 94)
print("第 11-12 轮：选择器里的转义与特殊字符")
print("=" * 94)
weird = [s for s in sels if re.search(r"[^\w\-#.\s\[\]()>+~*:=,'\"]", s)]
print(f"  含特殊字符的选择器: {len(weird)}")
for s in weird[:10]:
    print(f"    {s!r}")
