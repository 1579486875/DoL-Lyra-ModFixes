"""第 1 轮：环境快照（L0，只读，不改任何字节）。"""
import hashlib
import html
import os
import re
import zipfile
from datetime import datetime

OUT = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"
WORK = r"E:\TAML\_dol\work"
ARCHIVE = r"E:\TAML\_dol\archive"


def mb(n):
    return f"{n / 1048576:.2f} MB"


def sha256(p, limit=None):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while True:
            b = f.read(1048576)
            if not b:
                break
            h.update(b)
    return h.hexdigest().upper()


print("=" * 88)
print("环境快照（本轮 L3）")
print("=" * 88)
print(f"  时间: {datetime.now():%Y-%m-%d %H:%M:%S}")

print("\n--- 交付物 ---")
for label, p in (("modded", OUT), ("vanilla", VAN)):
    if os.path.exists(p):
        st = os.stat(p)
        print(f"  {label:8} {mb(st.st_size):>12}  {datetime.fromtimestamp(st.st_mtime):%Y-%m-%d %H:%M}  {os.path.basename(p)}")

print(f"\n--- 归档 ---")
ar = sorted([f for f in os.listdir(ARCHIVE) if f.endswith(".apk")])
print(f"  {len(ar)} 个 APK")
if ar:
    print(f"  最新: {ar[-1]}")
    print(f"  最旧: {ar[0]}")

print(f"\n--- 构建产物 ---")
for f in ("index_modded6.html", "build.py", "build_all.py", "validate.py", "regress.py"):
    p = os.path.join(WORK, f)
    if os.path.exists(p):
        st = os.stat(p)
        print(f"  {f:24} {mb(st.st_size):>12}  {datetime.fromtimestamp(st.st_mtime):%Y-%m-%d %H:%M}")

# 读 APK
z = zipfile.ZipFile(OUT)
names = z.namelist()
raw = z.read("assets/www/index.html")
txt = raw.decode("utf-8", "replace")
g = html.unescape(txt)

print("\n--- APK 结构 ---")
print(f"  条目总数: {len(names):,}")
img = [n for n in names if n.startswith("assets/www/img/")]
print(f"  图片: {len(img):,}")
print(f"  index.html: {mb(len(raw))}")

# 版本
m = re.search(r'<tw-storydata[^>]*name="([^"]*)"[^>]*', txt)
if m:
    print(f"  故事名: {html.unescape(m.group(1))}")
mv = re.search(r'if\(version\s*===\s*"([^"]+)"\)|版本\s*([\d.]+)|version:\s*"([\d.]+)"', txt)
if mv:
    print(f"  版本标记: {[x for x in mv.groups() if x]}")

# passage 数
pn = len(re.findall(r"<tw-passagedata", txt))
print(f"  passage: {pn:,}")

# 模组
mm = re.findall(r'window\.modDataValueZipList\s*=\s*\[([^\]]*)\]', txt)
if mm:
    print(f"  模组 zip 条目: 见下")

# widget 数
wcount = len(re.findall(r'<<widget\s+"', g))
print(f"  widget 定义: {wcount:,}")

# <<script>> 数
sc = len(re.findall(r"<script\b", txt))
print(f"  <script> 标签: {sc}")

# 关键修复标记
print("\n--- 已知修复标记 ---")
MARKERS = {
    "setup 守卫(typeof setup)": 'typeof setup !== "undefined"',
    "NPC_CN getter 锁定": "__cnLockCount",
    "Widgets Repair passage": "Widgets Repair",
    "flight_text": "flight_text",
    "_bodyKeys": "_bodyKeys",
    "compoundWraith": "compoundWraith",
}
for k, v in MARKERS.items():
    print(f"  {v in g and '✅' or '❌'} {k}: {g.count(v)}")

print("\n--- 构建脚本 ---")
ba = os.path.join(WORK, "build_all.py")
if os.path.exists(ba):
    s = open(ba, encoding="utf-8").read()
    scripts = re.findall(r'_dol\\\\work\\\\([A-Z]+0\d_[a-z0-9_]+\.py)', s)
    print(f"  build_all 含 {len(scripts)} 个脚本")
    # 检查文件是否都存在
    missing = [x for x in scripts if not os.path.exists(os.path.join(WORK, x))]
    print(f"  缺失脚本: {missing if missing else '无'}")
