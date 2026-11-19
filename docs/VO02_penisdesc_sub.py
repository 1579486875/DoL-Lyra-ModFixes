"""查 penisdesc 的英文子串判断是否在中文值下失效。"""
import html
import re
import zipfile

MOD = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"


def load(p):
    z = zipfile.ZipFile(p)
    return html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))


mg = load(MOD)
vg = load(VAN)

print("=" * 94)
print("1) penisdesc.includes / .is 的所有判断")
print("=" * 94)
for label, g in (("vanilla", vg), ("modded", mg)):
    print(f"\n--- {label} ---")
    pats = set()
    for m in re.finditer(r"penisdesc\s*\.\s*(includes|is|===|indexOf)\s*\(?\s*[\"']([^\"']{1,30})[\"']", g):
        pats.add((m.group(1), m.group(2)))
    for method, val in sorted(pats):
        print(f"  .{method}({val!r})")

print("\n" + "=" * 94)
print("2) vanilla 里 penisdesc 的完整取值（_pd 数组）")
print("=" * 94)
for m in list(re.finditer(r"_pd\s*(?:to|=)\s*\[([^\]]{1,600})\]", vg))[:3]:
    print(f"  {m.group(1)[:500]!r}")
    print()

print("=" * 94)
print("3) modded 里同样的数组")
print("=" * 94)
for m in list(re.finditer(r"_pd\s*(?:to|=)\s*\[([^\]]{1,600})\]", mg))[:3]:
    print(f"  {m.group(1)[:500]!r}")
    print()

print("=" * 94)
print("4) 关键子串在两边是否存在")
print("=" * 94)
for kw in ["horse", "knotted", "canine", "strapped", "穿戴式", "马", "打结"]:
    print(f"  {kw!r}: modded {mg.count(kw):>4}  vanilla {vg.count(kw):>4}")
