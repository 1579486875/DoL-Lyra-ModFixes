"""给 BE_bake_i18n 加「widget 名黑名单」。

先扫原始 index 里所有 <<widget "名字">>，建立黑名单；
翻译时如果 f 恰好是某个 widget 名，直接跳过。

这样：
  slide -> 滑行   会被跳过（slide 是 widget 名）
  Beast -> 野兽   正常翻译（Beast 不是 widget 名）
  Monstergirl -> 怪物女孩  正常翻译
"""
import os
import re
import sys

PATH = r"E:\TAML\_dol\work\BE_bake_i18n.py"
s = open(PATH, encoding="utf-8").read()

# 1) 在 _is_code_like 之前插入黑名单构建
ANCHOR = "def _is_code_like(text, other=None):"
if ANCHOR not in s:
    print("❌ 未找到 _is_code_like")
    sys.exit(1)

BLOCK = '''# === widget 名 / setup 键黑名单（由下方 load 时填充）===
_RESERVED = set()


def _build_reserved(data_text):
    """从 index.html 原文里扫出所有不能翻译的标识符。"""
    import html as _h
    g = _h.unescape(data_text)
    for m in re.finditer(r'<<widget\\s+"([^"]+)"', g):
        _RESERVED.add(m.group(1))
    # setup 对象的所有键（只收纯 ASCII 的，中文键本来就不该翻）
    for m in re.finditer(r"<<set\\s+setup\\.(\\w+)\\s+to", g):
        _RESERVED.add(m.group(1))
    return len(_RESERVED)


'''

if "_build_reserved" not in s:
    s = s.replace(ANCHOR, BLOCK + ANCHOR, 1)
    print("✅ 已插入黑名单构建函数")

# 2) 在 _is_code_like 里加黑名单检查
OLD_TAIL = '''    if not text:
        return False
    for kw in ("<<widget", "<<macro", "Macro.add"):
        if kw in text:
            return True'''

NEW_TAIL = '''    if not text:
        return False
    for kw in ("<<widget", "<<macro", "Macro.add"):
        if kw in text:
            return True
    # widget 名 / setup 键：整条 f 恰好等于它们时不能翻
    if text.strip() in _RESERVED:
        return True'''

if OLD_TAIL in s:
    s = s.replace(OLD_TAIL, NEW_TAIL, 1)
    print("✅ 已加入黑名单检查")
else:
    print("⚠️ 未找到 _is_code_like 尾部锚点")

# 3) 在 main 开头调用 _build_reserved
M_ANCHOR = "def main():"
if M_ANCHOR in s:
    # 找 data 变量定义
    m = re.search(r"(data = open\(HTML[^\n]*\n)", s)
    if m:
        ins = m.group(1) + "    n_res = _build_reserved(data)\n    print(f\"  已加载 {n_res} 个保留标识符（widget 名 + setup 键）\")\n"
        s = s[:m.start(1)] + ins + s[m.end(1):]
        print("✅ 已在 main 里调用 _build_reserved")
    else:
        print("⚠️ 未找到 data 定义")

open(PATH, "w", encoding="utf-8").write(s)
print("\n完成")
