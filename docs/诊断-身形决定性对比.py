# -*- coding: utf-8 -*-
"""决定性对比：基础版（无美化）vs 我们的包 —— 身形立绘到底差在哪。"""
import hashlib
import os
import zipfile
from collections import Counter

BASE = r"E:\TAML\_dol\apk\对照-基础版-无美化.apk"
OURS = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"


def imgs(apk):
    z = zipfile.ZipFile(apk)
    m = {}
    for n in z.namelist():
        if not n.startswith("assets/www/img/"):
            continue
        if not n.lower().endswith((".png", ".jpg", ".gif", ".webp")):
            continue
        try:
            m[n] = hashlib.md5(z.read(n)).hexdigest()
        except Exception:
            pass
    return m


print("基础版:")
b = imgs(BASE)
print("  %d 张图" % len(b))
print("我们的包:")
o = imgs(OURS)
print("  %d 张图" % len(o))

only_b = set(b) - set(o)
only_o = set(o) - set(b)
common = set(b) & set(o)
diff = [k for k in common if b[k] != o[k]]

print("\n=== 汇总 ===")
print("基础版独有:", len(only_b))
print("我们独有:", len(only_o))
print("共有:", len(common))
print("内容不同（被替换）:", len(diff))


def bucket(p):
    s = p.replace("assets/www/img/", "")
    parts = s.split("/")
    if parts[0] == "body":
        return "body/" + (parts[1] if len(parts) > 1 else "(root)")
    if parts[0] == "clothes":
        return "clothes/" + (parts[1] if len(parts) > 1 else "")
    return parts[0]


print("\n=== 被替换的图（按目录）===")
for k, v in Counter(bucket(x) for x in diff).most_common(30):
    print("  %-36s %d" % (k, v))

print("\n=== 我们独有（按目录）===")
for k, v in Counter(bucket(x) for x in only_o).most_common(20):
    print("  %-36s %d" % (k, v))

print("\n=== 基础版独有（按目录）===")
for k, v in Counter(bucket(x) for x in only_b).most_common(20):
    print("  %-36s %d" % (k, v))

# 重点：身形相关
print("\n=== 身形相关图的对比（body/）===")
body_keys = sorted(k for k in (set(diff) | set(only_o) | set(only_b)) if "/img/body/" in k)
print("涉及 %d 个 body 文件" % len(body_keys))
for k in body_keys[:40]:
    tag = "替换" if k in diff else ("我们独有" if k in only_o else "基础版独有")
    print("  [%s] %s" % (tag, k.replace("assets/www/img/", "")))
