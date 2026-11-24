# -*- coding: utf-8 -*-
"""让 corset 不再绘制胸部覆盖层，使胸完全由身体渲染（自然凸出）。

依据：
- corset 的 exposed: 1（本来就露胸）
- 问题不是「缺图」而是「图盖住了胸」
- breast_img 设为 0 → 不生成 upper_breasts 层
"""
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
OUT = r"E:\TAML\_dol\work\DoL-corset-v4.apk"

z = zipfile.ZipFile(APK)
h = z.read("assets/www/index.html").decode("utf-8", "replace")

i = h.find('variable: "corset"')
if i < 0:
    raise SystemExit("❌ 未找到 corset")
seg = h[i:i + 3000]
m = re.search(r"breast_img\s*:\s*(\{[^}]*\}|\d+)", seg)
if not m:
    raise SystemExit("❌ 未找到 breast_img")

old = m.group(0)
print("原:", old)

NEW = "breast_img: 0"
h2 = h[:i + m.start()] + NEW + h[i + m.end():]
print("新:", NEW)

# 只在 corset 段内校验（别处也有 breast_img: 0）
seg2 = h2[i:i + 3000]
assert "breast_img: 0" in seg2, "corset 段内未生效"
assert old not in seg2, "corset 段内旧值仍在"
# 全库计数只做记录
print("   全库 breast_img: 0 出现 %d 次（含其它衣服）" % h2.count("breast_img: 0"))
print("✅ 已改（不再绘制胸部覆盖层）")

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in z.infolist():
        d = h2.encode("utf-8") if info.filename == "assets/www/index.html" else z.read(info.filename)
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zo.writestr(zi, d)

print("\n✅ 输出:", OUT)
z2 = zipfile.ZipFile(OUT)
print("   条目:", len(z2.namelist()))
h3 = z2.read("assets/www/index.html").decode("utf-8", "replace")
print("   新值存在:", NEW in h3)
print("   旧值已消:", old not in h3)
