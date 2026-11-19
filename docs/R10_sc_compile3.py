"""第 10 轮：修正误匹配判定，重新全量编译 <<script>>。

判定规则（从第 9 轮教训）：
  - 第一行含 JS 结构符号 ( ) { } ; = => 或 // 或 /* → 代码
  - 第一行以字母开头且无上述符号 → 散文（误匹配）
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
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"


def is_prose(body):
    head = body.lstrip()
    if not head:
        return True, "空"
    firstline = head.split("\n", 1)[0]
    # 有 JS 符号 → 代码
    if re.search(r"[(){};=]|=>", firstline) or firstline.lstrip().startswith(("//", "/*")):
        return False, ""
    # 以字母开头且无 JS 符号 → 散文
    if re.match(r"^[A-Za-z]", firstline):
        return True, f"散文首行 {firstline[:60]!r}"
    return False, ""


def analyze(path, label):
    z = zipfile.ZipFile(path)
    g = html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))

    opens = [m.start() for m in re.finditer(r"<<script>>", g)]
    closes = [m.start() for m in re.finditer(r"<</script>>", g)]

    real, fake = [], []
    for op in opens:
        cand = [cp for cp in closes if cp > op]
        if not cand:
            continue
        cp = cand[0]
        body = g[op + len("<<script>>"):cp]
        prose, why = is_prose(body)
        if prose:
            fake.append((op, why, body[:80]))
        else:
            real.append((op, body))

    print(f"\n[{label}] <<script>> {len(opens)} 个 → 真实 {len(real)} / 误匹配 {len(fake)}")
    return g, real, fake


mg, mreal, mfake = analyze(APK, "modded")
vg, vreal, vfake = analyze(VAN, "vanilla")

print("\n" + "=" * 88)
print("编译 modded 的真实脚本")
print("=" * 88)

tmpdir = tempfile.mkdtemp(prefix="dol_sc3_")
bad = []
for i, (pos, body) in enumerate(mreal, 1):
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
    if not ok:
        bad.append((i, pos, len(body), err))
        print(f"  ❌ [{i:>2}] @{pos:>10} {len(body):>10,} B")

print(f"\n  结果：{len(mreal)} 个，失败 {len(bad)} 个" + ("  ✅ 全部通过" if not bad else ""))

for i, pos, n, err in bad[:6]:
    print(f"\n❌ [{i}] @{pos} ({n:,} B)")
    for line in err.split("\n")[:6]:
        print(f"   {line}")
    print(f"   {mg[pos:pos+250]!r}")

# 对照：vanilla 同样失败吗？
if bad:
    print("\n" + "=" * 88)
    print("对照 vanilla 同样位置")
    print("=" * 88)
    vtmp = tempfile.mkdtemp(prefix="dol_vsc_")
    for i, (pos, body) in enumerate(vreal, 1):
        p = os.path.join(vtmp, f"v{i:03d}.js")
        with open(p, "w", encoding="utf-8") as f:
            f.write(body)
    vr = []
    for i, (pos, body) in enumerate(vreal, 1):
        p = os.path.join(vtmp, f"v{i:03d}.js")
        r = subprocess.run(["node", "--check", p], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=180)
        if r.returncode != 0:
            vr.append((i, pos, len(body)))
    print(f"  vanilla 失败 {len(vr)} 个: {vr[:5]}")
    shutil.rmtree(vtmp, ignore_errors=True)

print("\n" + "=" * 88)
print(f"结论：modded 真实 <<script>> {len(mreal)} 个，语法错误 {len(bad)} 个")
print(f"      （vanilla 对照 {len(vreal)} 个）")
print("=" * 88)

with open(r"E:\TAML\_dol\work\_sc_list.txt", "w", encoding="utf-8") as f:
    for i, (pos, body) in enumerate(mreal, 1):
        f.write(f"{i}\t{pos}\t{len(body)}\n")
    f.write(f"# total {len(mreal)} fake {len(mfake)}\n")

shutil.rmtree(tmpdir, ignore_errors=True)
sys.exit(1 if bad else 0)
