import zipfile, io, base64, re, json, hashlib, os

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
z = zipfile.ZipFile(APK)
h = z.read("assets/www/index.html")
c = z.read("assets/www/custom_cordova_additions.js").decode("utf-8")
from PIL import Image

print("=" * 80)
print("最终包验证")
print("=" * 80)
checks = []
checks.append(("APK 大小", f"{os.path.getsize(APK):,} 字节 ({os.path.getsize(APK)/1048576:.2f} MB)"))
checks.append(("SHA256", hashlib.sha256(open(APK, "rb").read()).hexdigest().upper()))

j = h.find(b"[", h.find(b"window.modDataValueZipList"))
k = h.find(b"]", j)
parts = re.findall(r'"([A-Za-z0-9+/=\s]+)"', h[j + 1:k].decode("utf-8", "replace"))
checks.append(("模组数", str(len(parts))))
checks.append(("index.html", f"{len(h):,} 字节"))

names = []
for s in parts:
    b = base64.b64decode(re.sub(r"\s+", "", s))
    if b[:2] != b"PK":
        continue
    zz = zipfile.ZipFile(io.BytesIO(b))
    if "boot.json" in zz.namelist():
        names.append(json.loads(zz.read("boot.json").decode("utf-8-sig")).get("name"))

print()
for k2, v in checks:
    print(f"  {k2:<14} {v}")

print("\n=== 修复项在位确认 ===")
fixes = {
    "返回键 Dialog 修复": "typeof Dialog" in c,
    "harmony 路径": b"sym-harmony.png" in h and h.count(b"wolfharmony.png") == 0,
    "doggyRed 归零": h.count(b"doggyRed") == 0,
    "missionaryRed 归零": h.count(b"missionaryRed") == 0,
    "xray 连字符": b"xray-vaginal.png" in h and h.count(b"xray_vaginal.png") == 0,
    "金币占位 x2": all(x in z.namelist() for x in
                   ["assets/www/img/ui/coin-platinum-fake.gif", "assets/www/img/ui/coin-jeweled-fake.gif"]),
}
for v in ["foxy", "gloomy", "makeup"]:
    im = Image.open(io.BytesIO(z.read(f"assets/www/img/face/default/{v}/iris.png"))).convert("RGBA")
    fixes[f"iris/{v}"] = sum(1 for q in im.getdata() if q[3] > 0) == 16342

mods = {
    "Missing Widget Stubs": "widget 补桩",
    "Dead Link Stubs": "模组断链 13",
    "Game Dead Link Stubs": "本体断链 7",
    "Quoted Link Fix": "引号链接 8",
    "Icon Path Fix": "图标路径 3",
    "Toilet Addon": "如厕 4 浴室",
    "EffectsMan Null Guard": "空值保护 14",
    "Handheld Idle Fix": "idle 补图 104",
    "Clothes": "扩展服装",
    "BeautyFixer": "美化修正",
    "clothesicon": "随身衣柜",
}
for n in mods:
    fixes[f"模组 {n}"] = n in names

ok = 0
for name, val in fixes.items():
    mark = "✅" if val else "❌"
    print(f"  {mark} {name}")
    if val:
        ok += 1
print(f"\n通过 {ok}/{len(fixes)}")
