"""第 27 轮：链接目标可达性 —— 所有 [[文本|目标]] / <<include>> 的目标 passage 是否存在。"""
import html
import re
import sys
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"


def load(p):
    z = zipfile.ZipFile(p)
    raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    blocks = {}
    for m in re.finditer(r'<tw-passagedata([^>]*)>(.*?)</tw-passagedata>', raw, re.S):
        nm = re.search(r'name="([^"]+)"', m.group(1))
        if nm:
            blocks[html.unescape(nm.group(1))] = html.unescape(m.group(2))
    return blocks


def check(blocks, label):
    names = set(blocks)
    missing_links = []
    missing_inc = []

    for pn, body in blocks.items():
        # [[文本|目标]] 或 [[目标]]
        for m in re.finditer(r"\[\[([^\]\[]+)\]\]", body):
            inner = m.group(1)
            if "|" in inner:
                target = inner.split("|")[-1].strip()
            elif "->" in inner:
                target = inner.split("->")[-1].strip()
            elif "<-" in inner:
                target = inner.split("<-")[0].strip()
            else:
                target = inner.strip()
            # 目标可能是变量/宏
            if not target or target.startswith("$") or target.startswith("_") or "<<" in target:
                continue
            if target not in names:
                missing_links.append((pn, target))

        # <<include "目标">>
        for m in re.finditer(r'<<include\s+"([^"]+)"', body):
            t = m.group(1)
            if t not in names:
                missing_inc.append((pn, t))

    print("=" * 90)
    print(f"{label}  ({len(blocks)} passage)")
    print("=" * 90)
    print(f"  <<link>> 目标缺失: {len(missing_links)}")
    print(f"  <<include>> 目标缺失: {len(missing_inc)}")

    if missing_links:
        from collections import Counter
        c = Counter(t for _, t in missing_links)
        print(f"\n  缺失链接目标（Top 15）:")
        for t, n in c.most_common(15):
            src = [p for p, x in missing_links if x == t][:2]
            print(f"    {n:>3}× {t!r}  来自 {src}")

    if missing_inc:
        from collections import Counter
        c = Counter(t for _, t in missing_inc)
        print(f"\n  缺失 include 目标:")
        for t, n in c.most_common(15):
            src = [p for p, x in missing_inc if x == t][:2]
            print(f"    {n:>3}× {t!r}  来自 {src}")

    return set(t for _, t in missing_links), set(t for _, t in missing_inc)


mb = load(APK)
vb = load(VAN)

ml, mi = check(mb, "modded")
vl, vi = check(vb, "vanilla")

print("\n" + "=" * 90)
print("结论（只看 modded 独有）")
print("=" * 90)
ml_only = ml - vl
mi_only = mi - vi
print(f"  modded 独有缺失链接目标: {sorted(ml_only) if ml_only else '无'}")
print(f"  modded 独有缺失 include: {sorted(mi_only) if mi_only else '无'}")

# passage 集合差异
mp = set(mb)
vp = set(vb)
extra = mp - vp
lack = vp - mp
print(f"\n  modded 多出 passage: {sorted(extra) if extra else '无'}")
print(f"  modded 缺少 passage: {sorted(lack)[:20] if lack else '无'}  （共 {len(lack)}）")

sys.exit(1 if (ml_only or mi_only or lack) else 0)
