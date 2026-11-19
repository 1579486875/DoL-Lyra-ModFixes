"""第 8 轮：修正 <<script>> 误匹配，重新编译。

误匹配特征：body 以 ','、'*'、'/'、字母开头且首行像英文散文。
真实 [[script]] 块通常以换行 + 代码开头。
"""
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
z = zipfile.ZipFile(APK)
g = html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))


def looks_like_prose(body):
    """判断 body 开头像不像英文散文/注释，而不是 JS 代码。"""
    head = body.lstrip()
    if not head:
        return True
    first = head[0]
    # 以这些开头的一律不是 JS
    if first in ",*/.）)]}":
        return True
    # 第一行是纯英文句子（含空格且不含 JS 符号）
    firstline = head.split("\n", 1)[0]
    if re.match(r"^[A-Za-z][A-Za-z ,']+[.,;]", firstline):
        return True
    return False


print("=" * 88)
print("提取并分类 <<script>> 块")
print("=" * 88)

REAL = []
FAKE = []

# 用位置逐个配对：从每个 <<script>> 找最近的 <</script>>，但跳过散文体
pos = 0
open_positions = [m.start() for m in re.finditer(r"<<script>>", g)]
close_positions = [m.start() for m in re.finditer(r"<</script>>", g)]

for op in open_positions:
    # 找 >= op 的第一个 close
    cand = [cp for cp in close_positions if cp > op]
    if not cand:
        continue
    cp = cand[0]
    body = g[op + len("<<script>>"):cp]
    if looks_like_prose(body):
        FAKE.append((op, body, "散文/注释体"))
        continue
    REAL.append((op, body))

print(f"  <<script>> 共 {len(open_positions)} 个")
print(f"  真实脚本 {len(REAL)} 个，误匹配 {len(FAKE)} 个")

if FAKE:
    print("\n--- 误匹配明细 ---")
    for pos, body, why in FAKE:
        print(f"  @{pos} {why}: {body.strip()[:110]!r}")

print("\n" + "=" * 88)
print("编译真实脚本")
print("=" * 88)

tmpdir = tempfile.mkdtemp(prefix="dol_sc2_")
results = []
for i, (pos, body) in enumerate(REAL, 1):
    p = os.path.join(tmpdir, f"sc{i:03d}.js")
    with open(p, "w", encoding="utf-8") as f:
        f.write(body)
    try:
        r = subprocess.run(["node", "--check", p], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=180)
        ok = r.returncode == 0
        err = (r.stderr or "").strip()
    except subprocess.TimeoutExpired:
        ok, err = False, "TIMEOUT"
    results.append((i, pos, len(body), ok, err))
    if not ok:
        print(f"  ❌ [{i:>2}] @{pos:>10} {len(body):>10,} B")

bad = [r for r in results if not r[3]]
print(f"\n  编译完成：{len(results)} 个，失败 {len(bad)} 个")
if not bad:
    print("  ✅ 全部通过")

for i, pos, n, ok, err in bad[:8]:
    print(f"\n❌ [{i}] @{pos} ({n:,} B)")
    for line in err.split("\n")[:6]:
        print(f"   {line}")
    print(f"   源码开头: {g[pos:pos+300]!r}")

print("\n" + "=" * 88)
print(f"结论：真实 <<script>> {len(REAL)} 个，{len(bad)} 个语法错误")
print("=" * 88)

# 保存清单供后续轮次用
with open(r"E:\TAML\_dol\work\_sc_list.txt", "w", encoding="utf-8") as f:
    for i, (pos, body) in enumerate(REAL, 1):
        f.write(f"{i}\t{pos}\t{len(body)}\n")

shutil.rmtree(tmpdir, ignore_errors=True)
sys.exit(1 if bad else 0)
