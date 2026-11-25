# -*- coding: utf-8 -*-
"""定位「反正正是自己家」这段家中裸体文案，找出为什么会在公园段落出现。"""
import html as H
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")

KEY = "反正正是自己家"
hits = list(re.finditer(KEY, h))
print("index 里命中 %d 处" % len(hits))
for mm in hits[:3]:
    print("\n@%d:" % mm.start())
    print(h[max(0, mm.start() - 700):mm.start() + 700].replace("\n", " ")[:1400])

# 也搜繁体/变体
for k2 in ("窗帘拉着", "不用提防任何人", "赤脚踩在地板上"):
    n = len(re.findall(re.escape(k2), h))
    print("\n%s: %d 处" % (k2, n))

# 在 passage 里定位
PS = {}
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', h, re.S):
    PS[m.group(1)] = H.unescape(m.group(2))

print("\n=== 含该文案的 passage ===")
for name, body in PS.items():
    if "反正正是自己家" in body or "窗帘拉着" in body or "不用提防任何人" in body:
        print("  【%s】%d 字符" % (name, len(body)))
        i = body.find("反正正是自己家")
        if i < 0:
            i = body.find("窗帘拉着")
        if i < 0:
            i = body.find("不用提防任何人")
        print("   上下文:", body[max(0, i - 500):i + 500].replace("\n", " ")[:1000])
