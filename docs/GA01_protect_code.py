"""紧急修复：BE_bake_i18n 误翻 widget 名 / 标识符。

现象：
  <<widget "characteristics">>  ->  <<widget "ch一↑racteristics">>
  <<widget "flesh_text">>       ->  <<widget "f浅色_text">>
导致 SugarCube 报 invalid macro name，游戏部分功能失效。

策略：i18n 条目只要「原文或译文里出现宏定义/代码特征」就跳过。
      宁可少翻，不可改坏代码。
"""
import re
import sys

PATH = r"E:\TAML\_dol\work\BE_bake_i18n.py"
s = open(PATH, encoding="utf-8").read()

OLD = """    for it in sorted(lst, key=lambda x: x.get("pos") or 0, reverse=True):
        f, t = it.get("f"), it.get("t")
        if not f or t is None:
            continue
        pos = it.get("pos", -1)"""

NEW = """    for it in sorted(lst, key=lambda x: x.get("pos") or 0, reverse=True):
        f, t = it.get("f"), it.get("t")
        if not f or t is None:
            continue
        # === 安全检查：绝不翻译代码/标识符 ===
        if _is_code_like(f) or _is_code_like(t):
            total_skip += 1
            continue
        pos = it.get("pos", -1)"""

if OLD not in s:
    print("❌ 未找到锚点，请手工检查")
    sys.exit(1)

s = s.replace(OLD, NEW, 1)

# 插入 _is_code_like 定义
HELPER = '''
CODE_PATTERNS = (
    "<<widget", "<<macro", "<<script", "<<silently",
    "Macro.add", "function(", "=>", "!!", "&&", "||",
)

def _is_code_like(text):
    """判断一段文本是否是代码/标识符，不能参与翻译。"""
    if not text:
        return False
    # 明确的代码特征
    for p in CODE_PATTERNS:
        if p in text:
            return True
    # 含下划线的短标识符（如 flesh_text）
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", text) and "_" in text:
        return True
    # 全小写单词且无空格（如 characteristics）—— 单个标识符
    if re.fullmatch(r"[a-z][a-z0-9]*", text) and len(text) <= 30:
        return True
    return False


'''

# 放在 fix_block 之前
anchor = "def fix_block(m):"
if anchor not in s:
    print("❌ 未找到 fix_block")
    sys.exit(1)
s = s.replace(anchor, HELPER + anchor, 1)

open(PATH, "w", encoding="utf-8").write(s)
print("✅ BE_bake_i18n.py 已加入代码保护")
print("\n保护规则：")
print("  1) 含 <<widget / <<macro / <<script / Macro.add / => 等 -> 跳过")
print("  2) 纯标识符（含下划线或全小写单词）-> 跳过")
