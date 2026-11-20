"""U09：查剩余 31 处的真实上下文。"""
import html as H
import re

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

PAT = re.compile(r"<<(if|elseif|else)\b[^>]*>>\s*\n\s*([A-Za-z][A-Za-z\- ']{1,40})\s*\n\s*<<", re.M)

seen = set()
for m in PAT.finditer(g):
    w = m.group(2).strip()
    if not w or re.search(r"[\u4e00-\u9fff]", w):
        continue
    if w.startswith("<<") or w.startswith("<") or re.search(r"[${}()\[\];=]", w):
        continue
    key = (w, m.start() // 1000)
    if key in seen:
        continue
    seen.add(key)
    print("=" * 95)
    print(f"[{w}]  @{m.start()}")
    print("=" * 95)
    print(repr(g[max(0, m.start() - 250):m.start() + 250]))
    print()
