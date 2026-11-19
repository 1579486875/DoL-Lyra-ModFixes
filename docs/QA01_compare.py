"""对比昨天的包与新包的翻译覆盖率。"""
import html
import os
import re
import zipfile
from collections import Counter

OLD = r"C:\Users\asus\Downloads\DoL-Lyra-0.5.12.13-CHS-modded-11.18.apk"
NEW = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"

print("=" * 94)
print("文件信息")
print("=" * 94)
for label, p in (("昨天 11.18", OLD), ("现在", NEW)):
    if not os.path.exists(p):
        print(f"  {label}: ❌ 不存在 {p}")
        continue
    print(f"  {label}: {os.path.getsize(p):,} 字节")

if not os.path.exists(OLD):
    raise SystemExit(1)


def load(path):
    z = zipfile.ZipFile(path)
    raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    return raw, html.unescape(raw)


o_raw, o_g = load(OLD)
n_raw, n_g = load(NEW)

print("\n" + "=" * 94)
print("index.html 结构对比")
print("=" * 94)
for label, raw, g in (("昨天", o_raw, o_g), ("现在", n_raw, n_g)):
    cjk = len(re.findall(r"[\u4e00-\u9fff]", g))
    print(f"  {label}: index {len(raw):,} 字节，中文字符 {cjk:,}")

print("\n" + "=" * 94)
print("关键 UI 文本对比")
print("=" * 94)
KEYS = ["疼痛：", "性奋：", "疲劳：", "压力：", "创伤：", "自控：", "诱惑：",
        "Pain:", "Arousal:", "Fatigue:", "Stress:", "Trauma:", "Control:", "Allure:",
        "身体", "头部", "性格",
        "Body", "Head", "Personality",
        "生殖器：", "Genitals:"]
for k in KEYS:
    o = o_g.count(k)
    n = n_g.count(k)
    mark = "" if o == n else ("  ← 新包减少" if n < o else "  ← 新包增加")
    print(f"  {k:<14} 昨天 {o:>5}   现在 {n:>5}{mark}")

print("\n" + "=" * 94)
print("模组列表对比")
print("=" * 94)
import base64
import io
import json


def mods(path):
    z = zipfile.ZipFile(path)
    raw = z.read("assets/www/index.html")
    j = raw.find(b"[", raw.find(b"window.modDataValueZipList"))
    k = raw.find(b"]", j)
    parts = re.findall(r'"([A-Za-z0-9+/=\s]+)"', raw[j + 1:k].decode("utf-8", "replace"))
    out = []
    for s in parts:
        b = base64.b64decode(re.sub(r"\s+", "", s))
        if b[:2] != b"PK":
            continue
        try:
            zz = zipfile.ZipFile(io.BytesIO(b))
            if "boot.json" not in zz.namelist():
                continue
            bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
            out.append(bj.get("name") or "?")
        except Exception:
            pass
    return out


om = mods(OLD)
nm = mods(NEW)
print(f"  昨天 {len(om)} 个，现在 {len(nm)} 个")
print(f"\n  昨天有、现在没有: {sorted(set(om) - set(nm))}")
print(f"  现在有、昨天没有: {sorted(set(nm) - set(om))}")
