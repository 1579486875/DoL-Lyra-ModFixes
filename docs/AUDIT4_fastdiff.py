# -*- coding: utf-8 -*-
"""AUDIT4：twine-user-script 的逐行差异（快速）。"""
import html as H
import re

A = r"E:\TAML\_dol\work\index_modded6.html.bak_r7fix"
B = r"E:\TAML\_dol\work\index_modded6.html"


def get_script(path):
    raw = open(path, "rb").read().decode("utf-8", "replace")
    m = re.search(r'<script\b[^>]*id="twine-user-script"[^>]*>(.*?)</script>', raw, re.S)
    return m.group(1) if m else ""


a = get_script(A).split("\n")
b = get_script(B).split("\n")
print("lines: %d -> %d" % (len(a), len(b)))

# 行数相同则逐行比对；不同则用 difflib 行级
diff = []
if len(a) == len(b):
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            diff.append((i + 1, x, y))
else:
    import difflib
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        diff.append(("%d-%d -> %d-%d" % (i1 + 1, i2, j1 + 1, j2), "\n".join(a[i1:i2]), "\n".join(b[j1:j2])))

print("差异行/块:", len(diff))
for d in diff[:20]:
    print("\n  L%s" % (d[0],))
    print("    A:", repr(d[1][:200]))
    print("    B:", repr(d[2][:200]))
