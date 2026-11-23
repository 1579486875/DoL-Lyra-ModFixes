# -*- coding: utf-8 -*-
"""全局扫兽人化相关词，检查术语一致性。"""
import html as H
import re

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

# 找所有 xxxperson / xxxpeople 对应的中文
pairs = {}
for m in re.finditer(r'<<(?:case|if|elseif)[^>]*"(\w*(?:person|people))"[^>]*>>[^<]{0,40}?_text_output to "([^"]*)"', g):
    pairs.setdefault(m.group(1), set()).add(m.group(2))

# 直接找 _text_output to 附近的英文
for mm in re.finditer(r'(\w*(?:person|people))', g):
    w = mm.group(1)
    if w not in ("person", "people", "person1", "persons"):
        seg = g[mm.start():mm.start() + 200]
        v = re.search(r'_text_output to "([^"]*)"', seg)
        if v:
            pairs.setdefault(w, set()).add(v.group(1))

print("=== person/people 词 → 译文 ===")
for k in sorted(pairs):
    print("  %-22s %s" % (k, sorted(pairs[k])))

# 检查「犬人 / 狗人」分布
print("\n=== 犬人 vs 狗人 ===")
for kw in ("犬人", "狗人", "猪人", "奶牛人", "牛人"):
    n = len(re.findall(re.escape(kw), g))
    print("  %-8s %d 处" % (kw, n))
