"""第 9-16 轮：链接目标检查。

检查：
  A) <<link [[文字|目标]]>> 的目标 passage 是否存在
  B) <<goto "目标">> 的目标
  C) <<display "目标">> / <<include "目标">>
  D) <<link>> 里只有链接文字没有目标（语法错）
  E) 目标名含未反转义的实体
"""
import html
import re
import zipfile
from collections import Counter, defaultdict

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"


def load(p):
    z = zipfile.ZipFile(p)
    raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    blocks = {}
    for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
        blocks[html.unescape(m.group(1))] = html.unescape(m.group(2))
    return html.unescape(raw), blocks


mg, mb = load(APK)
vg, vb = load(VAN)

print(f"modded {len(mb)} passage / vanilla {len(vb)} passage")


def collect_targets(raw, blocks):
    """收集所有链接目标。"""
    out = []  # (kind, source_passage, target)
    # <<link [[text|target]]>> 或 <<link [[target]]>>
    for m in re.finditer(r'<<link\s+\[\[(.{1,300}?)\]\]', raw, re.S):
        inner = m.group(1)
        if "|" in inner:
            tgt = inner.rsplit("|", 1)[1].strip()
        elif "->" in inner:
            tgt = inner.rsplit("->", 1)[1].strip()
        elif "<-" in inner:
            tgt = inner.split("<-", 1)[0].strip()
        else:
            tgt = inner.strip()
        out.append(("link", None, tgt))
    # <<link "text" "target">>
    for m in re.finditer(r'<<link\s+"[^"]*"\s+"([^"]+)"', raw):
        out.append(("link2", None, m.group(1)))
    # <<goto "target">>
    for m in re.finditer(r'<<goto\s+"([^"]+)"', raw):
        out.append(("goto", None, m.group(1)))
    for m in re.finditer(r'<<goto\s+\[\[([^\]]+)\]\]', raw):
        out.append(("goto", None, m.group(1)))
    # <<display "target">> / <<include "target">>
    for m in re.finditer(r'<<(?:display|include)\s+"([^"]+)"', raw):
        out.append(("include", None, m.group(1)))
    return out


def audit(raw, blocks, label):
    print("\n" + "=" * 90)
    print(f"[{label}] 链接目标")
    print("=" * 90)
    targets = collect_targets(raw, blocks)
    print(f"  收集 {len(targets)} 个")

    missing = Counter()
    dynd = 0
    for kind, src, tgt in targets:
        t = tgt.strip()
        if not t:
            continue
        # 动态目标（含 $ _ + << 等）跳过
        if any(x in t for x in ("$", "_", "+", "<<", "[", "]", "(", ")")):
            dynd += 1
            continue
        if t not in blocks:
            missing[(kind, t)] += 1
    print(f"  动态目标 {dynd} 个（跳过）")
    print(f"  静态目标缺失 {len(missing)} 种")
    for (k, t), n in missing.most_common(30):
        print(f"    [{k}] {t!r} × {n}")
    return missing


m_miss = audit(mg, mb, "modded")
v_miss = audit(vg, vb, "vanilla")

print("\n" + "=" * 90)
print("modded 独有的缺失目标（我们引入的）")
print("=" * 90)
only = {k: v for k, v in m_miss.items() if k not in v_miss}
print(f"  {len(only)} 种")
for (k, t), n in sorted(only.items(), key=lambda x: -x[1])[:25]:
    print(f"    [{k}] {t!r} × {n}")
    # 找引用处
    for m in list(re.finditer(r"\|\s*" + re.escape(t) + r"\s*\]\]", mg))[:2]:
        print(f"      {mg[max(0,m.start()-150):m.start()+80]!r}")

print("\n" + "=" * 90)
print("链接目标名里的 HTML 实体残留")
print("=" * 90)
n = 0
for m in re.finditer(r'\[\[[^\]]*\|([^\]]*&[a-z]+;[^\]]*)\]\]', mg):
    n += 1
    if n <= 10:
        print(f"  {m.group(0)[:120]!r}")
print(f"  共 {n} 处")
