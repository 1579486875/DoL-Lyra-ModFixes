"""验证 penisdesc / genitals.name 等被中文比较的字段，其值到底是中文还是英文。"""
import html
import re
import zipfile

MOD = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"


def load(p):
    z = zipfile.ZipFile(p)
    raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    return html.unescape(raw)


mg = load(MOD)
vg = load(VAN)

FIELDS = ["penisdesc", "genitals.name", "genitals.type", "condom", "namecap"]

print("=" * 94)
print("1) penisdesc 的赋值来源")
print("=" * 94)
for label, g in (("vanilla", vg), ("modded", mg)):
    print(f"\n--- {label} ---")
    # 找 penisdesc 被赋值的字面量
    assigns = sorted(set(re.findall(r"penisdesc\s*(?:to|=)\s*[\"']([^\"']{1,40})[\"']", g)))
    print(f"  直接赋值: {assigns[:15]}")
    # 找 <<set ... penisdesc to ...>>
    for m in list(re.finditer(r"penisdesc\s*(?:to|=)\s*([^>\n]{1,80})", g))[:8]:
        print(f"    {m.group(0)[:100]!r}")

print("\n" + "=" * 94)
print("2) '穿戴式' 在 vanilla 里的对应写法")
print("=" * 94)
for kw in ["穿戴式", "strapped on", "strapon", "strapped"]:
    print(f"  {kw!r}: modded {mg.count(kw)}  vanilla {vg.count(kw)}")

print("\n" + "=" * 94)
print("3) 找 setup 里定义 penisdesc 的地方")
print("=" * 94)
for m in list(re.finditer(r"penisdesc", vg))[:5]:
    print(f"  vanilla @{m.start()}: {vg[max(0,m.start()-180):m.start()+180]!r}")
    print()

print("=" * 94)
print("4) 中文比较值的完整分类统计")
print("=" * 94)
CJK = re.compile(r"[\u4e00-\u9fff]")
from collections import Counter
c = Counter()
for m in re.finditer(r'<<(?:if|elseif|unless|while)\s+([^\n>]{1,300})>>', mg):
    expr = m.group(1)
    for lit in re.findall(r'"([^"]{1,50})"', expr):
        if CJK.search(lit):
            c[lit] += 1
print(f"  不同的中文值: {len(c)}")
for val, n in c.most_common(25):
    print(f"    {n:>3}  {val!r}")
