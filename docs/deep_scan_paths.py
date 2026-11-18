import re, zipfile, collections

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
z = zipfile.ZipFile(APK)
raw = z.read("assets/www/index.html")
text = raw.decode("utf-8", "replace")

have = {n[len("assets/www/"):] for n in z.namelist() if n.startswith("assets/www/img/")}
have_lower = {h.lower(): h for h in have}
print("APK img 文件:", len(have))

# 更宽松：单引号 + 双引号 + 反引号，允许前导缺 img/ 的写法先不管
pats = [
    r'"((?:img/)[^"\n]{1,120}?\.(?:png|gif|jpg|jpeg|webp|mp3|ogg|wav))"',
    r"'((?:img/)[^'\n]{1,120}?\.(?:png|gif|jpg|jpeg|webp|mp3|ogg|wav))'",
    r"`((?:img/)[^`\n]{1,120}?\.(?:png|gif|jpg|jpeg|webp|mp3|ogg|wav))`",
]
refs = set()
for p in pats:
    refs |= set(re.findall(p, text))
print("扫描到的完整路径字面量:", len(refs))

missing = []
case_bad = []
for r in sorted(refs):
    if r in have:
        continue
    if r.lower() in have_lower:
        case_bad.append((r, have_lower[r.lower()]))
    else:
        missing.append(r)

print(f"\n=== 不存在 {len(missing)} 条 ===")
by_dir = collections.Counter("/".join(m.split("/")[:4]) for m in missing)
for k, v in by_dir.most_common(20):
    print(f"  {v:>4}  {k}")

print(f"\n=== 大小写不匹配 {len(case_bad)} 条 ===")
for a, b in case_bad[:15]:
    print(f"  引用 {a}\n    实际 {b}")

# 打印前 40 条缺失明细
print("\n=== 缺失明细（前 40）===")
for m in missing[:40]:
    print("  ", m)
