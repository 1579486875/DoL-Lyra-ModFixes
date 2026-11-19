"""验证 SugarCube.setup vs window.setup。"""
import html
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"


def load(p):
    z = zipfile.ZipFile(p)
    return html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))


mg = load(APK)
vg = load(VAN)

print("=" * 88)
print("SugarCube.setup 用法统计")
print("=" * 88)
for label, g in (("modded", mg), ("vanilla", vg)):
    n1 = len(re.findall(r"SugarCube\.setup", g))
    n2 = len(re.findall(r"window\.setup\b", g))
    n3 = len(re.findall(r"(?<![\w.])setup\.", g))
    print(f"  {label}: SugarCube.setup {n1}  window.setup {n2}  裸 setup. {n3}")

print("\n" + "=" * 88)
print("vanilla 里 SugarCube.setup 的上下文（如果存在）")
print("=" * 88)
for m in list(re.finditer(r"SugarCube\.setup", vg))[:5]:
    print(f"  {vg[max(0,m.start()-200):m.start()+200]!r}")
    print()

print("=" * 88)
print("modded 里 SugarCube.setup 的上下文")
print("=" * 88)
for m in list(re.finditer(r"SugarCube\.setup", mg))[:8]:
    print(f"  {mg[max(0,m.start()-200):m.start()+200]!r}")
    print()

print("=" * 88)
print("vanilla 里如何定义 setup 函数（示例）")
print("=" * 88)
for m in list(re.finditer(r"<<script>>", vg))[:3]:
    seg = vg[m.start():m.start()+400]
    print(f"  {seg!r}")
    print()

print("=" * 88)
print("vanilla 里 setup.xxx = 的写法")
print("=" * 88)
hits = re.findall(r"(window\.)?setup\.(\w+)\s*=\s*function", vg)
from collections import Counter
print(f"  {len(hits)} 处: {Counter(h[1] for h in hits).most_common(10)}")
# 看几个上下文
for m in list(re.finditer(r"(?:window\.)?setup\.(\w+)\s*=\s*function", vg))[:3]:
    print(f"\n  {vg[max(0,m.start()-250):m.start()+150]!r}")
