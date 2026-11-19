"""验证最终 APK 里的 setup 守卫。"""
import html
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
z = zipfile.ZipFile(APK)
g = html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))

print("=" * 88)
print("1) SugarCube.setup 残留（应为 0，除了注释）")
print("=" * 88)
n = 0
for m in re.finditer(r"SugarCube\.setup", g):
    ctx = g[max(0, m.start() - 70):m.start() + 70]
    if "Can be found at" in ctx:
        continue
    n += 1
    print(f"  ❌ {ctx!r}")
print(f"  非注释残留: {n}")

print("\n" + "=" * 88)
print("2) var st = st 自赋值（应为 0）")
print("=" * 88)
print(f"  {g.count('var st = st')}")

print("\n" + "=" * 88)
print("3) 所有 <<script>> 的开头（确认守卫形态）")
print("=" * 88)
for i, m in enumerate(re.finditer(r"<<script>>", g), 1):
    seg = g[m.end():m.end() + 200].replace("\n", " ")
    if "typeof setup" in seg or "SugarCube" in seg:
        print(f"  [{i}] {seg[:180]!r}")

print("\n" + "=" * 88)
print("4) 关键 setup 函数定义")
print("=" * 88)
for fn in ["description_CN", "NPC_CN_TOOLNAME", "NPC_CN_TYPE", "NPC_CN_NAME",
           "CAFE_FOOD_CN", "DirectionCN", "brothelshowType_CN", "update_cloth_cn"]:
    print(f"  st.{fn}: {'✅' if (f'st.{fn} =' in g or f's.{fn} =' in g) else '❌'}")

print("\n" + "=" * 88)
print("5) <<= <<= 嵌套残留")
print("=" * 88)
print(f"  {len(re.findall(r'<<=\s*[^>]{0,80}<<=', g))}")

print("\n" + "=" * 88)
print("6) eels / lizard / whale 的映射")
print("=" * 88)
m2 = re.search(r'setup\.NPCTypeList_cn_name to "([^"]{0,4000})"', g)
if m2:
    t = m2.group(1)
    for w in ["eels", "lizard", "whale"]:
        print(f"  {w}: {'✅' if w + ',' in t else '❌'}")

print("\n" + "=" * 88)
print("7) Makeup 残留")
print("=" * 88)
print(f"  {g.count('Makeup')} 次")
for m in list(re.finditer("Makeup", g))[:3]:
    print(f"    {g[max(0,m.start()-100):m.start()+80]!r}")
