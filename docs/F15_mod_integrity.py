"""F15（第12轮）：模组 zip 完整性 + 模组 passage 冲突。"""
import base64
import html as H
import io
import json
import re
import zipfile
from collections import Counter

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
g = H.unescape(zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace"))

m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", g, re.S)
if not m:
    raise SystemExit("❌ 无 modDataValueZipList")

parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m.group(1))
print(f"模组 zip: {len(parts)}")

base_passages = set(re.findall(r'<tw-passagedata[^>]*name="([^"]*)"', g))

OK = 0
BAD = []
mod_passages = {}   # mod -> set of passage names

for idx, s in enumerate(parts):
    try:
        raw = base64.b64decode(re.sub(r"\s+", "", s))
    except Exception as e:
        BAD.append((idx, "base64 解码失败", str(e)))
        continue
    if raw[:2] != b"PK":
        BAD.append((idx, "不是 ZIP", raw[:20]))
        continue
    try:
        zz = zipfile.ZipFile(io.BytesIO(raw))
        bad_member = zz.testzip()
        if bad_member:
            BAD.append((idx, "ZIP 内部损坏", bad_member))
            continue
    except Exception as e:
        BAD.append((idx, "ZIP 打不开", str(e)))
        continue

    try:
        bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
        name = bj.get("name", f"#{idx}")
    except Exception:
        name = f"#{idx}"

    OK += 1

    # 收集 mod 的 passage 名
    ps = set()
    for n in zz.namelist():
        if n.endswith(".twee"):
            try:
                txt = zz.read(n).decode("utf-8", "replace")
            except Exception:
                continue
            for mm in re.finditer(r"^::\s*([^\n\[]+)", txt, re.M):
                ps.add(mm.group(1).strip())
    mod_passages[name] = ps

print("\n" + "=" * 90)
print(f"✅ 正常 {OK} / ❌ 异常 {len(BAD)}")
print("=" * 90)
for idx, why, detail in BAD:
    print(f"  #{idx} {why}: {detail}")

print("\n" + "=" * 90)
print("模组 passage 与主 story 冲突")
print("=" * 90)
conflict_by_mod = {}
for mod, ps in mod_passages.items():
    c = ps & base_passages
    if c:
        conflict_by_mod[mod] = c

print(f"  {len(conflict_by_mod)} 个模组有冲突")
for mod, ps in sorted(conflict_by_mod.items(), key=lambda x: -len(x[1]))[:15]:
    print(f"    [{mod}] {len(ps)} 个: {sorted(ps)[:5]}")

print("\n" + "=" * 90)
print("模组之间 passage 冲突")
print("=" * 90)
seen = {}
multi = {}
for mod, ps in mod_passages.items():
    for p in ps:
        if p in seen and seen[p] != mod:
            multi.setdefault(p, set()).update({seen[p], mod})
        else:
            seen[p] = mod
print(f"  {len(multi)} 个 passage 被多个模组定义")
for p, mods in list(multi.items())[:15]:
    print(f"    {p!r} <- {sorted(mods)}")

print("\n" + "=" * 90)
print("模组数量 / passage 总数")
print("=" * 90)
total_ps = sum(len(v) for v in mod_passages.values())
print(f"  模组 passage 总数: {total_ps}")
print(f"  主 story passage: {len(base_passages)}")
