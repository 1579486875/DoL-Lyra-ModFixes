"""H02：完整提取 BODYPARTS_CN_NAME 的所有定义形式与内容。"""
import html as H
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
raw = zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace")
g = H.unescape(raw)

print("=" * 95)
print("1. 搜所有「BODYPARTS_CN_NAME = 」形式（不限定前缀）")
print("=" * 95)
for m in re.finditer(r"BODYPARTS_CN_NAME\s*=", g):
    print(f"\n@{m.start()}")
    print(f"  {g[max(0, m.start() - 60):m.start() + 200]!r}")

print("\n" + "=" * 95)
print("2. mk({...}) 的完整表内容")
print("=" * 95)
i = g.find("st.BODYPARTS_CN_NAME = mk({")
if i > 0:
    # 找匹配的 })
    j = i + len("st.BODYPARTS_CN_NAME = mk({")
    depth = 1
    while j < len(g) and depth > 0:
        if g[j] == "{":
            depth += 1
        elif g[j] == "}":
            depth -= 1
        j += 1
    body = g[i:j + 2]
    print(f"  长度 {len(body)}")
    pairs = re.findall(r'"([^"]+)"\s*:\s*"([^"]*)"', body)
    d = {}
    for k, v in pairs:
        d[k] = v
    print(f"  {len(d)} 键")
    for kw in ("penis", "vagina", "anus", "breasts", "tongue", "buttocks", "wings",
               "hand", "foot", "mouth", "thigh", "leg", "arm"):
        print(f"    {'✅' if kw in d else '❌'} {kw:<10} = {d.get(kw)!r}")

print("\n" + "=" * 95)
print("3. __PB 内联表")
print("=" * 95)
i2 = g.find("var __PB = {")
if i2 > 0:
    j2 = g.find("};", i2)
    body2 = g[i2:j2 + 2]
    pairs2 = dict(re.findall(r'"([^"]+)"\s*:\s*"([^"]*)"', body2))
    print(f"  {len(pairs2)} 键")
    for kw in ("penis", "vagina", "anus", "breasts", "tongue", "buttocks", "wings"):
        print(f"    {'✅' if kw in pairs2 else '❌'} {kw:<10} = {pairs2.get(kw)!r}")
    print(f"\n  完整定义: {g[max(0,i2-150):j2+150]!r}")
else:
    print("  ❌ 找不到 __PB")

print("\n" + "=" * 95)
print("4. 代码顺序（谁最后执行）")
print("=" * 95)
pos_mk = g.find("st.BODYPARTS_CN_NAME = mk({")
pos_pb = g.find("var __PB = {")
pos_fn = g.find("BODYPARTS_CN_NAME = function (x)")
print(f"  mk 定义      @{pos_mk}")
print(f"  __PB 表      @{pos_pb}")
print(f"  function 定义@{pos_fn}")

if pos_mk > 0 and pos_fn > 0:
    print(f"\n  顺序: {'function 在后（覆盖 mk）' if pos_fn > pos_mk else 'mk 在后（覆盖 function）'}")
