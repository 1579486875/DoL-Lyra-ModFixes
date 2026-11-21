"""AU09（第13轮）：补译运行时仍为英文、官方汉化没有条目的玩家可见文本（幂等，passage 内限定替换）。

来源：AU01_runtime_english.py 对运行时导出（RT_GATE 的 _rt_gate_passages.jsonl）的扫描。
第12轮修好 BE2 烘焙后运行时残留从 182 段降到 20 段，其中 18 段是 $debug 选项或错误提示（原版调试文本，不动），
真正玩家可见的只剩下面 2 段（官方 i18n.json 里没有对应条目）。
"""
import html as H
import os
import re
import sys

HTML = os.environ.get("DOL_HTML") or r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")
if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[AU09] index 形态异常")
    sys.exit(1)
MARK = "[AU09]"
if MARK in H.unescape(data):
    print("[AU09] 已存在，跳过")
    sys.exit(0)

FIXES = [
    # 戴着恋人照片吊坠时的动作前缀；同一 if 的 else 分支官方译为「你抓紧时间，」
    ("Widgets Text", "\t\t\t\t\tYou hold your locket as\n", "\t\t\t\t\t你握紧吊坠盒，\n", 1),
    # 格威岚仪式的复选框
    ("Gwylan Ritual Sex Widgets", '<<checkbox "$sexRitual.resistOrgasm" false true autocheck>> Try to resist orgasm ',
     '<<checkbox "$sexRitual.resistOrgasm" false true autocheck>> 试着忍住高潮 ', 1),
]


def span(name):
    m = re.search(r'<tw-passagedata\s+[^>]*name="' + re.escape(name) + r'"[^>]*>', data)
    return (m.end(), data.find("</tw-passagedata>", m.end())) if m else None


miss = []
total = 0
for pname, old, new, want in FIXES:
    sp = span(pname)
    if not sp:
        miss.append((pname, "找不到 passage"))
        continue
    s, e = sp
    body = data[s:e]
    oe, ne = H.escape(old, quote=False), H.escape(new, quote=False)
    c = body.count(oe)
    if c != want:
        miss.append((pname, "命中 %d 应 %d" % (c, want)))
        continue
    data = data[:s] + body.replace(oe, ne) + data[e:]
    total += c

anchor = H.escape('<<widget "slithers">>', quote=False)
if anchor in data:
    data = data.replace(anchor, H.escape("<!-- [AU09] 补译运行时英文残留 -->", quote=False) + anchor, 1)
else:
    miss.append(("标记", "找不到 slithers"))
if miss:
    for x in miss:
        print("[AU09] MISS", x)
    print("[AU09] FAIL（未写盘）")
    sys.exit(1)
open(HTML, "wb").write(data.encode("utf-8"))
print("[AU09] 补译 %d 处  OK" % total)
