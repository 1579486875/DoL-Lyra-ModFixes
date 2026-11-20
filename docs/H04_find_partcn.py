"""H04：找 partCN / BODYPARTS / tr 的定义，制定彻底修复方案。"""
import html as H
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
raw = zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace")
g = H.unescape(raw)

print("=" * 95)
print("1. partCN 定义")
print("=" * 95)
for m in re.finditer(r"function partCN\s*\(", g):
    print(f"\n@{m.start()}")
    print(f"  {g[max(0, m.start() - 200):m.start() + 400]!r}")

print("\n" + "=" * 95)
print("2. BODYPARTS 表定义")
print("=" * 95)
for m in re.finditer(r"(?:var|const|let)\s+BODYPARTS\s*=", g):
    print(f"\n@{m.start()}")
    seg = g[m.start():m.start() + 2000]
    print(f"  {seg[:800]!r}")
    # 数键
    j = g.find("};", m.start())
    body = g[m.start():j + 2]
    pairs = dict(re.findall(r'"?([A-Za-z_][A-Za-z0-9_ ]*)"?\s*:\s*"([^"]*)"', body))
    print(f"  {len(pairs)} 键")
    for kw in ("penis", "vagina", "anus", "breasts", "tongue", "buttocks", "wings", "hand"):
        print(f"    {'OK ' if kw in pairs else 'MISS'} {kw:<10} = {pairs.get(kw)!r}")

print("\n" + "=" * 95)
print("3. tr() 定义")
print("=" * 95)
for m in re.finditer(r"function tr\s*\(", g):
    print(f"\n@{m.start()}")
    print(f"  {g[max(0, m.start() - 100):m.start() + 600]!r}")

print("\n" + "=" * 95)
print("4. 所有给 setup.BODYPARTS_CN_NAME 赋值的位置（含 partCN）")
print("=" * 95)
for m in re.finditer(r"BODYPARTS_CN_NAME\s*[=:]\s*(?:partCN|function|mk)", g):
    print(f"  @{m.start()}: {g[max(0,m.start()-80):m.start()+120]!r}")
