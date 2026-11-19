"""按 passage 精确定位修复（解决"两个 passage 锚点相同"的 case）。"""
import html as H
import re
import sys
import os

HTML = r"E:\TAML\_dol\work\index_modded6.html"

# (passage 名, 需要补闭合的文本)
TARGETS = [
    ("Asylum Depths Tunnels 4 Return", '<<link [[离开|Asylum Depths Tunnel 4 Leave]]>>'),
]

data = open(HTML, "rb").read().decode("utf-8", "replace")

PAT = re.compile(r'(<tw-passagedata[^>]*name="([^"]+)"[^>]*>)(.*?)(</tw-passagedata>)', re.S)

def patch_block(m):
    open_tag, pname, body_esc, close_tag = m.group(1), m.group(2), m.group(3), m.group(4)
    for target_ps, bad in TARGETS:
        if pname != target_ps:
            continue
        body = H.unescape(body_esc)
        e_bad = H.escape(bad, quote=False)
        # 只补未闭合的
        if re.search(re.escape(bad) + r"(?!<)", body):
            body = re.sub(re.escape(bad) + r"(?!<)", H.escape(bad + "<</link>>", quote=False), body, count=1)
            print(f"  ✅ [{pname}]")
            return open_tag + H.escape(body, quote=False) + close_tag
        elif re.search(re.escape(e_bad) + r"(?!&lt;)", body_esc):
            body_esc = re.sub(re.escape(e_bad) + r"(?!&lt;)",
                              H.escape(bad + "<</link>>", quote=False), body_esc, count=1)
            print(f"  ✅ [{pname}]（转义形态）")
            return open_tag + body_esc + close_tag
        else:
            print(f"  ❌ [{pname}] 未找到待闭合锚点")
    return m.group(0)

new = PAT.sub(patch_block, data)
open(HTML, "wb").write(new.encode("utf-8"))
print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")
