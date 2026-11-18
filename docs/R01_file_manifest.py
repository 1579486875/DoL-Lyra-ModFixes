import base64, io, json, os, re, zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
z = zipfile.ZipFile(APK)
raw = z.read("assets/www/index.html")
j = raw.find(b"[", raw.find(b"window.modDataValueZipList"))
k = raw.find(b"]", j)
parts = re.findall(r'"([A-Za-z0-9+/=\s]+)"', raw[j + 1:k].decode("utf-8", "replace"))

print("=" * 92)
print("R1. 文件清单完整性：boot.json 声明 vs 包内实际")
print("=" * 92)

KEYS = ["tweeFileList", "scriptFileList", "scriptFileList_inject_early",
        "scriptFileList_preload", "scriptFileList_earlyload", "styleFileList",
        "imgFileList", "additionFile", "additionBinaryFile"]

problems = []
total_refs = 0
mod_count = 0
for s in parts:
    b = base64.b64decode(re.sub(r"\s+", "", s))
    if b[:2] != b"PK":
        continue
    try:
        zz = zipfile.ZipFile(io.BytesIO(b))
        if "boot.json" not in zz.namelist():
            continue
        bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
    except Exception as e:
        problems.append(("(解析失败)", str(e)[:60]))
        continue
    mod_count += 1
    name = bj.get("name") or "?"
    names = set(zz.namelist())
    for key in KEYS:
        for f in bj.get(key) or []:
            total_refs += 1
            if f not in names:
                problems.append((name, f"{key}: {f}"))
    # boot.json 自身字段
    for req in ("name", "version"):
        if not bj.get(req):
            problems.append((name, f"boot.json 缺 {req}"))

print(f"模组数: {mod_count}")
print(f"引用总数: {total_refs}")
print(f"缺失/问题: {len(problems)}")
for n, p in problems[:25]:
    print(f"  ❌ {n} | {p}")

# APK 顶层结构
print("\n=== APK 关键文件 ===")
for f in ["AndroidManifest.xml", "classes.dex", "resources.arsc",
          "assets/www/index.html", "assets/www/custom_cordova_additions.js"]:
    try:
        print(f"  ✅ {f:<46} {z.getinfo(f).file_size:>12,} 字节")
    except KeyError:
        print(f"  ❌ {f:<46} 缺失")
