"""第 45 轮：查剩余的「中文数据值」判断是否正确。"""
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

print("=" * 90)
print("1) $earSlime.event 的候选值来源（$slimeEvent）")
print("=" * 90)
for label, g in (("modded", mg), ("vanilla", vg)):
    print(f"\n[{label}]")
    # 找 slimeEvent 的赋值
    for m in list(re.finditer(r"\$slimeEvent\s+to\s+([^\n>]{0,200})", g))[:5]:
        print(f"  {m.group(0)[:220]!r}")
    # 找 earSlime 事件表
    for m in list(re.finditer(r"(?:slimeEvents?|earSlimeEvents?)\s*=\s*\[", g))[:2]:
        print(f"  事件表 @{m.start()}: {g[m.start():m.start()+400]!r}")

print("\n" + "=" * 90)
print("2) pregnancyNameCorrection 的返回值")
print("=" * 90)
for label, g in (("modded", mg), ("vanilla", vg)):
    print(f"\n[{label}]")
    for m in list(re.finditer(r"(?:function\s+)?pregnancyNameCorrection", g))[:3]:
        print(f"  @{m.start()}: {g[max(0,m.start()-50):m.start()+600]!r}")

print("\n" + "=" * 90)
print("3) .includes(\"中文\") 的 81 处 —— 看是否同时检查英文")
print("=" * 90)
pat = re.compile(r'\.includes\(\s*"([^"]*[\u4e00-\u9fff][^"]*)"\s*\)')
hits = list(pat.finditer(mg))
print(f"  共 {len(hits)} 处")
compat = 0
incompat = []
for m in hits:
    to = m.group(1)
    # 看前后 200 字符里有没有 .includes("英文")
    ctx = mg[max(0, m.start() - 200):m.start() + 400]
    if re.search(r'\.includes\(\s*"[A-Za-z]', ctx):
        compat += 1
    else:
        incompat.append((to, m.start(), ctx[:250]))

print(f"  同时检查英文（兼容）: {compat}")
print(f"  只检查中文（可疑）: {len(incompat)}")
for to, pos, ctx in incompat[:12]:
    print(f"\n    {to!r} @{pos}")
    print(f"      {ctx!r}")

print("\n" + "=" * 90)
print("4) 其他中文 === / is 判断（排除已修的）")
print("=" * 90)
pat2 = re.compile(r'(?:\$[\w.\[\]]+|_[\w]+)\s+(?:is|isnot|===|!==)\s+"([^"]*[\u4e00-\u9fff][^"]*)"')
hits2 = list(pat2.finditer(mg))
print(f"  共 {len(hits2)} 处")
from collections import Counter
c = Counter(m.group(1) for m in hits2)
for v, n in c.most_common(20):
    print(f"    {n:>3}× {v!r}")
