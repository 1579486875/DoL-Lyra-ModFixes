"""Z01（第8轮）：模组完整性审计 —— boot.json 引用的文件是否都存在。

检查项：
  1. scriptFileList / tweeFileList / styleFileList / imgFileList 列出的文件是否存在
  2. TweeReplacerAddon 的 replaceFile 是否存在
  3. addonPlugin 的 modName 指向的模组是否已安装
  4. 模组依赖（dependencies）是否满足
"""
import base64
import html as H
import io
import json
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
z = zipfile.ZipFile(APK)
g = H.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))

m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", g, re.S)
parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m.group(1))

mods = []
for s in parts:
    raw = base64.b64decode(re.sub(r"\s+", "", s))
    if raw[:2] != b"PK":
        continue
    try:
        zz = zipfile.ZipFile(io.BytesIO(raw))
        bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
    except Exception:
        continue
    mods.append((bj.get("name", "?"), bj, zz))

names = {n for n, _, _ in mods}
print(f"模组总数: {len(mods)}")

print("\n" + "=" * 95)
print("1. 文件清单里缺失的文件")
print("=" * 95)
LIST_KEYS = ("scriptFileList", "tweeFileList", "styleFileList", "imgFileList")
total_miss = 0
for modname, bj, zz in mods:
    files = set(zz.namelist())
    miss = []
    for key in LIST_KEYS:
        for f in (bj.get(key) or []):
            if f not in files:
                miss.append((key, f))
    if miss:
        total_miss += len(miss)
        print(f"\n  [{modname}] 缺 {len(miss)} 个")
        for key, f in miss[:8]:
            print(f"    {key}: {f!r}")
        if len(miss) > 8:
            print(f"    ... 还有 {len(miss) - 8}")
print(f"\n  合计缺失: {total_miss}")

print("\n" + "=" * 95)
print("2. TweeReplacerAddon 的 replaceFile 是否存在")
print("=" * 95)
n2 = 0
miss2 = []
for modname, bj, zz in mods:
    files = set(zz.namelist())
    for a in (bj.get("addonPlugin") or []):
        if not isinstance(a, dict) or a.get("addonName") != "TweeReplacerAddon":
            continue
        for p in (a.get("params") or []):
            if not isinstance(p, dict):
                continue
            rf = p.get("replaceFile")
            if not isinstance(rf, str):
                continue
            n2 += 1
            if rf not in files:
                miss2.append((modname, p.get("passage", "")[:30], rf))
print(f"  共 {n2} 条 replaceFile")
print(f"  缺失: {len(miss2)}")
for mod, psg, rf in miss2[:15]:
    print(f"    [{mod}] {psg!r}  {rf!r}")

print("\n" + "=" * 95)
print("3. addonPlugin 的 modName 指向的模组是否存在")
print("=" * 95)
n3 = 0
miss3 = []
for modname, bj, zz in mods:
    for a in (bj.get("addonPlugin") or []):
        if not isinstance(a, dict):
            continue
        mn = a.get("modName")
        if not mn:
            continue
        n3 += 1
        if mn not in names:
            miss3.append((modname, a.get("addonName", "?"), mn))
print(f"  共 {n3} 条 addon 引用")
print(f"  指向不存在的模组: {len(miss3)}")
for a, b, c in miss3[:15]:
    print(f"    [{a}] {b!r} -> {c!r}")

print("\n" + "=" * 95)
print("4. 模组依赖是否满足")
print("=" * 95)
n4 = 0
miss4 = []
for modname, bj, zz in mods:
    deps = bj.get("dependencies") or {}
    if not isinstance(deps, dict):
        continue
    for dep in deps:
        n4 += 1
        if dep not in names:
            miss4.append((modname, dep))
print(f"  共 {n4} 条依赖")
print(f"  不满足: {len(miss4)}")
for a, b in miss4[:15]:
    print(f"    [{a}] 需要 {b!r}")

print("\n" + "=" * 95)
print("汇总")
print("=" * 95)
print(f"  文件清单缺失:      {total_miss}")
print(f"  replaceFile 缺失:  {len(miss2)} / {n2}")
print(f"  addon 引用失效:    {len(miss3)} / {n3}")
print(f"  依赖不满足:        {len(miss4)} / {n4}")
