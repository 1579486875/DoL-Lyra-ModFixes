"""第 11 轮：修正误匹配判定 + 跳过误匹配找真正的 <</script>>。

关键：误匹配的 <<script>> 后面第一个 <</script>> 不是它的结尾，
      真正的结尾在更后面。所以要「跳过散文体，继续找下一个 close」。
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
    # 以非 JS 开头字符起头 → 散文
    # 合法的 JS 首字符：字母、_、$、(、[、{、<、!、~、+、-、数字、引号、`、/、.
    if re.match(r"^[A-Za-z_$(\[{<!~+\-\d\"'`/.\\]", firstline):
        # 字母开头且无 JS 符号，仍可能是散文
        if re.match(r"^[A-Za-z]", firstline):
            return True, f"散文 {firstline[:60]!r}"
        return False, ""
    # 其余（逗号、星号、等号、分号等）都是散文
    return True, f"非常规首字符 {firstline[:40]!r}"


def extract(g):
    """正确配对：跳过散文体，继续找下一个 close。"""
    opens = [m.start() for m in re.finditer(r"<<script>>", g)]
    closes = [m.start() for m in re.finditer(r"<</script>>", g)]
    real, fake = [], []
    used_close = set()

    for op in opens:
        rest = [cp for cp in closes if cp > op and cp not in used_close]
        if not rest:
            continue
        # 逐个候选试，第一个"非散文"的就是真结尾
        chosen = None
        for cp in rest[:6]:
            body = g[op + len("<<script>>"):cp]
            prose, why = is_prose(body)
            if not prose:
                chosen = cp
                break
        if chosen is None:
            fake.append((op, is_prose(g[op + 11:rest[0]])[1] if rest else "无close", ""))
            continue
        body = g[op + len("<<script>>"):chosen]
        real.append((op, body))
        used_close.add(chosen)
    return real, fake


def run(label, path, do_compile):
    z = zipfile.ZipFile(path)
    g = html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))
    real, fake = extract(g)
    print(f"\n[{label}] 真实 {len(real)} / 误匹配 {len(fake)}")

    if not do_compile:
        return g, real, fake, []

    tmp = tempfile.mkdtemp(prefix=f"dol_{label}_")
    bad = []
    for i, (pos, body) in enumerate(real, 1):
        p = os.path.join(tmp, f"s{i:03d}.js")
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

    print(f"  编译 {len(real)} 个，失败 {len(bad)} 个" + ("  ✅" if not bad else ""))
    for i, pos, n, err in bad[:8]:
        print(f"\n  ❌ [{i}] @{pos} ({n:,} B)")
        for line in err.split("\n")[:5]:
            print(f"     {line}")
        print(f"     {g[pos:pos+200]!r}")
    shutil.rmtree(tmp, ignore_errors=True)
    return g, real, fake, bad


print("=" * 88)
print("modded")
print("=" * 88)
mg, mreal, mfake, mbad = run("modded", APK, True)

print("\n" + "=" * 88)
print("vanilla 对照")
print("=" * 88)
vg, vreal, vfake, vbad = run("vanilla", VAN, True)

print("\n" + "=" * 88)
print("结论")
print("=" * 88)
print(f"  modded : 真实 {len(mreal)} 个，语法错误 {len(mbad)} 个")
print(f"  vanilla: 真实 {len(vreal)} 个，语法错误 {len(vbad)} 个")
if mbad and not vbad:
    print("  ⚠️ modded 独有错误 —— 需修")
elif mbad and vbad:
    print("  ✅ 两边都有同类错误（原版问题）")
elif not mbad:
    print("  ✅ modded 全部通过")

with open(r"E:\TAML\_dol\work\_sc_list.txt", "w", encoding="utf-8") as f:
    for i, (pos, body) in enumerate(mreal, 1):
        f.write(f"{i}\t{pos}\t{len(body)}\n")
    f.write(f"# total={len(mreal)} fake={len(mfake)} bad={len(mbad)}\n")

sys.exit(1 if (mbad and not vbad) else 0)
