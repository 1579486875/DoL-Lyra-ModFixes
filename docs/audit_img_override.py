import base64, io, json, re, zipfile, collections

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
z = zipfile.ZipFile(APK)
raw = z.read("assets/www/index.html")

have = {n[len("assets/www/"):] for n in z.namelist() if n.startswith("assets/www/img/")}

j = raw.find(b"[", raw.find(b"window.modDataValueZipList"))
k = raw.find(b"]", j)
parts = re.findall(r'"([A-Za-z0-9+/=\s]+)"', raw[j + 1:k].decode("utf-8", "replace"))

overrides = collections.defaultdict(list)
missing = []
for s in parts:
    b = base64.b64decode(re.sub(r"\s+", "", s))
    if b[:16] == b"JeremieModLoader":
        continue
    try:
        zz = zipfile.ZipFile(io.BytesIO(b))
        bj = json.loads(zz.read("boot.json").decode("utf-8-sig")) if "boot.json" in zz.namelist() else {}
    except Exception:
        continue
    name = bj.get("name") or "?"
    names = set(zz.namelist())
    for p in bj.get("imgFileList") or []:
        full = p if p.startswith("img/") else "img/" + p
        if full in names:
            # mod 自带此图 → 会覆盖游戏同名图
            if full in have:
                overrides[full].append(name)
        elif full in have:
            pass
        else:
            missing.append((name, p))

print("【1】模组 imgFileList 覆盖游戏同名图片（会改变原版外观）:")
tot = 0
for p, owners in sorted(overrides.items()):
    tot += 1
    if tot <= 25:
        print(f"  {p:<60} ← {owners}")
print(f"  合计 {len(overrides)} 张")

print(f"\n【2】imgFileList 指向不存在的图: {len(missing)}")
for m in missing[:15]:
    print(f"  {m[0]} | {m[1]}")

# 覆盖游戏的「关键 UI 图」需要留意
CRITICAL = ("img/ui/", "img/misc/icon/", "img/face/", "img/body/", "img/eyes/")
crit = {p: o for p, o in overrides.items() if p.startswith(CRITICAL)}
print(f"\n【3】其中覆盖了 UI/脸/身体/眼睛等关键资源: {len(crit)}")
for p, o in list(crit.items())[:25]:
    print(f"  {p:<60} ← {o}")
