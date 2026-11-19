"""轮15：修 wardrobe locker 判断 + 全量扫描 .name.includes("中文") 同类。"""
import html
import html as H
import re
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"
CJK = re.compile(r"[\u4e00-\u9fff]")


def load_apk(p):
    z = zipfile.ZipFile(p)
    return html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))


mg = load_apk(APK)
vg = load_apk(VAN)

print("=" * 90)
print("全量扫描 .name.includes / .variable.includes 的中文值")
print("=" * 90)
PAT = re.compile(r'\.(name|variable|fullDescription|fullDesc|desc|type|category)\.includes\(\s*"([^"]*)"\s*\)')
for label, g in (("modded", mg), ("vanilla", vg)):
    print(f"\n[{label}]")
    for m in PAT.finditer(g):
        attr, val = m.group(1), m.group(2)
        if CJK.search(val):
            print(f"  {attr}.includes({val!r}) @{m.start()}")
            print(f"    {g[max(0,m.start()-140):m.start()+160]!r}")

print("\n" + "=" * 90)
print("修复")
print("=" * 90)
data = open(HTML, "rb").read().decode("utf-8", "replace")
g = H.unescape(data)

FIXES = [
    ('wardrobes[_locationName].name.includes("更衣室")',
     'wardrobes[_locationName].name.includes("locker")'),
    ('$wardrobes[_locationName].name.includes("更衣室")',
     '$wardrobes[_locationName].name.includes("locker")'),
]

total = 0
for old, new in FIXES:
    for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
        if a in data:
            n = data.count(a)
            data = data.replace(a, b)
            total += n
            print(f"  ✅ {old[:60]} -> {new[:60]}  ({n} 处)")
            break
    if total:
        break

if not total:
    # 正则兜底
    pat = re.compile(r'(wardrobes\[[^\]]+\]\.name\.includes\()"更衣室"(\))')
    if pat.search(g):
        new_g = pat.sub(r'\1"locker"\2', g)
        data = H.escape(new_g, quote=False)
        total = 1
        print("  ✅ 正则修复 1 处")

if total:
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"\n共修 {total} 处")

# 校验
g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
print("\n=== 校验 ===")
print(f"  wardrobes 更衣室 残留: {g2.count(chr(34)+'更衣室'+chr(34))}")
print(f"  wardrobes locker: {g2.count('name.includes(' + chr(34) + 'locker' + chr(34) + ')')}")

# 加入 ZZ01 守卫
ZZ = r"E:\TAML\_dol\work\ZZ01_final_guard.py"
s = open(ZZ, encoding="utf-8").read()
if "locker" not in s:
    OLD = '''    ("11. Yourself 判断",'''
    NEW = '''    ("11b. wardrobe locker 判断",
     [('wardrobes[_locationName].name.includes("更衣室")',
       'wardrobes[_locationName].name.includes("locker")')],
     lambda g: 'name.includes("更衣室")' not in g),

    ("11. Yourself 判断",'''
    if OLD in s:
        s = s.replace(OLD, NEW, 1)
        open(ZZ, "w", encoding="utf-8").write(s)
        print("\n  ✅ 已加入 ZZ01 守卫")

sys.exit(0 if total else 1)
