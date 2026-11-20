"""F04：对比基线的缺失链接。"""
import html as H
import os
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
ARCHIVE = r"E:\TAML\_dol\archive"
GOOD = os.path.join(ARCHIVE, "DoL-Lyra-0.5.12.13-CHS-modded_20261120-061313_修复arsc可安装.apk")


def get_p(path):
    raw = zipfile.ZipFile(path).read("assets/www/index.html").decode("utf-8", "replace")
    out = {}
    for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
        out[m.group(1)] = H.unescape(m.group(2))
    return out


def missing_links(ps):
    names = set(ps)
    miss = set()
    for pname, body in ps.items():
        for m in re.finditer(r'<<link\s+\[\[\s*([^\]|]*?)\s*\|\s*([^\]]+?)\s*\]\]', body):
            tgt = m.group(2).strip()
            if tgt in names:
                continue
            if any(c in tgt for c in "$_<{"):
                continue
            miss.add(tgt)
    return miss


def missing_includes(ps):
    names = set(ps)
    miss = set()
    for pname, body in ps.items():
        for m in re.finditer(r'<<include\s+"([^"]+)"', body):
            if m.group(1) not in names:
                miss.add(m.group(1))
    return miss


cur = get_p(APK)
base = get_p(GOOD)

cm = missing_links(cur)
bm = missing_links(base)
ci = missing_includes(cur)
bi = missing_includes(base)

print("=" * 100)
print("<<link>> 缺失目标对比")
print("=" * 100)
print(f"  基线: {len(bm)}")
print(f"  当前: {len(cm)}")
new_miss = sorted(cm - bm)
fixed = sorted(bm - cm)
print(f"\n  {'✅ 无新增' if not new_miss else '❌ 新增 ' + str(len(new_miss))}")
for t in new_miss:
    print(f"    + {t!r}")
print(f"\n  已修好: {len(fixed)}")

print("\n" + "=" * 100)
print("<<include>> 缺失对比")
print("=" * 100)
print(f"  基线: {len(bi)}  {sorted(bi)}")
print(f"  当前: {len(ci)}  {sorted(ci)}")
print(f"  {'✅ 无新增' if not (ci - bi) else '❌ 新增'}")

print("\n" + "=" * 100)
print("带引号的 link 目标（语法错误）")
print("=" * 100)
for pname, body in cur.items():
    for m in re.finditer(r'<<link\s+\[\[\s*([^\]|]*?)\s*\|\s*("[^"]*"|\'[^\']*\')\s*\]\]', body):
        print(f"  [{pname}] {m.group(0)[:120]!r}")
