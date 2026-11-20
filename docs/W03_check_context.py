"""W03：查 3 个真问题的完整上下文。"""
import html as H
import re

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

TARGETS = [
    ("setup.colourName(.colour)", r"setup\.colourName\(\.colour\)"),
    ("body size 那段", r"body part sizes"),
    ("goal bug 提示", r"这是个发生在goal"),
    ("pose 口语", r"开始摆起了pose"),
]

for label, pat in TARGETS:
    print("=" * 95)
    print(f"[{label}]")
    print("=" * 95)
    for m in re.finditer(pat, g):
        print(f"  @{m.start()}")
        print(f"  {g[max(0, m.start() - 400):m.start() + 500]!r}")
    print()

# 顺便查「代码泄漏到正文」的同类模式：正文里出现 setup.xxx( 但没被 <<print>> 包
print("=" * 95)
print("同类：正文里裸露的 setup.xxx(...)")
print("=" * 95)
n = 0
for m in re.finditer(r"(?<![<>=\w])setup\.([A-Za-z_][A-Za-z0-9_]*)\(", g):
    pre = g[max(0, m.start() - 40):m.start()]
    # 排除在 << >> 里的
    if pre.rfind("<<") > pre.rfind(">>"):
        continue
    # 排除 JS 上下文
    if pre and pre[-1] in ".=({[,;:+*/<>!&|?~^%$":
        continue
    # 必须有中文前后（说明在正文里）
    ctx = g[max(0, m.start() - 30):m.start() + 60]
    if not re.search(r"[\u4e00-\u9fff]", ctx):
        continue
    n += 1
    if n <= 15:
        print(f"  @{m.start()}: {ctx!r}")
print(f"  共 {n} 处")
