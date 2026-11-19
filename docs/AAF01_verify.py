"""验证 setup 函数 + 查 rngWraith/wPersist/wHunt 宏。"""
import html
import re
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"

g = html.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))

vz = zipfile.ZipFile(VAN)
vg = html.unescape(vz.read("assets/www/index.html").decode("utf-8", "replace"))

print("=" * 88)
print("1) setup 函数定义（st.xxx =）")
print("=" * 88)
for fn in ["description_CN", "NPC_CN_TOOLNAME", "NPC_CN_TYPE", "NPC_CN_NAME",
           "NPC_CN_TITLE", "BODYPARTS_CN_NAME", "CAFE_FOOD_CN", "DirectionCN",
           "brothelshowType_CN", "update_cloth_cn", "descriptionCN"]:
    v = f"st.{fn} =" in g or f"s.{fn} =" in g
    print(f"  {fn}: {'✅' if v else '❌'}")

print("\n" + "=" * 88)
print("2) 5 个 <<script>> 的完整开头（确认守卫）")
print("=" * 88)
for i, m in enumerate(re.finditer(r"<<script>>", g), 1):
    seg = g[m.end():m.end() + 260]
    if "typeof setup" in seg or "st." in seg[:200]:
        print(f"  [{i}] {seg[:250]!r}")
        print()

print("=" * 88)
print("3) rngWraith / wPersist / wHunt 宏定义")
print("=" * 88)
for macro in ["rngWraith", "wPersist", "wHunt", "wTimerProgress", "speechWraith"]:
    md = len(re.findall(r'<<widget\s+"' + macro + r'"', g))
    vd = len(re.findall(r'<<widget\s+"' + macro + r'"', vg))
    usage = len(re.findall(r"<<" + macro + r"\b", g))
    print(f"  {macro}: modded 定义 {md} / vanilla {vd} / 调用 {usage}")

print("\n" + "=" * 88)
print("4) 这些宏在 vanilla 里定义在哪个 passage")
print("=" * 88)
for macro in ["rngWraith", "wPersist", "wHunt"]:
    for m in re.finditer(r'<<widget\s+"' + macro + r'"', vg):
        # 往前找 passage 名
        head = vg[:m.start()]
        pm = list(re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"', vg))
        last = None
        for x in pm:
            if x.start() < m.start():
                last = x
            else:
                break
        print(f"  vanilla {macro} @ passage {last.group(1) if last else '?'}")

print("\n" + "=" * 88)
print("5) modded 里这些宏是否在某 passage 内（可能被吞进 script）")
print("=" * 88)
for macro in ["rngWraith", "wPersist", "wHunt"]:
    idx = g.find(f'<<widget "{macro}"')
    print(f"  {macro}: {'找到 @' + str(idx) if idx > 0 else '❌ 找不到定义'}")
    if idx > 0:
        print(f"    上下文: {g[max(0,idx-150):idx+150]!r}")
