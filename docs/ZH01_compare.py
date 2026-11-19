"""对比 modded vs vanilla 的「widget 参数不足」和「switch case 重复」。"""
import html
import re
import zipfile
from collections import Counter

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"


def load(p):
    z = zipfile.ZipFile(p)
    return html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))


mg = load(APK)
vg = load(VAN)


def param_mismatch(g):
    wdefs = {}
    for m in re.finditer(r'<<widget\s+"([^"]+)"\s*>>(.*?)<</widget>>', g, re.S):
        name, body = m.group(1), m.group(2)
        idxs = [int(x) for x in re.findall(r"_args\[(\d+)\]", body)]
        wdefs[name] = max(idxs) + 1 if idxs else 0
    out = set()
    for name, need in wdefs.items():
        if not need:
            continue
        for cm in re.finditer(r"<<" + re.escape(name) + r"((?:\s+[^>]{1,80})?)>>", g):
            argstr = cm.group(1).strip()
            if not argstr:
                continue
            cnt = len(re.findall(r'(?:"[^"]*"|\'[^\']*\'|[^\s]+)', argstr))
            if cnt < need and not any(x in argstr for x in ("$", "_", "(", "[")):
                out.add((name, need, cnt))
    return out


def case_dup(g):
    out = set()
    for m in re.finditer(r"<<switch[^>]*>>(.*?)<</switch>>", g, re.S):
        body = m.group(1)
        cases = re.findall(r'<<case\s+"?([^">]+)"?>>', body)
        for k, v in Counter(cases).items():
            if v > 1:
                out.add(k)
    return out


print("=" * 90)
print("widget 参数不足")
print("=" * 90)
mp = param_mismatch(mg)
vp = param_mismatch(vg)
print(f"  modded {len(mp)} 种 / vanilla {len(vp)} 种")
only = mp - vp
print(f"  modded 独有: {len(only)}")
for x in sorted(only)[:20]:
    print(f"    {x}")

print("\n" + "=" * 90)
print("switch case 重复")
print("=" * 90)
mc = case_dup(mg)
vc = case_dup(vg)
print(f"  modded {len(mc)} 种 / vanilla {len(vc)} 种")
only_c = mc - vc
print(f"  modded 独有: {len(only_c)}")
for x in sorted(only_c)[:20]:
    print(f"    {x!r}")
    for m in list(re.finditer(r'<<case\s+"?' + re.escape(x) + r'"?>>', mg))[:3]:
        print(f"      {mg[max(0,m.start()-200):m.start()+100]!r}")
