"""Y03：全量扫 TweeReplacer 补丁的健康度。

检查项：
  1. 空 regexFlag（会导致 new RegExp(p, "") 失败）
  2. findRegex 语法是否合法（用 re.compile 在本地验）
  3. findString 的锚点是否真的存在于 index
  4. 补丁里的 passage 是否存在
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

PASSAGES = {}
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', g, re.S):
    PASSAGES[m.group(1)] = m.group(2)

m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", g, re.S)
parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m.group(1))

print("=" * 95)
print("1. 空 regexFlag（全模组）")
print("=" * 95)
n1 = 0
bad_mods = []
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
    for a in (bj.get("addonPlugin") or []):
        if not isinstance(a, dict) or a.get("addonName") != "TweeReplacerAddon":
            continue
        for p in (a.get("params") or []):
            if not isinstance(p, dict):
                continue
            if p.get("regexFlag") == "":
                n1 += 1
                bad_mods.append((modname, p.get("passage", "")[:40],
                                 (p.get("findRegex") or "")[:60]))
print(f"  共 {n1} 处")
for mod, psg, fr in bad_mods[:20]:
    print(f"    [{mod}] {psg!r}  regex={fr!r}")

print("\n" + "=" * 95)
print("2. findRegex 语法合法性（用 Python re 近似验）")
print("=" * 95)
n2 = 0
bad_regex = []
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
    for a in (bj.get("addonPlugin") or []):
        if not isinstance(a, dict) or a.get("addonName") != "TweeReplacerAddon":
            continue
        for p in (a.get("params") or []):
            if not isinstance(p, dict):
                continue
            fr = p.get("findRegex")
            if not isinstance(fr, str):
                continue
            n2 += 1
            try:
                re.compile(fr)
            except re.error as e:
                bad_regex.append((modname, p.get("passage", "")[:30], fr[:70], str(e)[:50]))
print(f"  共 {n2} 条 findRegex")
print(f"  Python re 编译失败: {len(bad_regex)}")
for mod, psg, fr, err in bad_regex[:10]:
    print(f"    [{mod}] {psg!r}")
    print(f"      {fr!r}")
    print(f"      → {err}")

print("\n" + "=" * 95)
print("3. findString 锚点是否存在于 index")
print("=" * 95)
n3 = 0
miss3 = []
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
    for a in (bj.get("addonPlugin") or []):
        if not isinstance(a, dict) or a.get("addonName") != "TweeReplacerAddon":
            continue
        for p in (a.get("params") or []):
            if not isinstance(p, dict):
                continue
            fs = p.get("findString")
            psg = p.get("passage")
            if not isinstance(fs, str) or not psg:
                continue
            n3 += 1
            body = PASSAGES.get(psg)
            if body is None:
                miss3.append((modname, psg, fs[:50], "passage 不存在"))
            elif fs not in body:
                miss3.append((modname, psg, fs[:50], "锚点不在"))

print(f"  共 {n3} 条 findString")
print(f"  失效: {len(miss3)}")
for mod, psg, fs, why in miss3[:15]:
    print(f"    [{mod}] {psg!r}  {why}")
    print(f"      {fs!r}")

print("\n" + "=" * 95)
print("汇总")
print("=" * 95)
print(f"  空 regexFlag:      {n1}")
print(f"  findRegex 语法错:  {len(bad_regex)} / {n2}")
print(f"  findString 失效:   {len(miss3)} / {n3}")
