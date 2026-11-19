"""第 15 轮：图片缺失归属 —— vanilla 也缺的就不是我的锅。"""
import html
import re
import zipfile

VANILLA = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"
MODDED = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"


def scan(apk):
    z = zipfile.ZipFile(apk)
    names = set(z.namelist())
    g = html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))
    refs = set(m.group(0) for m in
               re.finditer(r"img/[A-Za-z0-9_/.\-]+\.(?:png|gif|jpg|jpeg|webp|svg)", g))
    missing = {r for r in refs if ("assets/www/" + r) not in names}
    return refs, missing


vr, vm = scan(VANILLA)
mr, mm = scan(MODDED)

print("=" * 94)
print("图片缺失归属")
print("=" * 94)
print(f"  vanilla: 引用 {len(vr)}  缺失 {len(vm)}")
print(f"  modded : 引用 {len(mr)}  缺失 {len(mm)}")
print(f"  modded 独有缺失: {len(mm - vm)}")
for x in sorted(mm - vm)[:20]:
    print(f"    {x}")
print(f"  vanilla 独有缺失: {len(vm - mm)}")

print("\n" + "=" * 94)
print("按目录归类 modded 的缺失")
print("=" * 94)
from collections import Counter
d = Counter()
for x in mm:
    parts = x.split("/")
    d["/".join(parts[:3])] += 1
for k, v in d.most_common(12):
    print(f"  {v:>3}  {k}/")
