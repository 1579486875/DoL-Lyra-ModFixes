"""第 21 轮：确认断链是原版就有，还是我引入的。

对照 vanilla 包（Lyra 官方原包）与当前 modded 包。
"""
import html
import re
import zipfile

VANILLA = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"
MODDED = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"

SUSPECTS = [
    "Estate Manor Intro Entrance",
    "Mansion Intro 9 Push",
    "School Boy's Toilets",
    "Renderer Test Page",
]


def load(apk):
    z = zipfile.ZipFile(apk)
    raw = z.read("assets/www/index.html")
    names = set(html.unescape(x) for x in re.findall(r'<tw-passagedata[^>]*name="([^"]+)"', raw.decode("utf-8", "replace")))
    g = html.unescape(raw.decode("utf-8", "replace"))
    return names, g


print("加载 vanilla ...")
vnames, vg = load(VANILLA)
print(f"  passage: {len(vnames)}")
print("加载 modded ...")
mnames, mg = load(MODDED)
print(f"  passage: {len(mnames)}")

print("\n" + "=" * 94)
print("断链归属")
print("=" * 94)
for s in SUSPECTS:
    inv = s in vnames
    inm = s in mnames
    # 在原文里被链接几次
    vlink = len(re.findall(re.escape(s), vg))
    mlink = len(re.findall(re.escape(s), mg))
    print(f"  {s!r}")
    print(f"     passage 存在: vanilla={inv}  modded={inm}")
    print(f"     出现次数    : vanilla={vlink}  modded={mlink}")
    print(f"     → {'原版遗留' if (not inv and vlink) else '本次引入' if (not inm and mlink and inv) else '正常' if inm else '未知'}")
    print()

print("=" * 94)
print("对照：如果 modded 有断链而 vanilla 没有，才是我的锅")
print("=" * 94)
# 全量对比：modded 里被链接但不存在、且 vanilla 里存在该 passage 的
def broken(g, names):
    out = set()
    for label, target in re.findall(r"\[\[([^\]|]+)\|([^\]]+)\]\]", g):
        t = target.strip()
        if t.startswith("$") or t.startswith("_") or "<<" in t or t.startswith('"') or t.startswith("`"):
            continue
        if t not in names:
            out.add(t)
    return out


vb = broken(vg, vnames)
mb = broken(mg, mnames)
print(f"  vanilla 断链: {len(vb)} 种")
print(f"  modded  断链: {len(mb)} 种")
new_broken = mb - vb
print(f"\n  modded 独有（可能是本次引入）: {len(new_broken)} 种")
for x in sorted(new_broken)[:20]:
    print(f"    {x!r}")
