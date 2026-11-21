"""BA02（第14轮）：loadFiltersMenu widget 加防护 —— shopDetails[trait] 缺失时不崩溃（Forest Shop 筛选器，第二道防线）。

BA01 补全了当前缺失的 5 个特质定义；BA02 是防护，避免未来新模组引入新特质时再崩溃。
修法：`<<if !_traitObj.desc>>` 改为 `<<if !_traitObj or !_traitObj.desc>>`，缺定义时只显示特质英文名。
"""
import html as H
import os
import re
import sys

HTML = os.environ.get("DOL_HTML") or r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")
if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[BA02] index 形态异常")
    sys.exit(1)

OLD = '<<if !_traitObj.desc>>'
NEW = '<<if !_traitObj or !_traitObj.desc>>'
# 转义形态查找
i = data.find('&lt;&lt;widget "loadFiltersMenu"&gt;&gt;')
if i < 0:
    print("[BA02] FAIL 找不到 loadFiltersMenu widget")
    sys.exit(1)
j = data.find('&lt;&lt;/widget&gt;&gt;', i)
if j < 0:
    print("[BA02] FAIL 找不到 widget 结束")
    sys.exit(1)
block = H.unescape(data[i:j + 24])
if OLD not in block:
    if NEW in block:
        print("[BA02] 无需修改（已存在防护）")
        sys.exit(0)
    print("[BA02] FAIL 找不到锚点")
    sys.exit(1)
new_block = block.replace(OLD, NEW)
data = data[:i] + H.escape(new_block, quote=False) + data[j + 24:]
open(HTML, "wb").write(data.encode("utf-8"))
print("[BA02] 已加防护：_traitObj 空值检查")
