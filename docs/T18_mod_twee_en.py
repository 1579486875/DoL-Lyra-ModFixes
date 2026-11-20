"""T18：扫模组 .twee 里的英文正文（排除宏行/标签行/赋值行）。

判据（一行算「正文」必须同时满足）：
  1. 不以 :: / << / <!-- / /* / // / [ / { 开头
  2. 不含 << 宏
  3. 去掉 HTML 标签后，中文占比为 0
  4. 有 4+ 个 ≥2 字母的英文词
"""
import base64
import html as H
import io
import json
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
z = zipfile.ZipFile(APK)
g = H.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))

SKIP_MODS = {"ModI18N", "ModLoaderGui", "ModLoader", "TweeReplacer",
             "I18nTweeReplacer", "TweeReplacerLinker", "ModSubUiAngularJs"}

m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", g, re.S)
parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m.group(1))


def is_body(line):
    s = line.strip()
    if len(s) < 20:
        return False
    if s.startswith(("::", "<<", "<!--", "/*", "//", "[", "{", "}", "<", "@", "#")):
        return False
    if "<<" in s or ">>" in s:
        return False
    if re.search(r"[\u4e00-\u9fff]", s):
        return False
    # 去 HTML 标签
    plain = re.sub(r"<[^>]+>", " ", s)
    plain = re.sub(r"&[a-z]+;", " ", plain)
    if len(re.findall(r"[A-Za-z]{2,}", plain)) < 4:
        return False
    if re.fullmatch(r"[A-Za-z0-9_ .\-]+", plain) and plain.count(" ") < 3:
        return False
    return True


results = {}
for s in parts:
    raw = base64.b64decode(re.sub(r"\s+", "", s))
    if raw[:2] != b"PK":
        continue
    try:
        zz = zipfile.ZipFile(io.BytesIO(raw))
        bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
        modname = bj.get("name", "?")
    except Exception:
        continue
    if modname in SKIP_MODS:
        continue

    hits = []
    for n in zz.namelist():
        if not n.endswith(".twee"):
            continue
        try:
            txt = zz.read(n).decode("utf-8", "replace")
        except Exception:
            continue
        for ln, line in enumerate(txt.split("\n"), 1):
            if is_body(line):
                hits.append((n, ln, line.strip()[:130]))
    if hits:
        results[modname] = hits

print("=" * 95)
print(f"模组 .twee 里的英文正文：{len(results)} 个模组")
print("=" * 95)

total = 0
for mod, hits in sorted(results.items(), key=lambda x: -len(x[1])):
    total += len(hits)
    print(f"\n[{mod}]  {len(hits)} 行")
    for n, ln, s in hits[:6]:
        print(f"    {n}:{ln}  {s!r}")
    if len(hits) > 6:
        print(f"    ... 还有 {len(hits) - 6}")

print("\n" + "=" * 95)
print(f"总计 {total} 行英文正文，跨 {len(results)} 个模组")
print("=" * 95)

# 保存清单
with open(r"E:\TAML\_dol\work\_mod_twee_en.json", "w", encoding="utf-8") as f:
    json.dump({k: v[:50] for k, v in results.items()}, f, ensure_ascii=False, indent=1)
print("已保存 _mod_twee_en.json（每模组最多 50 行）")
