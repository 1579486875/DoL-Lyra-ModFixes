"""第 7 轮：全量编译所有 <<script>> 块（SugarCube 内联 JS）。

注意：index 是 HTML 转义形态，<<script>> 实际写作 &lt;&lt;script&gt;&gt;。
需要先 unescape。
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

print("=" * 88)
print("提取 <<script>> 块")
print("=" * 88)

blocks = []
for m in re.finditer(r"<<script>>(.*?)<</script>>", g, re.S):
    body = m.group(1)
    pos = m.start()
    blocks.append((pos, body))

print(f"  匹配到 {len(blocks)} 个 <<script>>")

# 分类：真实脚本 vs 注释/字符串里的误匹配
SUSPECT = []
REAL = []
for pos, body in blocks:
    b = body.strip()
    # 常见误匹配：出现在 <!-- --> 里、或本身就是注释
    prefix = g[max(0, pos - 80):pos]
    in_comment = "<!--" in prefix and "-->" not in prefix
    if in_comment:
        SUSPECT.append((pos, body, "在 HTML 注释里"))
        continue
    if not b:
        SUSPECT.append((pos, body, "空"))
        continue
    REAL.append((pos, body))

print(f"  真实脚本 {len(REAL)} 个，疑似误匹配 {len(SUSPECT)} 个")

print("\n" + "=" * 88)
print("编译真实脚本")
print("=" * 88)

tmpdir = tempfile.mkdtemp(prefix="dol_sc_")
results = []
for i, (pos, body) in enumerate(REAL, 1):
    p = os.path.join(tmpdir, f"sc{i:03d}.js")
    with open(p, "w", encoding="utf-8") as f:
        f.write(body)
    try:
        r = subprocess.run(["node", "--check", p], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=120)
        ok = r.returncode == 0
        err = (r.stderr or "").strip()
    except subprocess.TimeoutExpired:
        ok = False
        err = "TIMEOUT"
    results.append((i, pos, len(body), ok, err))
    if not ok:
        print(f"  ❌ [{i:>2}] @{pos:>10} {len(body):>8,} B")
    elif i <= 5 or i % 10 == 0:
        print(f"  ✅ [{i:>2}] @{pos:>10} {len(body):>8,} B")

bad = [r for r in results if not r[3]]
print("\n" + "=" * 88)
print(f"结果：{len(results)} 个真实脚本，{len(bad)} 个失败")
print("=" * 88)

for i, pos, n, ok, err in bad[:10]:
    print(f"\n❌ [{i}] @{pos} ({n:,} B)")
    for line in err.split("\n")[:8]:
        print(f"   {line}")
    # 显示源码片段
    raw = g[pos:pos + 400]
    print(f"   源码开头: {raw[:250]!r}")

if SUSPECT:
    print(f"\n--- 疑似误匹配 {len(SUSPECT)} 个（前 10）---")
    for pos, body, why in SUSPECT[:10]:
        print(f"  @{pos} {why}: {body.strip()[:100]!r}")

shutil.rmtree(tmpdir, ignore_errors=True)
sys.exit(1 if bad else 0)
