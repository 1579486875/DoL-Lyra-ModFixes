# -*- coding: utf-8 -*-
"""看第46轮 vs 第53轮同一个 passage 的具体差异（前 800 字符对比）。"""
import html as H
import re
import zipfile

GOOD = r"E:\TAML\_dol\archive\DoL-Lyra-0.5.12.13-CHS-modded_20261128_第46轮_洗澡返回与文案翻译修复.apk"
BAD = r"E:\TAML\_dol\archive\DoL-Lyra-0.5.12.13-CHS-modded_20261128_第53轮_逃脱尝试汉化.apk"


def get_raw(apk, name):
    z = zipfile.ZipFile(apk)
    raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    m = re.search(r'<tw-passagedata[^>]*name="' + re.escape(name) + r'"[^>]*>(.*?)</tw-passagedata>', raw, re.S)
    return m.group(1) if m else None


NAME = "Widgets variablesStatic"
g = get_raw(GOOD, NAME)
b = get_raw(BAD, NAME)
print("=== 原始（未反转义）对比 ===")
print("第46轮长度: %d" % len(g))
print("第53轮长度: %d" % len(b))
print("\n第46轮前 500 字符（repr）:")
print(repr(g[:500]))
print("\n第53轮前 500 字符（repr）:")
print(repr(b[:500]))

print("\n\n=== 转义字符统计 ===")
for label, s in (("第46轮", g), ("第53轮", b)):
    print("%s:" % label)
    print("   &lt; : %d" % s.count("&lt;"))
    print("   &gt; : %d" % s.count("&gt;"))
    print("   &amp;: %d" % s.count("&amp;"))
    print("   &quot;: %d" % s.count("&quot;"))
    print("   裸 < : %d" % s.count("<"))
    print("   裸 > : %d" % s.count(">"))
    print("   裸 & : %d" % s.count("&"))
    print("   \\r\\n : %d" % s.count("\r\n"))
    print("   \\n   : %d" % s.count("\n"))
