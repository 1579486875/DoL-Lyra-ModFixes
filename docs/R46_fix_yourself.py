"""第 46 轮：修 === "你自己" + 查 penisdesc 的来源。"""
import html
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"


def load(p):
    import zipfile
    z = zipfile.ZipFile(p)
    return html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))


mg = load(APK)
vg = load(VAN)

print("=" * 88)
print("1) penisdesc 的来源")
print("=" * 88)
for label, g in (("modded", mg), ("vanilla", vg)):
    print(f"\n[{label}]")
    # foreskin / strapon 等描述
    for pat in [r'penisdesc\s*[:=]\s*"([^"]+)"', r'"strapon"']:
        hits = re.findall(pat, g)
        print(f"  {pat}: {hits[:8]}  (共 {len(hits)})")
    # 找 penisdesc 表
    m = re.search(r"(?:setup\.)?penisdesc\w*\s*=\s*[\[\{](.{0,600})", g)
    if m:
        print(f"  表: {m.group(0)[:650]!r}")

print("\n" + "=" * 88)
print("2) 'strapon' / '穿戴式' 两边的出现次数")
print("=" * 88)
for label, g in (("modded", mg), ("vanilla", vg)):
    print(f"  {label}: 'strapon' {g.count('strapon')} / '穿戴式' {g.count('穿戴式')}")

print("\n" + "=" * 88)
print("3) === \"你自己\" 现状")
print("=" * 88)
data = open(HTML, "rb").read().decode("utf-8", "replace")
g = H.unescape(data)
for m in re.finditer(r'===\s*"你自己"', g):
    print(f"  @{m.start()}: {g[max(0,m.start()-150):m.start()+150]!r}")

print("\n" + "=" * 88)
print("4) 修复 === \"你自己\" -> \"Yourself\"")
print("=" * 88)
total = 0
for old, new in [('=== "你自己"', '=== "Yourself"')]:
    for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
        if a in data:
            n = data.count(a)
            data = data.replace(a, b)
            total += n
            print(f"  ✅ {old} -> {new}  ({n} 处)")
            break

if total:
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"  已写回 {total} 处")

# 校验
g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
print(f"\n  残留 === \"你自己\": {len(re.findall(chr(61)*3 + chr(32) + chr(34) + '你自己', g2))}")

print("\n" + "=" * 88)
print("5) penisdesc 候选值（决定 includes(\"穿戴式\") 是否正确）")
print("=" * 88)
# 找 setup.penisdesc 或类似
for pat in [r"penisdesc", r"strapon"]:
    for m in list(re.finditer(pat, mg))[:3]:
        ctx = mg[max(0, m.start() - 200):m.start() + 200]
        if ":" in ctx or "=" in ctx:
            print(f"  {ctx!r}")

sys.exit(0)
