"""只处理确认被翻译破坏的标识符（用 vanilla 精确对照）。"""
import html as H
import os
import re
import sys

VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"
HTML = r"E:\TAML\_dol\work\index_modded6.html"

CJK = re.compile(r"[\u4e00-\u9fff]")


def load_apk(p):
    import zipfile
    z = zipfile.ZipFile(p)
    return H.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))


vg = load_apk(VAN)

# 1) $avery_mansion 的属性名
print("=" * 94)
print("1) $avery_mansion.bow vs .鞠躬")
print("=" * 94)
v_bow = len(re.findall(r"\$avery_mansion\.bow\b", vg))
print(f"  vanilla $avery_mansion.bow: {v_bow} 处")

data = open(HTML, "rb").read().decode("utf-8", "replace")
g = H.unescape(data)
m_bow = len(re.findall(r"\$avery_mansion\.bow\b", g))
m_ju = len(re.findall(r"\$avery_mansion\.鞠躬", g))
print(f"  modded  $avery_mansion.bow: {m_bow} 处")
print(f"  modded  $avery_mansion.鞠躬: {m_ju} 处")

# 2) $attitudesControl.unlockAvery*
print("\n" + "=" * 94)
print("2) $attitudesControl 的属性")
print("=" * 94)
v_att = sorted(set(re.findall(r"\$attitudesControl\.(\w+)", vg)))
m_att = sorted(set(re.findall(r"\$attitudesControl\.([\w\u4e00-\u9fff]+)", g)))
print(f"  vanilla: {v_att}")
print(f"  modded : {m_att}")

# 3) 上下文
print("\n" + "=" * 94)
print("3) $avery_mansion.鞠躬 的上下文")
print("=" * 94)
for mm in list(re.finditer(r"\$avery_mansion\.鞠躬", g))[:3]:
    print(f"  {g[max(0,mm.start()-180):mm.start()+180]!r}")
    print()

print("=" * 94)
print("4) vanilla 里对应的写法")
print("=" * 94)
# 找 vanilla 里 "不鞠躬" 附近
for mm in list(re.finditer(r"\$avery_mansion\.bow", vg))[:3]:
    print(f"  {vg[max(0,mm.start()-180):mm.start()+180]!r}")
    print()

# 5) 执行修复
print("=" * 94)
print("5) 修复")
print("=" * 94)
total = 0
FIXES = [
    ("$avery_mansion.鞠躬", "$avery_mansion.bow"),
    ("$attitudesControl.unlockAvery鞠躬", "$attitudesControl.unlockAveryBow"),
]
for old, new in FIXES:
    for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
        if a in data:
            n = data.count(a)
            data = data.replace(a, b)
            total += n
            print(f"  ✅ {old} -> {new}  ({n} 处)")
            break

if total:
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"\n合计 {total} 处，写出 {HTML}")

# 6) 校验
g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
print("\n=== 校验 ===")
print(f"  $avery_mansion.鞠躬: {len(re.findall(r'[$]avery_mansion[.]鞠躬', g2))}")
print(f"  $avery_mansion.bow:  {len(re.findall(r'[$]avery_mansion[.]bow', g2))}")
print(f"  unlockAvery鞠躬:     {len(re.findall('unlockAvery鞠躬', g2))}")

# 7) 全库：中文属性名（严格版：.后面直接中文，前面是英文变量名）
print("\n" + "=" * 94)
print("7) 全库严格扫描：$obj.纯中文属性")
print("=" * 94)
hits = set()
for mm in re.finditer(r"\$(\w+)\.([\u4e00-\u9fff]+)(?=[\s\]\)\>,|&;]|$)", g2):
    hits.add(f"${mm.group(1)}.{mm.group(2)}")
print(f"  {len(hits)} 处")
for h in sorted(hits):
    print(f"    {h}")
