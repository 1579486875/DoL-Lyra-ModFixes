"""第 32 轮：setup 表键对比 —— 找 modded 缺失/新增的 setup 键。"""
import html
import re
import sys
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"


def load(p):
    z = zipfile.ZipFile(p)
    return html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))


def setup_keys(g):
    keys = set()
    # setup.xxx = / setup["xxx"] = / setup.xxx to
    keys |= set(re.findall(r"setup\.([A-Za-z_$][\w$]*)\s*=", g))
    keys |= set(re.findall(r'setup\["([^"]+)"\]\s*=', g))
    keys |= set(re.findall(r"setup\.([A-Za-z_$][\w$]*)\s+to\s", g))
    return keys


def setup_refs(g):
    """所有被读取的 setup.xxx"""
    return set(re.findall(r"setup\.([A-Za-z_$][\w$]*)", g))


mg = load(APK)
vg = load(VAN)

md = setup_keys(mg)
vd = setup_keys(vg)
mr = setup_refs(mg)
vr = setup_refs(vg)

print("=" * 90)
print("setup 键")
print("=" * 90)
print(f"  定义: modded {len(md)} / vanilla {len(vd)}")
print(f"  引用: modded {len(mr)} / vanilla {len(vr)}")

only_m = sorted(md - vd)
only_v = sorted(vd - md)
print(f"\n  modded 独有定义 {len(only_m)}: {only_m[:30]}")
print(f"  vanilla 独有定义 {len(only_v)}: {only_v[:30]}")

print("\n" + "=" * 90)
print("引用但没定义（可能是运行时动态加的）")
print("=" * 90)
undef_m = sorted(mr - md - vd)
undef_v = sorted(vr - vd - md)
print(f"  modded 引用但未定义: {len(undef_m)}")
for k in undef_m[:20]:
    # 找引用处
    m = re.search(r"setup\." + re.escape(k), mg)
    ctx = mg[max(0, m.start() - 80):m.start() + 80] if m else ""
    print(f"    {k:<28} {ctx[:100]!r}")

print(f"\n  vanilla 引用但未定义: {len(undef_v)}")

only_undef = set(undef_m) - set(undef_v)
print(f"\n  modded 独有未定义: {sorted(only_undef) if only_undef else '无'}")

# 关键函数检查
print("\n" + "=" * 90)
print("关键 setup 函数")
print("=" * 90)
CRITICAL = ["description_CN", "NPC_CN_TOOLNAME", "NPC_CN_TYPE", "NPC_CN_NAME",
            "NPC_CN_TITLE", "BODYPARTS_CN_NAME", "CAFE_FOOD_CN", "DirectionCN",
            "brothelshowType_CN", "update_cloth_cn", "__cnLockCount", "__descCNInstalled"]
for k in CRITICAL:
    a = k in md or k in mr
    b = k in vd or k in vr
    print(f"  {k:<24} modded {'✅' if a else '❌'}  vanilla {'✅' if b else '❌'}")

sys.exit(1 if only_undef else 0)
