"""新一轮 第1轮：环境快照 + 历史修复复查（防复发）。"""
import hashlib
import html
import os
import re
import zipfile
from datetime import datetime

OUT = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"
ARCHIVE = r"E:\TAML\_dol\archive"

print("=" * 90)
print(f"环境快照 · {datetime.now():%Y-%m-%d %H:%M:%S}")
print("=" * 90)

for label, p in (("modded", OUT), ("vanilla", VAN)):
    st = os.stat(p)
    print(f"  {label:8} {st.st_size/1048576:>8.2f} MB  {datetime.fromtimestamp(st.st_mtime):%Y-%m-%d %H:%M}")

ar = sorted(f for f in os.listdir(ARCHIVE) if f.endswith(".apk"))
print(f"  归档 {len(ar)} 个，最新: {ar[-1][:70] if ar else '-'}")

h = hashlib.sha256(open(OUT, "rb").read()).hexdigest().upper()
print(f"  SHA256 {h}")

z = zipfile.ZipFile(OUT)
g = html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))
print(f"  passage {len(re.findall(r'<tw-passagedata', z.read('assets/www/index.html').decode('utf-8','replace'))):,}")
print(f"  index {z.getinfo('assets/www/index.html').file_size/1048576:.2f} MB")

print("\n" + "=" * 90)
print("历史修复复查（11 类，防复发）")
print("=" * 90)
CHECKS = [
    ("1. setup 守卫（裸 setup）", 'typeof setup !== "undefined"', True),
    ("2. getter 锁定", "__cnLockCount", True),
    ("3. Widgets Repair passage", "Widgets Repair", True),
    ("4. flight_text", "flight_text", True),
    ("5. flesh_text 残留", "flesh_text", False),
    ("6. printNobody 残留", "<<printNobody>>", False),
    ("7. pcpet-name 残留", "<<pcpet-name", False),
    ("8. plural-ize 残留", "<<plural-ize", False),
    ("9. 中文键对象残留", "{'男':", False),
    ("10. _bodyKeys", "_bodyKeys", True),
    ("11. compoundWraith", "compoundWraith", True),
    ("12. 三重尖括号残留", "<<</if>>", False),
    ("13. NPC名 case 中文残留", '<<case "巨鹰">>', False),
    ("14. C.npc 中文索引残留", 'C.npc["巨鹰"]', False),
    ("15. nnpc 中文参数残留", '<<nnpc_his "巨鹰">>', False),
    ("16. 贞操锁寄生虫 判断残留", 'is "贞操锁寄生虫"', False),
    ("17. === 你自己 残留", '=== "你自己"', False),
    ("18. R24 翻译样本", "它「啵」地一声抽了出来", True),
]

bad = []
for item in CHECKS:
    name, pat, want = item[0], item[1], item[2]
    n = g.count(pat)
    ok = (n > 0) if want else (n == 0)
    print(f"  {'✅' if ok else '❌'} {name}: {n}")
    if not ok:
        bad.append((name, pat, n, want))

print("\n" + "=" * 90)
print(f"复查结果: {len(CHECKS)-len(bad)}/{len(CHECKS)} 通过")
print("=" * 90)
if bad:
    for name, pat, n, want in bad:
        print(f"  ❌ {name}: 实际 {n}，期望 {'>0' if want else '==0'}")
else:
    print("  ✅ 全部历史修复仍在生效，无复发")
