# -*- coding: utf-8 -*-
"""把所有声明文件里的个人署名统一为：大赢经直插白皮赢道（1579486875）"""
import os
import re

SIGN = "大赢经直插白皮赢道（1579486875）"

FILES = [
    r"E:\TAML\_dol\repos\DoL-Lyra-ModFixes\声明与许可.md",
    r"E:\TAML\_dol\work\联动模组\系统联动补全\LICENSE.md",
    r"E:\TAML\_dol\work\_mods\44_美化修正\LICENSE.md",
    r"E:\TAML\_dol\work\加-整合包声明.py",     # NOTICE.md 的模板在这里
]

for p in FILES:
    if not os.path.exists(p):
        print("⚠ 不存在:", p)
        continue
    t = open(p, encoding="utf-8").read()
    orig = t

    # 1) 把裸的 1579486875（后面不跟括号内容）替换为完整署名
    #    先处理 "1579486875" 独立出现的情况
    t = re.sub(r"(?<![（\w])1579486875(?![）\w])", SIGN, t)

    # 2) 已经写成 "大赢经直插白皮赢道（1579486875）" 的不再重复
    t = t.replace(SIGN + "（1579486875）", SIGN)

    if t != orig:
        open(p, "w", encoding="utf-8").write(t)
        n = t.count(SIGN)
        print("✅ %s → 署名出现 %d 次" % (os.path.basename(p), n))
    else:
        print("—  %s 无变化" % os.path.basename(p))

print("\n=== 校验 ===")
for p in FILES:
    if not os.path.exists(p):
        continue
    t = open(p, encoding="utf-8").read()
    hits = [m.start() for m in re.finditer(re.escape(SIGN), t)]
    bare = re.findall(r"(?<![（\w])1579486875(?![）\w])", t)
    print("%-30s 完整署名 %d 处 | 裸号残留 %d 处" % (
        os.path.basename(p), len(hits), len(bare)))
