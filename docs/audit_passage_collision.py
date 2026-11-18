import base64, html, io, json, re, zipfile, collections

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
DEADWOOD = r"E:\TAML\_dol\work\deadwood_decrypted.zip"

z = zipfile.ZipFile(APK)
raw = z.read("assets/www/index.html")

# 游戏原版 passage
game_passages = set()
for m in re.finditer(rb'<tw-passagedata[^>]*name="([^"]+)"', raw):
    game_passages.add(m.group(1).decode("utf-8", "replace"))
print("游戏原版 passage:", len(game_passages))

j = raw.find(b"[", raw.find(b"window.modDataValueZipList"))
k = raw.find(b"]", j)
parts = re.findall(r'"([A-Za-z0-9+/=\s]+)"', raw[j + 1:k].decode("utf-8", "replace"))

mod_twee = []  # (name, zip, [files])
for s in parts:
    b = base64.b64decode(re.sub(r"\s+", "", s))
    if b[:16] == b"JeremieModLoader":
        continue
    try:
        zz = zipfile.ZipFile(io.BytesIO(b))
        bj = json.loads(zz.read("boot.json").decode("utf-8-sig")) if "boot.json" in zz.namelist() else {}
        if bj.get("tweeFileList"):
            mod_twee.append((bj.get("name"), zz, bj.get("tweeFileList")))
    except Exception:
        pass

# Deadwood（已解密）
try:
    dz = zipfile.ZipFile(DEADWOOD)
    dbj = json.loads(dz.read("boot.json").decode("utf-8-sig"))
    if dbj.get("tweeFileList"):
        mod_twee.append(("deadwood-reblooms", dz, dbj["tweeFileList"]))
except Exception as e:
    print("Deadwood 读取失败:", e)

# 统计每个 mod 定义的 passage / widget
def collect(txt):
    ps = re.findall(r"(?m)^::\s*([^\n\[]+?)(?:\s*\[[^\]]*\])?\s*$", txt)
    wg = re.findall(r'<<widget\s+"([^"]+)"', txt)
    return [p.strip() for p in ps], wg

all_ps = collections.defaultdict(set)   # passage -> mods
all_wg = collections.defaultdict(set)
for name, zz, files in mod_twee:
    for f in files:
        try:
            t = zz.read(f).decode("utf-8", "ignore")
        except Exception:
            continue
        ps, wg = collect(t)
        for p in ps:
            all_ps[p].add(name)
        for w in wg:
            all_wg[w].add(name)

print(f"\n模组定义的 passage 总数: {len(all_ps)}")
print(f"模组定义的 widget 总数: {len(all_wg)}")

# 1) 与游戏原版重名
overlap = {p: o for p, o in all_ps.items() if p in game_passages}
print(f"\n【1】模组 passage 与游戏原版重名（会覆盖原版！）: {len(overlap)}")
for p, o in sorted(overlap.items())[:30]:
    print(f"  {p:<50} ← {sorted(o)}")

# 2) 多个模组之间重名
multi = {p: o for p, o in all_ps.items() if len(o) > 1}
print(f"\n【2】多个模组定义同名 passage: {len(multi)}")
for p, o in sorted(multi.items())[:30]:
    print(f"  {p:<50} ← {sorted(o)}")

# 3) widget 重名
wmulti = {w: o for w, o in all_wg.items() if len(o) > 1}
print(f"\n【3】多个模组定义同名 widget: {len(wmulti)}")
for w, o in sorted(wmulti.items())[:30]:
    print(f"  {w:<40} ← {sorted(o)}")
