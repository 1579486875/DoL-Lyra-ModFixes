"""第 8-14 轮：图片资源完整性。

 8) index 里所有 img/xxx 引用是否存在于 APK
 9) 模组 imgFileList 是否与 zip 内路径一致
10) 路径大小写一致性
11) 服装图层引用
12) 表情/脸型变体
13) GIF 动画完整性
14) 图标路径
"""
import base64
import html
import io
import json
import re
import zipfile
from collections import Counter

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
z = zipfile.ZipFile(APK)
names = set(z.namelist())

raw = z.read("assets/www/index.html")
g = html.unescape(raw.decode("utf-8", "replace"))

print("=" * 94)
print("第 8 轮：index 里的 img 引用 vs APK 实际文件")
print("=" * 94)
refs = set()
for m in re.finditer(r"img/[A-Za-z0-9_/.\-]+\.(?:png|gif|jpg|jpeg|webp|svg)", g):
    refs.add(m.group(0))
print(f"  静态引用: {len(refs)}")

missing = []
for r in sorted(refs):
    if ("assets/www/" + r) not in names:
        missing.append(r)
print(f"  缺失: {len(missing)}")
for m_ in missing[:25]:
    print(f"    {m_}")

print("\n" + "=" * 94)
print("第 9 轮：模组 imgFileList 与 zip 内路径一致性")
print("=" * 94)
j = raw.find(b"[", raw.find(b"window.modDataValueZipList"))
k = raw.find(b"]", j)
parts = re.findall(r'"([A-Za-z0-9+/=\s]+)"', raw[j + 1:k].decode("utf-8", "replace"))

bad_mod = []
for s in parts:
    b = base64.b64decode(re.sub(r"\s+", "", s))
    if b[:2] != b"PK":
        continue
    zz = zipfile.ZipFile(io.BytesIO(b))
    if "boot.json" not in zz.namelist():
        continue
    bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
    name = bj.get("name") or "?"
    inner = set(zz.namelist())
    for f in bj.get("imgFileList") or []:
        if f not in inner:
            bad_mod.append((name, f))
print(f"  imgFileList 与实际不符: {len(bad_mod)}")
for n, f in bad_mod[:15]:
    print(f"    [{n}] {f}")

print("\n" + "=" * 94)
print("第 10 轮：路径大小写一致性（index 引用 vs 实际文件）")
print("=" * 94)
lower_map = {}
for n in names:
    lower_map.setdefault(n.lower(), []).append(n)
case_bad = []
for r in sorted(refs):
    p = "assets/www/" + r
    if p in names:
        continue
    cand = lower_map.get(p.lower())
    if cand:
        case_bad.append((r, cand[0]))
print(f"  大小写不符: {len(case_bad)}")
for a, b in case_bad[:10]:
    print(f"    {a}  →  实际是 {b}")

print("\n" + "=" * 94)
print("第 11 轮：服装图层引用")
print("=" * 94)
cloth = set()
for m in re.finditer(r"img/clothes/[A-Za-z0-9_/.\-]+\.(?:png|gif)", g):
    cloth.add(m.group(0))
miss_c = [c for c in cloth if ("assets/www/" + c) not in names]
print(f"  服装图引用 {len(cloth)}，缺失 {len(miss_c)}")
for c in miss_c[:15]:
    print(f"    {c}")

print("\n" + "=" * 94)
print("第 12 轮：脸型变体覆盖")
print("=" * 94)
variants = Counter()
for n in names:
    m = re.match(r"assets/www/img/face/([^/]+)/([^/]+)/", n)
    if m:
        variants[(m.group(1), m.group(2))] += 1
face_roots = Counter(v[0] for v in variants)
for k_, c in face_roots.most_common(12):
    subs = sorted({v[1] for v in variants if v[0] == k_})
    print(f"  {k_}: {len(subs)} 个子目录, {c} 个文件")

print("\n" + "=" * 94)
print("第 13 轮：GIF 完整性")
print("=" * 94)
gifs = [n for n in names if n.lower().endswith(".gif")]
bad_gif = 0
for n in gifs:
    try:
        d = z.read(n)
        if d[:6] not in (b"GIF87a", b"GIF89a"):
            bad_gif += 1
    except Exception:
        bad_gif += 1
print(f"  GIF 总数 {len(gifs)}，损坏 {bad_gif}")

print("\n" + "=" * 94)
print("第 14 轮：PNG 完整性（抽样 200 个）")
print("=" * 94)
pngs = [n for n in names if n.lower().endswith(".png")]
sample = pngs[:: max(1, len(pngs) // 200)][:200]
bad_png = 0
for n in sample:
    try:
        d = z.read(n)
        if not d.startswith(b"\x89PNG\r\n\x1a\n"):
            bad_png += 1
    except Exception:
        bad_png += 1
print(f"  PNG 总数 {len(pngs)}，抽样 {len(sample)} 个，损坏 {bad_png}")
