"""第 37 轮：CSS class / 颜色名 / 图片路径 三维度对比。"""
import html
import re
import sys
import zipfile
from collections import Counter

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"
CJK = re.compile(r"[\u4e00-\u9fff]")


def load(p):
    z = zipfile.ZipFile(p)
    raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    return html.unescape(raw), z.namelist()


mg, mnames = load(APK)
vg, vnames = load(VAN)

# 1) CSS class
def classes(g):
    out = Counter()
    for m in re.finditer(r'class\s*=\s*"([^"]*)"', g):
        for c in m.group(1).split():
            if c:
                out[c] += 1
    return out


mc = classes(mg)
vc = classes(vg)
only_m = sorted(set(mc) - set(vc))
only_v = sorted(set(vc) - set(mc))

print("=" * 90)
print("1) CSS class")
print("=" * 90)
print(f"  modded {len(mc)} / vanilla {len(vc)}")
print(f"  modded 独有 {len(only_m)}: {[x for x in only_m if CJK.search(x) or len(x) > 3][:15]}")
print(f"  vanilla 独有 {len(only_v)}: {only_v[:15]}")
m_cjk = [x for x in mc if CJK.search(x) and not x.startswith(("'", '"', "("))]
print(f"  modded 含中文 class（排除表达式）: {m_cjk}")

# 2) 图片路径
def imgpaths(g):
    return set(re.findall(r"img/[a-zA-Z0-9_/\-]+\.(?:png|jpg|jpeg|gif|webp)", g))


mi = imgpaths(mg)
vi = imgpaths(vg)
print("\n" + "=" * 90)
print("2) 图片路径")
print("=" * 90)
print(f"  modded 引用 {len(mi)} / vanilla {len(vi)}")
only_mi = sorted(mi - vi)
print(f"  modded 独有 {len(only_mi)}: {only_mi[:12]}")

# 检查独有路径是否在 APK 里
mfiles = set(n.replace("assets/www/", "") for n in mnames)
missing_mi = [p for p in only_mi if p not in mfiles]
print(f"  独有路径中缺失于 APK: {missing_mi if missing_mi else '无'}")

# 全部路径的缺失率
all_missing = [p for p in mi if p not in mfiles]
print(f"  modded 全部引用中缺失: {len(all_missing)}/{len(mi)}")
if all_missing[:10]:
    print(f"    前 10: {all_missing[:10]}")

# 3) 颜色名
def colours(g):
    return set(re.findall(r'class="([a-z]+)"', g)) | set(re.findall(r"colourName\(['\"]([a-z ]+)['\"]\)", g))


print("\n" + "=" * 90)
print("3) setup.colours 表")
print("=" * 90)
for label, g in (("modded", mg), ("vanilla", vg)):
    m = re.search(r"setup\.colours\s*=\s*\{(.{0,2000})", g, re.S)
    if m:
        has_cn = bool(CJK.search(m.group(1)))
        print(f"  {label}: 有 setup.colours，含中文 {has_cn}")
    else:
        print(f"  {label}: 无 setup.colours 定义")

print("\n" + "=" * 90)
print("结论")
print("=" * 90)
bad = 0
if m_cjk:
    print(f"  ⚠️ 含中文的 class: {m_cjk}")
    bad += 1
if missing_mi:
    print(f"  ❌ modded 独有但缺失的图片: {missing_mi}")
    bad += 1
if not bad:
    print("  ✅ 三维度无 modded 独有问题")

sys.exit(1 if bad else 0)
