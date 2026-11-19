"""第 38 轮：图片缺失对比 —— 52 个缺失是否原版也有。"""
import html
import re
import sys
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"


def load(p):
    z = zipfile.ZipFile(p)
    raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    files = set(n.replace("assets/www/", "") for n in z.namelist())
    return html.unescape(raw), files


mg, mfiles = load(APK)
vg, vfiles = load(VAN)


def imgpaths(g):
    return set(re.findall(r"img/[a-zA-Z0-9_/\-]+\.(?:png|jpg|jpeg|gif|webp)", g))


mi = imgpaths(mg)
vi = imgpaths(vg)

mm = [p for p in mi if p not in mfiles]
vm = [p for p in vi if p not in vfiles]

print("=" * 90)
print("图片缺失对比")
print("=" * 90)
print(f"  modded: 引用 {len(mi)}，缺失 {len(mm)}")
print(f"  vanilla: 引用 {len(vi)}，缺失 {len(vm)}")

only_m = sorted(set(mm) - set(vm))
only_v = sorted(set(vm) - set(mm))
print(f"\n  modded 独有缺失 {len(only_m)}:")
for p in only_m[:20]:
    print(f"    {p}")

print(f"\n  vanilla 独有缺失 {len(only_v)}: {only_v[:10]}")

# 检查这些「缺失」是不是动态拼接的
print("\n" + "=" * 90)
print("验证：这些路径是否动态拼接（源码里有模板）")
print("=" * 90)
for p in only_m[:5]:
    base = p.rsplit("/", 1)[-1].replace(".png", "")
    # 找源码里的模板
    pats = [
        rf"img/[^\"']*\${{?[^\"']*{re.escape(base[:6])}",
        rf"{re.escape(base[:8])}[^\"']*\$\{{",
    ]
    found = False
    for pat in pats:
        m = re.search(pat, mg)
        if m:
            print(f"  {p}")
            print(f"    → 动态模板 {mg[max(0,m.start()-80):m.start()+120]!r}")
            found = True
            break
    if not found:
        # 找同名片段
        m = re.search(re.escape(base[:10]), mg)
        if m:
            print(f"  {p}")
            print(f"    → 源码片段 {mg[max(0,m.start()-100):m.start()+100]!r}")
        else:
            print(f"  {p}  → 源码里无痕迹（可能是 JS 动态生成）")

print("\n" + "=" * 90)
print("结论")
print("=" * 90)
if only_m:
    print(f"  ⚠️ modded 独有缺失 {len(only_m)} 个（需逐个人工确认是否动态生成）")
else:
    print("  ✅ 无 modded 独有缺失")
    sys.exit(0)
sys.exit(0)
