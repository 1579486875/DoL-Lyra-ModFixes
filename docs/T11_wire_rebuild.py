"""T11：固化 T10 + 修正 build_all 顺序 + 重建。

顺序问题：TF01_nest_guard 必须最后，但 R10/R17 现在排在它后面。
正确收尾顺序：... → R10 → R17 → T10 → TF01（最后）
"""
import ast
import os
import re
import shutil
import subprocess
import sys

WORK = r"E:\TAML\_dol\work"

# ---- 1. T10 已自带 MARK 幂等，无需复制 ----
print("OK T10 就绪")

# ---- 2. 重排 build_all ----
BA = os.path.join(WORK, "build_all.py")
s = open(BA, encoding="utf-8").read()

# 先删掉已有的 T10 / R10 / R17 / O05 / P09 行（稍后按正确顺序重新插入）
def drop_line(text, key):
    pat = re.compile(r'^[ \t]*\(r"[^"]*' + re.escape(key) + r'\.py".*\n', re.M)
    return pat.sub("", text)

for key in ("T10_fix_templates", "R10_fix_clothing_slot", "R17_fix_slot_fallback"):
    s = drop_line(s, key)

# 找 TF01 那一行作为锚点
m = re.search(r'^([ \t]*)\(r"[^"]*TF01_nest_guard\.py".*$', s, re.M)
if not m:
    print("MISS 找不到 TF01")
    sys.exit(1)
ind = m.group(1)

def mk(key, desc):
    return ind + ('(r"E:' + chr(92) + 'TAML' + chr(92) + '_dol' + chr(92) + 'work'
                  + chr(92) + key + '.py", "' + desc + '"),' + chr(10))

block = (
    mk("R10_fix_clothing_slot", "补全 mod 服装缺失的 slot（clothingShopv2 侧）") +
    mk("R17_fix_slot_fallback", "generateshoppage 的 slot 兜底（Forest Shop 崩溃）") +
    mk("T10_fix_templates", "Template.add 英文清理 + 恢复被翻的模板名")
)

# 插到 TF01 之前
s = s[:m.start()] + block + s[m.start():]
open(BA, "w", encoding="utf-8").write(s)

ast.parse(open(BA, encoding="utf-8").read())
print("OK build_all 语法")

PAT = re.compile(r'E:\\\\?TAML\\\\?_dol\\\\?work\\\\?([A-Za-z0-9_]+\.py)')
steps = PAT.findall(open(BA, encoding="utf-8").read())
print(f"\n共 {len(steps)} 步，末尾 8 步:")
for i, f in enumerate(steps[-8:], len(steps) - 7):
    print(f"  {i}. {f}")

if steps[-1] != "TF01_nest_guard.py":
    print("⚠️ TF01 不在最后！")
else:
    print("✅ TF01 在最后")

# ---- 3. 给 REGRESS 加两条断言 ----
RP = os.path.join(WORK, "REGRESS_ALL.py")
rs = open(RP, encoding="utf-8").read()
if "no_cn_template_name" not in rs:
    NEW = '''chk("C", "no_macro_in_if", n_macro_in_if == 0, f"{n_macro_in_if} 处")

# ★ Template.add 的模板名不能含中文（否则 ?xxx 模板调用失效）
_tpl_names = re.findall(r'Template\\.add\\(\\s*"([^"]+)"', g)
_cn_tpl = [n for n in _tpl_names if re.search(r"[\\u4e00-\\u9fff]", n)]
chk("D", "no_cn_template_name", not _cn_tpl, str(_cn_tpl))
'''
    OLD = 'chk("C", "no_macro_in_if", n_macro_in_if == 0, f"{n_macro_in_if} 处")\n'
    if OLD in rs:
        rs = rs.replace(OLD, NEW, 1)
        open(RP, "w", encoding="utf-8").write(rs)
        ast.parse(open(RP, encoding="utf-8").read())
        print("OK 已加 D.no_cn_template_name 断言")
    else:
        print("MISS 断言锚点")

# ---- 4. 重建 ----
print("\n重建 ...")
r2 = subprocess.run([sys.executable, os.path.join(WORK, "build.py"),
                     "Template.add 英文清理 + 恢复被翻模板名"],
                    capture_output=True, text=True, encoding="utf-8", errors="replace")
out = ((r2.stdout or "") + (r2.stderr or ""))
print(out[-1200:])
