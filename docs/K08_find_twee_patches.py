"""K08：搜所有 TweeReplacerAddon 的 params，找 fallentransform / robinpaid 补丁。"""
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

NEEDLES = ["fallentransform", "robinpaid", "robindebtknown", "canAfford"]


def flatten(x, path=""):
    out = []
    if isinstance(x, list):
        for i, y in enumerate(x):
            out.extend(flatten(y, f"{path}[{i}]"))
    elif isinstance(x, dict):
        for k, v in x.items():
            out.extend(flatten(v, f"{path}.{k}"))
    else:
        out.append((path, x))
    return out


found = []
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

    ap = bj.get("addonPlugin")
    if not ap:
        continue
    for a in (ap if isinstance(ap, list) else [ap]):
        if not isinstance(a, dict) or a.get("addonName") != "TweeReplacerAddon":
            continue
        for path, v in flatten(a.get("params")):
            if not isinstance(v, str):
                continue
            if any(kw in v for kw in NEEDLES):
                found.append((modname, path, v))

print("=" * 95)
print(f"TweeReplacerAddon 里含目标锚点的补丁: {len(found)} 条")
print("=" * 95)
for mod, path, v in found:
    print(f"\n[{mod}] {path}")
    print(f"  {v[:400]!r}")

# 如果没找到，说明补丁在别处
if not found:
    print("\n⚠️ 所有模组的 TweeReplacerAddon 里都没有这些锚点")
    print("→ 说明补丁定义在【用户手机本地存储】或【其他来源】，不在 APK 里")
    print("\n排查：看看哪些模组有 TweeReplacerAddon")
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
        ap = bj.get("addonPlugin")
        if not ap:
            continue
        names = [a.get("addonName") for a in (ap if isinstance(ap, list) else [ap])
                 if isinstance(a, dict)]
        if "TweeReplacerAddon" in names:
            # 数一下补丁条数
            cnt = 0
            for a in (ap if isinstance(ap, list) else [ap]):
                if isinstance(a, dict) and a.get("addonName") == "TweeReplacerAddon":
                    ps = a.get("params")
                    if isinstance(ps, list):
                        cnt += len(ps)
                    elif isinstance(ps, dict):
                        cnt += sum(len(v) for v in ps.values() if isinstance(v, list))
            print(f"  {modname}: {cnt} 条补丁")
