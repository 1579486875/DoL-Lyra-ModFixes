# -*- coding: utf-8 -*-
"""AUDIT1：当前 index vs 修复前备份，逐 passage diff + 明文 script 块 hash 对比。"""
import hashlib
import html as H
import re
import sys

A = r"E:\TAML\_dol\work\index_modded6.html.bak_r7fix"   # 修复前
B = r"E:\TAML\_dol\work\index_modded6.html"             # 修复后


def passages(path):
    raw = open(path, "rb").read().decode("utf-8", "replace")
    out = {}
    for m in re.finditer(r'<tw-passagedata([^>]*)>(.*?)</tw-passagedata>', raw, re.S):
        attrs, body = m.group(1), m.group(2)
        nm = re.search(r'name="([^"]*)"', attrs)
        if nm:
            out[nm.group(1)] = body
    return raw, out


def scripts(raw):
    out = {}
    for m in re.finditer(r'<script\b([^>]*)>(.*?)</script>', raw, re.S):
        key = re.sub(r'\s+', " ", m.group(1)).strip()[:60]
        out[key] = hashlib.md5(m.group(2).encode("utf-8", "replace")).hexdigest()[:10]
    return out


ra, pa = passages(A)
rb, pb = passages(B)
print("passage: %d -> %d" % (len(pa), len(pb)))

only_a = set(pa) - set(pb)
only_b = set(pb) - set(pa)
print("删除的 passage:", sorted(only_a)[:10])
print("新增的 passage:", sorted(only_b)[:10])

changed = []
for k in pa:
    if k in pb and pa[k] != pb[k]:
        changed.append(k)
print("\n内容变化的 passage: %d" % len(changed))
for k in changed:
    a, b = pa[k], pb[k]
    # 找第一处差异
    i = 0
    n = min(len(a), len(b))
    while i < n and a[i] == b[i]:
        i += 1
    print("\n--- [%s]  len %d -> %d" % (k, len(a), len(b)))
    print("    A:", a[max(0, i - 80):i + 160].replace("\n", "\\n")[:240])
    print("    B:", b[max(0, i - 80):i + 160].replace("\n", "\\n")[:240])

sa, sb = scripts(ra), scripts(rb)
print("\n=== 明文 script 块 ===")
for k in sa:
    flag = "SAME" if sa[k] == sb.get(k) else "DIFF"
    print("  %-50s %s (%s -> %s)" % (k, flag, sa[k], sb.get(k)))
