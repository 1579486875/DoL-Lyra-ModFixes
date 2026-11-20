"""H05：在模组 zip 里搜 partCN / BODYPARTS_CN_NAME 覆盖。"""
import base64
import html as H
import io
import json
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
g = H.unescape(zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace"))

m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", g, re.S)
parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m.group(1))
print(f"模组 zip {len(parts)}\n")

FOUND = []
for idx, s in enumerate(parts):
    raw = base64.b64decode(re.sub(r"\s+", "", s))
    if raw[:2] != b"PK":
        continue
    try:
        zz = zipfile.ZipFile(io.BytesIO(raw))
        bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
        modname = bj.get("name", f"#{idx}")
    except Exception:
        continue

    for n in zz.namelist():
        if not n.endswith((".js", ".twee", ".json", ".html")):
            continue
        try:
            txt = zz.read(n).decode("utf-8", "replace")
        except Exception:
            continue
        if "partCN" in txt or "BODYPARTS_CN_NAME" in txt or re.search(r"\bBODYPARTS\b\s*=", txt):
            FOUND.append((modname, n, txt))

print("=" * 95)
print(f"命中 {len(FOUND)} 个文件")
print("=" * 95)
for modname, fname, txt in FOUND:
    print(f"\n[{modname}] {fname}")
    # 提关键片段
    for kw in ("function partCN", "partCN =", "BODYPARTS_CN_NAME", "var BODYPARTS", "BODYPARTS ="):
        for mm in re.finditer(re.escape(kw), txt):
            seg = txt[max(0, mm.start() - 250):mm.start() + 600]
            print(f"  --- {kw} @{mm.start()} ---")
            print(f"  {seg!r}")
            break

# 也搜 index 里的 partCN（可能在 script 字符串里）
print("\n" + "=" * 95)
print("index 里的 partCN（宽松匹配）")
print("=" * 95)
for mm in list(re.finditer(r"partCN", g))[:10]:
    print(f"  @{mm.start()}: {g[max(0,mm.start()-200):mm.start()+300]!r}\n")
