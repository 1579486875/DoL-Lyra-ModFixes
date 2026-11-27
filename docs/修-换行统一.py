# -*- coding: utf-8 -*-
r"""修 index 换行：把 CRLF 改回 LF，恢复 TweeReplacer 锚点匹配。

根因：第52/53轮的几个脚本用 open(path, "w", encoding="utf-8") 写入，
      Windows 上 Python 自动把 \n 转成 \r\n，
      而模组 patch 的 findString 里是 \n -> 锚点失配 -> 126 条 patch 失效。

修法：
  1. 把 work\index_modded6.html 的 CRLF 全部改回 LF（只改 passage 内的，不改文件整体）
  2. 修所有「写 index」的脚本，加 newline="\n"
"""
import glob
import os
import re

HTML = r"E:\TAML\_dol\work\index_modded6.html"

raw_bytes = open(HTML, "rb").read()
text = raw_bytes.decode("utf-8", "replace")
n_crlf = text.count("\r\n")
n_lf = text.count("\n")
n_cr = text.count("\r")

print("=== 修前 ===")
print("  \\r\\n: %d" % n_crlf)
print("  \\n   : %d" % n_lf)
print("  \\r   : %d" % n_cr)
print("  字节 : %d" % len(raw_bytes))

if n_crlf == 0 and n_cr == 0:
    print("\n✅ 已经是纯 LF，无需修改")
else:
    text2 = text.replace("\r\n", "\n").replace("\r", "\n")
    open(HTML, "wb").write(text2.encode("utf-8"))
    print("\n=== 修后 ===")
    print("  \\r\\n: %d" % text2.count("\r\n"))
    print("  \\n   : %d" % text2.count("\n"))
    print("  \\r   : %d" % text2.count("\r"))
    print("  字节 : %d -> %d  (%+d)" % (len(raw_bytes), len(text2.encode("utf-8")),
                                        len(text2.encode("utf-8")) - len(raw_bytes)))

# ============ 修所有写 index 的脚本 ============
print("\n=== 修脚本的 open(...) 写入方式 ===")
TARGET_SCRIPTS = [
    "修-descCN拼接2.py",
    "修-EscapeAttempt.py",
    "修-拖动-落到work.py",
    "修-descCN拼接.py",
    "重打包-以最新为底.py",
    "打包-联动模组2.py",
]
fixed = 0
for fn in TARGET_SCRIPTS:
    p = os.path.join(r"E:\TAML\_dol\work", fn)
    if not os.path.isfile(p):
        continue
    s = open(p, encoding="utf-8", errors="replace").read()
    orig = s
    # 把 open(X, "w", encoding="utf-8") 改成加 newline="\n"
    s = re.sub(
        r'open\(([^,()]+),\s*"w"\s*,\s*encoding\s*=\s*"utf-8"\s*\)',
        r'open(\1, "w", encoding="utf-8", newline="\\n")',
        s,
    )
    if s != orig:
        open(p, "w", encoding="utf-8", newline="\n").write(s)
        print("  ✅ %s" % fn)
        fixed += 1
    else:
        # 检查是否已经是 wb
        if '"wb"' in s:
            print("  OK %s（已用 wb）" % fn)
        else:
            print("  -- %s（无匹配）" % fn)

print("\n共修 %d 个脚本" % fixed)
