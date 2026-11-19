"""修复 BE_bake_i18n 的 _is_code_like：去掉「纯标识符一律跳过」。

问题：单英文单词的 UI 文本（Monstergirl / Beast / Testing / Orphanage...）
被当成代码跳过，导致这些翻译缺失。

widget 名的保护不需要这条规则 —— `<<widget "characteristics">>` 的 f 里
含 `<<widget`，第一条规则已经挡住。
"""
import os
import re
import sys

PATH = r"E:\TAML\_dol\work\BE_bake_i18n.py"
s = open(PATH, encoding="utf-8").read()

OLD = '''def _is_code_like(text):
    """只挡真正会改坏代码的条目。

    不挡的情况（这些必须翻译）：
      - 含 <<set / <<link / <<if 等正常宏
      - 含 => 的箭头函数（如 _parasiteTypes.map(type => ...)）
      - 普通单词（eels / pain / affection）

    挡的情况：
      - 出现 widget / macro 定义关键字（名字不能变）
      - 整条 f 是纯标识符（^[A-Za-z_][A-Za-z0-9_]*$）且不超过 40 字符
        —— 这一定是变量名或 widget 名，翻了就坏
    """
    if not text:
        return False
    # 1) 宏/widget 定义关键字
    for kw in ("<<widget", "<<macro", "Macro.add"):
        if kw in text:
            return True
    # 2) f 整体是纯标识符（无空格、无标点）
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", text) and len(text) <= 40:
        return True
    return False'''

NEW = '''def _is_code_like(text):
    """只挡真正会改坏代码的条目。

    挡的情况（只有这一类）：
      - 出现 <<widget / <<macro / Macro.add —— 宏名和 widget 名不能变
        （`<<widget "characteristics">>` 的 f 会含 `<<widget`，已被这条挡住，
          所以不需要再单独判断「纯标识符」）

    曾经错误地加过「纯标识符一律跳过」，导致 Monstergirl / Beast / Testing /
    Orphanage 这类单英文单词的 UI 文本全部漏翻。已移除。
    """
    if not text:
        return False
    for kw in ("<<widget", "<<macro", "Macro.add"):
        if kw in text:
            return True
    return False'''

if OLD not in s:
    print("❌ 未找到旧的 _is_code_like")
    print("当前内容片段：")
    i = s.find("def _is_code_like")
    print(s[i:i + 800] if i >= 0 else "未找到函数")
    sys.exit(1)

s = s.replace(OLD, NEW, 1)
open(PATH, "w", encoding="utf-8").write(s)
print("✅ 已移除「纯标识符一律跳过」规则")
print("\n新规则：只有含 <<widget / <<macro / Macro.add 才跳过")
