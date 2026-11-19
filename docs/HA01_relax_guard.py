"""修复：收紧 BE_bake_i18n 的代码保护。

上一版太激进，误伤合法翻译：
  - 全小写单词一律跳过（eels / slimes / pain ... 全没了）
  - <<script / => / && / || 一律跳过（整条 <<set ... map(...)>> 被丢）

新版只挡两类真正危险的：
  1) f 或 t 里出现 <<widget / <<macro / Macro.add（宏名不能翻）
  2) f 是「纯标识符」（^[A-Za-z_][A-Za-z0-9_]*$，无空格）—— 这是变量/widget 名
"""
import re
import sys

PATH = r"E:\TAML\_dol\work\BE_bake_i18n.py"
s = open(PATH, encoding="utf-8").read()

# 找到旧的 helper 整块替换
START = "CODE_PATTERNS = ("
END = "def fix_block(m):"
i = s.find(START)
j = s.find(END)
if i < 0 or j < 0:
    print("❌ 未找到旧 helper")
    sys.exit(1)

NEW_HELPER = '''def _is_code_like(text):
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
    return False


'''

s = s[:i] + NEW_HELPER + s[j:]
open(PATH, "w", encoding="utf-8").write(s)
print("✅ 已收紧代码保护")
print("\n新规则：")
print("  挡：含 <<widget / <<macro / Macro.add，或 f 整体是纯标识符")
print("  放行：<<set / <<link / => / 普通单词（这些必须翻）")
