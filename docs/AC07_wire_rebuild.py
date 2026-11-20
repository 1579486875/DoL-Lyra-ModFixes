"""AC07：固化 AC06 + 加断言 + 接入 build_all + 重建。"""
import ast
import os
import re
import subprocess
import sys

WORK = r"E:\TAML\_dol\work"

# ---- 1. 把 AC06 作为幂等脚本（已有 MARK 检查）----
src = open(os.path.join(WORK, "AC06_translate_feats.py"), encoding="utf-8").read()
# 它已经自带 MARK 幂等，直接用

# ---- 2. 加进 build_all ----
BA = os.path.join(WORK, "build_all.py")
s = open(BA, encoding="utf-8").read()
if "AC06_translate_feats" not in s:
    m = re.search(r'^([ \t]*)\(r"[^"]*TF01_nest_guard\.py".*$', s, re.M)
    ind = m.group(1)
    line = ind + ('(r"E:' + chr(92) + 'TAML' + chr(92) + '_dol' + chr(92) + 'work'
                  + chr(92) + 'AC06_translate_feats.py", "翻译 256 个成就名"),' + chr(10))
    s = s[:m.start()] + line + s[m.start():]
    open(BA, "w", encoding="utf-8").write(s)
    print("OK 已加入 build_all（TF01 之前）")
ast.parse(open(BA, encoding="utf-8").read())
print("OK 语法")

# ---- 3. 加回归断言 ----
RP = os.path.join(WORK, "REGRESS_ALL.py")
rs = open(RP, encoding="utf-8").read()
if "feats_titles_cn" not in rs:
    ANCHOR = 'chk("D", "no_bare_en_branch", n_bare == 0, f"{n_bare} 处")\n'
    NEW = '''chk("D", "no_bare_en_branch", n_bare == 0, f"{n_bare} 处")

# ★ 成就名必须全中文（setup.feats 块内的 title 字段）
def _feat_titles(text):
    m = re.search(r"setup\\.feats\\s*=\\s*\\{", text)
    if not m:
        return []
    i = m.end()
    d = 1
    while i < len(text) and d > 0:
        if text[i] == "{":
            d += 1
        elif text[i] == "}":
            d -= 1
        i += 1
    blk = text[m.start():i]
    return re.findall(r'title:\\s*"((?:[^"\\\\]|\\\\.)*)"', blk)

_ft = _feat_titles(g)
_ft_en = [t for t in _ft if not re.search(r"[\\u4e00-\\u9fff]", t)]
chk("D", "feats_titles_cn", len(_ft) > 0 and not _ft_en,
    f"{len(_ft)} 个 / 英文 {len(_ft_en)} 个")
'''
    if ANCHOR in rs:
        rs = rs.replace(ANCHOR, NEW, 1)
        open(RP, "w", encoding="utf-8").write(rs)
        ast.parse(open(RP, encoding="utf-8").read())
        print("OK 已加 D.feats_titles_cn 断言")
    else:
        print("MISS 断言锚点")

print("\n重建 ...")
r2 = subprocess.run([sys.executable, os.path.join(WORK, "build.py"),
                     "翻译 256 个成就名"],
                    capture_output=True, text=True, encoding="utf-8", errors="replace")
print(((r2.stdout or "") + (r2.stderr or ""))[-800:])
