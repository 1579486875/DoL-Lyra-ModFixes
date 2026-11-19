"""第 13 轮：DOM 选择器问题归属（vanilla 对照）。"""
import html
import re
import zipfile
from collections import Counter

MODDED = r"E:\TAML\_dol\work\index_modded6.html"
VANILLA = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"


def load(path):
    if path.endswith(".apk"):
        z = zipfile.ZipFile(path)
        raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    else:
        raw = open(path, "rb").read().decode("utf-8", "replace")
    return html.unescape(raw)


mg = load(MODDED)
vg = load(VANILLA)


def audit(g):
    ids = set(re.findall(r'\bid="([^"]+)"', g))
    sel = Counter()
    for tag in ("replace", "append", "prepend", "remove"):
        for m in re.finditer(r"<<" + tag + r"\b", g):
            i = m.end()
            depth = 1
            while i < len(g) and depth > 0:
                if g.startswith("<<", i):
                    depth += 1
                    i += 2
                elif g.startswith(">>", i):
                    depth -= 1
                    i += 2
                else:
                    i += 1
            s = g[m.end():i - 2].split(">>")[0].strip()
            if s:
                sel[s] += 1
    miss = set()
    for s in sel:
        m = re.fullmatch(r"#([\w\-]+)", s)
        if m and m.group(1) not in ids:
            miss.add(s)
    jq = Counter(re.findall(r"""\$\(\s*['"]#([\w\-]+)['"]\s*\)""", g))
    jq_miss = {i for i in jq if i not in ids}
    return sel, miss, jq_miss


ms, mm, mj = audit(mg)
vs, vm, vj = audit(vg)

print("=" * 94)
print("第 13 轮：DOM 选择器问题归属")
print("=" * 94)
print(f"  <<replace>>等 选择器: modded {len(ms)} / vanilla {len(vs)}")
print(f"  找不到目标的:      modded {len(mm)} / vanilla {len(vm)}")
print(f"  modded 独有: {sorted(mm - vm)}")
print(f"  vanilla 独有: {sorted(vm - mm)}")

print(f"\n  jQuery #id 未定义: modded {len(mj)} / vanilla {len(vj)}")
print(f"  modded 独有: {sorted(mj - vj)[:15]}")
print(f"  vanilla 独有: {sorted(vj - mj)[:15]}")
