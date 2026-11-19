"""精修 _is_code_like：按「译文是否含 ASCII 字母」区分破坏性翻译。

规则：
  f 是纯标识符（无空格无标点）时：
    t 也含 ASCII 字母  -> 破坏了标识符（ch一个racteristics / f浅色_text），跳过
    t 是纯中文        -> 正常翻译（Monstergirl -> 怪物女孩），保留
"""
import re
import sys

PATH = r"E:\TAML\_dol\work\BE_bake_i18n.py"
s = open(PATH, encoding="utf-8").read()

OLD = '''def _is_code_like(text):
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

NEW = '''def _is_code_like(text, other=None):
    """判断这条 i18n 条目是否不能参与翻译。

    挡的情况：
      1) 出现 <<widget / <<macro / Macro.add —— 宏名不能变
      2) f 是纯标识符（无空格/标点）且 t 里也含 ASCII 字母
         —— 说明翻译破坏了标识符，如 characteristics -> ch一个racteristics

    不挡的情况：
      - f 是纯标识符但 t 是纯中文，如 Monstergirl -> 怪物女孩（正常 UI 翻译）
      - 含宏的普通文本
    """
    if not text:
        return False
    for kw in ("<<widget", "<<macro", "Macro.add"):
        if kw in text:
            return True
    # 纯标识符：看另一边是否仍是 ASCII（破坏性翻译）
    if other is not None:
        is_ident = bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,60}", text))
        if is_ident and re.search(r"[A-Za-z]", other) and not re.search(r"[\\u4e00-\\u9fff]", other):
            return True
        # 英文标识符 + 译文里混着 ASCII 标识符（部分保留原文）
        if is_ident and re.search(r"[A-Za-z_]{3,}", other) and re.search(r"[\\u4e00-\\u9fff]", other):
            return True
    return False'''

if OLD not in s:
    print("❌ 未找到旧的 _is_code_like")
    sys.exit(1)

s = s.replace(OLD, NEW, 1)

# 修改调用点
OLD_CALL = "if _is_code_like(f) or _is_code_like(t):"
NEW_CALL = "if _is_code_like(f, t) or _is_code_like(t, f):"
if OLD_CALL in s:
    s = s.replace(OLD_CALL, NEW_CALL, 1)
    print("✅ 已更新调用点")
else:
    print("⚠️ 未找到调用点，请手工检查")

open(PATH, "w", encoding="utf-8").write(s)
print("✅ 已更新 _is_code_like")
print("\n新规则：")
print("  挡：含 <<widget / <<macro / Macro.add")
print("  挡：f 是纯标识符 且 t 里混着 ASCII（破坏性翻译）")
print("  放行：f 是纯标识符 但 t 是纯中文（正常 UI 翻译）")
