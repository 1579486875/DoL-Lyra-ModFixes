# -*- coding: utf-8 -*-
"""对比第46轮（dead=5）与第53轮（dead=131）的 passage 内容差异。"""
import html as H
import re
import zipfile

GOOD = r"E:\TAML\_dol\archive\DoL-Lyra-0.5.12.13-CHS-modded_20261128_第46轮_洗澡返回与文案翻译修复.apk"
BAD = r"E:\TAML\_dol\archive\DoL-Lyra-0.5.12.13-CHS-modded_20261128_第53轮_逃脱尝试汉化.apk"


def passages(apk):
    z = zipfile.ZipFile(apk)
    raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    d = {}
    for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
        d[m.group(1)] = H.unescape(m.group(2))
    return d, len(raw)


g, glen = passages(GOOD)
b, blen = passages(BAD)
print("第46轮: %d passage, index %d 字符" % (len(g), glen))
print("第53轮: %d passage, index %d 字符" % (len(b), blen))

only_g = set(g) - set(b)
only_b = set(b) - set(g)
print("\n仅第46轮有: %d 个" % len(only_g))
for x in sorted(only_g)[:10]:
    print("   ", x)
print("\n仅第53轮有: %d 个" % len(only_b))
for x in sorted(only_b)[:10]:
    print("   ", x)

print("\n=== 两边都有但内容不同的 passage ===")
diff = []
for k in set(g) & set(b):
    if g[k] != b[k]:
        diff.append((k, len(g[k]), len(b[k])))
diff.sort(key=lambda x: -(abs(x[2] - x[1])))
print("共 %d 个不同" % len(diff))
for k, lg, lb in diff[:25]:
    print("   %-46s %d -> %d  (%+d)" % (k[:44], lg, lb, lb - lg))
