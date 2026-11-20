"""K09：打印 DomRobin 补丁 [38][39][74] 的完整定义（含 passage 字段）。"""
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
    if modname != "DomRobin":
        continue

    for a in (bj.get("addonPlugin") or []):
        if not isinstance(a, dict) or a.get("addonName") != "TweeReplacerAddon":
            continue
        ps = a.get("params")
        if not isinstance(ps, list):
            continue
        for idx in (38, 39, 51, 74):
            if idx >= len(ps):
                continue
            p = ps[idx]
            print("=" * 95)
            print(f"[DomRobin] params[{idx}]")
            print("=" * 95)
            if isinstance(p, dict):
                for k, v in p.items():
                    print(f"  {k} = {v!r}")
            print()

        # 数一下总补丁数
        print(f"总补丁数: {len(ps)}")
        # 列出所有 passage 名
        pns = {}
        for p in ps:
            if isinstance(p, dict):
                pn = p.get("passage")
                if pn:
                    pns[pn] = pns.get(pn, 0) + 1
        print(f"涉及 passage: {list(pns.items())[:20]}")
        break
    break

# 同时搜索 DoLSims 的 TweeReplacerAddon
print("\n" + "=" * 95)
print("DoLSims 的 TweeReplacerAddon")
print("=" * 95)
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
    if modname != "DoLSims":
        continue
    for a in (bj.get("addonPlugin") or []):
        if not isinstance(a, dict):
            continue
        if a.get("addonName") != "TweeReplacerAddon":
            continue
        ps = a.get("params")
        print(f"  params 类型: {type(ps).__name__}")
        if isinstance(ps, list):
            print(f"  条数: {len(ps)}")
            for i, p in enumerate(ps):
                if isinstance(p, dict):
                    fs = p.get("findString") or p.get("findRegex") or ""
                    if "fallentransform" in str(fs) or "angel" in str(fs):
                        print(f"\n  [{i}] 命中:")
                        for k, v in p.items():
                            print(f"    {k} = {v!r}")
