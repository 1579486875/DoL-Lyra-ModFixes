"""修正 SF01：把插入锚点从 bodyShapes（在 widget 内部）改为 variablesStatic 的闭合标签之后。

问题：bodyShapes 位于 <<widget "variablesStatic">> 内部，
      在它后面插 <<widget "wTimerProgress">> 会导致 widget 嵌套 → SugarCube 解析崩溃。
"""
import os
import re
import sys

PATH = r"E:\TAML\_dol\work\SF01_missing_symbols.py"
s = open(PATH, encoding="utf-8").read()

OLD_MAIN = '''    e_anchor = H.escape(ANCHOR, quote=False)
    e_defs = H.escape(DEFS, quote=False)

    if e_anchor in data:
        data = data.replace(e_anchor, e_anchor + e_defs, 1)
        print("✅ 已插入（转义形态）")
    elif ANCHOR in data:
        data = data.replace(ANCHOR, ANCHOR + DEFS, 1)
        print("✅ 已插入（未转义）")
    else:
        print("❌ 未找到锚点")
        return 1'''

NEW_MAIN = '''    e_defs = H.escape(DEFS, quote=False)

    # 新锚点：variablesStatic widget 的闭合标签（passage 级别，不在任何 widget 内）
    VS_OPEN = '&lt;&lt;widget "variablesStatic"&gt;&gt;'
    VS_CLOSE = '&lt;&lt;/widget&gt;&gt;'
    i = data.find(VS_OPEN)
    if i < 0:
        print("❌ 找不到 variablesStatic")
        return 1
    j = data.find(VS_CLOSE, i)
    if j < 0:
        print("❌ 找不到 variablesStatic 的闭合")
        return 1
    j += len(VS_CLOSE)
    data = data[:j] + "\\n" + e_defs + data[j:]
    print("✅ 已插到 variablesStatic 之后（passage 级别，不会造成 widget 嵌套）")'''

if OLD_MAIN not in s:
    print("❌ 未找到旧的插入逻辑")
    sys.exit(1)

s = s.replace(OLD_MAIN, NEW_MAIN, 1)

# 同时更新文件头注释
s = s.replace(
    '插入位置：Widgets variablesStatic 的 bodyShapes 之后（那里一定最早执行）。',
    '插入位置：variablesStatic widget 的闭合标签之后（passage 级别）。\n绝不能插在 bodyShapes 后面 —— 那在 widget 内部，会造成 widget 嵌套。'
)

open(PATH, "w", encoding="utf-8").write(s)
print("✅ SF01 已修正")
print("\n新插入位置：variablesStatic 闭合之后（passage 级别）")
