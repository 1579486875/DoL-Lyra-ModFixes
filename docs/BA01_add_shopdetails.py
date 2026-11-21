"""BA01（第14轮）：补全 setup.shopDetails 缺失的特质定义（Forest Shop 筛选器崩溃根因）。

现象：Forest Shop 的「Select Traits」筛选器报 reading 'desc'（loadFiltersMenu widget）。
根因：整合包新增衣物（dragonbreath / masquerade / sweet snowsuit）带 event / tanLines 特质，
      但 setup.shopDetails 没有这两项；另有 blindfold / shrinking / shackle 三项在 vanilla 与整合包都缺。
修法：在 shop.js 的 shopDetails 对象末尾 `};` 前插入 5 项（中文名 + 描述）。
"""
import html as H
import os
import re
import sys

HTML = os.environ.get("DOL_HTML") or r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")
if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[BA01] index 形态异常")
    sys.exit(1)

ADD = {
    "event": ("活动", "活动或节日专属服装。", "none"),
    "tanLines": ("晒痕", "穿着其它衣物晒出痕迹。", "none"),
    "blindfold": ("眼罩", "遮住双眼的装饰或限制装备。", "none"),
    "shrinking": ("缩水", "会因洗涤而缩水的衣物。", "none"),
    "shackle": ("镣铐", "限制行动的束缚装备。", "none"),
}
i = data.find("setup.shopDetails = {")
if i < 0:
    print("[BA01] FAIL 找不到 setup.shopDetails")
    sys.exit(1)
# 从 i 向后找到对象结束的 `};`（单独成行，前面只有制表符）
j = i
while True:
    j = data.find("};", j + 1)
    if j < 0:
        print("[BA01] FAIL 找不到 shopDetails 结束")
        sys.exit(1)
    # 检查这个 }; 前面是否是换行+制表符（说明是对象的顶层结束）
    k = j - 1
    while k >= i and data[k] in " \t":
        k -= 1
    if k >= i and data[k] == "\n":
        break
block = H.unescape(data[i:j + 2])
exist = set(re.findall(r'\b(\w+):\s*\{', block))
need = [k for k in ADD if k not in exist]
if not need:
    print("[BA01] 无需补充（已存在）")
    sys.exit(0)
lines = []
for k in need:
    nm, desc, det = ADD[k]
    lines.append('\t%s: {\n\t\tname: "%s",\n\t\tdesc: "%s",\n\t\tdetails: "%s",\n\t},' % (k, nm, desc, det))
inject = "\n" + "\n".join(lines) + "\n"
new_block = block.replace("};", inject + "};")
data = data[:i] + H.escape(new_block, quote=False) + data[j + 2:]
open(HTML, "wb").write(data.encode("utf-8"))
print("[BA01] 补充 %d 项: %s" % (len(need), need))
