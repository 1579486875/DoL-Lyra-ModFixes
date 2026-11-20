"""M05：查 i18n 表里 <br> -> <<br>> 的翻译错误。"""
import html as H
import io
import json
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
g = H.unescape(zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace"))

import base64
m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", g, re.S)
parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m.group(1))

print("=" * 95)
print("1. ModI18N 的 i18n.json 里，译文含 <<br>> 的")
print("=" * 95)
n = 0
for s in parts:
    raw = base64.b64decode(re.sub(r"\s+", "", s))
    if raw[:2] != b"PK":
        continue
    try:
        zz = zipfile.ZipFile(io.BytesIO(raw))
        bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
    except Exception:
        continue
    if bj.get("name") != "ModI18N":
        continue

    try:
        data = json.loads(zz.read("i18n.json").decode("utf-8-sig"))
    except Exception as e:
        print(f"  ❌ 读 i18n.json 失败: {e}")
        continue

    # 结构：可能是 list 或 dict
    entries = []
    if isinstance(data, list):
        entries = data
    elif isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, list):
                entries = v
                break

    print(f"  i18n 条目 {len(entries)}")

    for it in entries:
        if not isinstance(it, dict):
            continue
        t = it.get("t", "")
        f = it.get("f", "")
        if isinstance(t, str) and "<<br" in t:
            n += 1
            if n <= 15:
                print(f"\n  ❌ 译文含 <<br>>:")
                print(f"    f={str(f)[:180]!r}")
                print(f"    t={str(t)[:180]!r}")

print(f"\n  共 {n} 处译文含 <<br>>")

print("\n" + "=" * 95)
print("2. 全局：任何地方 '<br>' 后面跟 '>' 的异常形式")
print("=" * 95)
for pat in (r"<<br\s*/?\s*>>", r"<<\s*br\s*>>", r"<br\s*>>"):
    hs = list(re.finditer(pat, g))
    print(f"  {pat!r}: {len(hs)}")
    for h in hs[:3]:
        print(f"    {g[max(0,h.start()-120):h.start()+120]!r}")

print("\n" + "=" * 95)
print("3. 全局：'<br>' 在 JS 字符串里（可能被 wikify 二次解析）")
print("=" * 95)
for m2 in re.finditer(r'(?:sWikifier|wikifier|wikifyEval|\.wiki)\s*\(\s*[`\'"][^`\'"]{0,300}<br>', g):
    print(f"  @{m2.start()}: {m2.group(0)[:280]!r}")
