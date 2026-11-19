"""第 6 轮：零错误层① JS 语法 —— 编译 index 里所有 <script> 块。

判据（模板 §二.编译）：0 error、0 warning。
手段：提取每个 script 到临时文件，用 node --check 编译。
"""
import html
import os
import re
import subprocess
import sys
import tempfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"

import zipfile

z = zipfile.ZipFile(APK)
raw = z.read("assets/www/index.html").decode("utf-8", "replace")

print("=" * 88)
print("提取所有 <script> 块")
print("=" * 88)

blocks = []
for m in re.finditer(r"<script\b([^>]*)>(.*?)</script>", raw, re.S):
    attrs = m.group(1).strip()
    body = m.group(2)
    # 属性里含 src 的是外部脚本，跳过
    if re.search(r'src\s*=', attrs):
        continue
    if not body.strip():
        continue
    kind = "text/javascript"
    if "twine-javascript" in attrs:
        kind = "twine-user-script"
    elif "sugarcube" in attrs:
        kind = "sugarcube"
    elif "libraries" in attrs:
        kind = "libraries"
    else:
        mid = re.search(r'id="([^"]*)"', attrs)
        kind = mid.group(1) if mid else "?"
    blocks.append((kind, attrs[:70], body))

print(f"  共 {len(blocks)} 个内联脚本块")
for i, (k, a, b) in enumerate(blocks, 1):
    print(f"  {i:>2}. [{k[:34]:<34}] {len(b):>10,} B")

print("\n" + "=" * 88)
print("逐个 node --check 编译")
print("=" * 88)

tmpdir = tempfile.mkdtemp(prefix="dol_js_")
results = []
for i, (k, a, body) in enumerate(blocks, 1):
    p = os.path.join(tmpdir, f"block{i:02d}.js")
    with open(p, "w", encoding="utf-8") as f:
        f.write(body)
    r = subprocess.run(["node", "--check", p], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=300)
    ok = r.returncode == 0
    results.append((i, k, len(body), ok, (r.stderr or "").strip()))
    mark = "✅" if ok else "❌"
    print(f"  {mark} [{i:>2}] {k[:30]:<30} {len(body):>10,} B")
    if not ok:
        err = (r.stderr or "").strip().split("\n")
        for line in err[:6]:
            print(f"        {line}")

print("\n" + "=" * 88)
bad = [r for r in results if not r[3]]
print(f"结果：{len(results)} 个块，{len(bad)} 个编译失败")
print("=" * 88)
if bad:
    for i, k, n, ok, err in bad:
        print(f"\n❌ [{i}] {k}")
        print(f"   {err[:400]}")
else:
    print("✅ 全部通过（0 error）")

# 清理
import shutil
shutil.rmtree(tmpdir, ignore_errors=True)
sys.exit(1 if bad else 0)
