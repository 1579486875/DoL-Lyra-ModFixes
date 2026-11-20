"""C03：导出全部 JS 硬编码英文（文件方式，避免 shell 转义）。"""
import html
import json
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
g = html.unescape(zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace"))
CJK = re.compile(r"[\u4e00-\u9fff]")


def ok(t):
    t = t.strip()
    if len(t) < 10 or len(t) > 400:
        return False
    if CJK.search(t):
        return False
    w = re.findall(r"[A-Za-z][A-Za-z']+", t)
    if len(w) < 3:
        return False
    if re.search(r"[{}`\\]|=>|function|var |const |let |return|undefined|typeof|this\.|null|\.prototype", t):
        return False
    if all(x[0].islower() for x in w) and len(w) < 5:
        return False
    # 排除 HTML 片段
    if re.search(r"<[a-z]+[\s>]", t) or "class=" in t:
        return False
    return True


PATTERNS = [
    ("element", re.compile(r'element\(\s*"[a-z]+"\s*,\s*"([^"]{10,400})"')),
    ("elementTpl", re.compile(r'element\(\s*"[a-z]+"\s*,\s*`([^`]{10,400})`')),
    ("textContent", re.compile(r'\.textContent\s*=\s*"([^"]{10,400})"')),
    ("innerHTML", re.compile(r'\.innerHTML\s*=\s*"([^"]{10,400})"')),
    ("append", re.compile(r'\.append\(\s*"([^"]{10,400})"\s*\)')),
    ("wiki", re.compile(r'\$\.wiki\(\s*"([^"]{10,400})"')),
    ("Wikifier", re.compile(r'new\s+Wikifier\(\s*[^,]+,\s*"([^"]{10,400})"')),
    ("link", re.compile(r'<<link\s+"([^"]{10,400})"\s*>>')),
    ("button", re.compile(r'<<button\s+"([^"]{10,400})"\s*>>')),
    ("print", re.compile(r'<<print\s+"([^"]{10,400})"')),
    ("eval2", re.compile(r'<<=\s*"([^"]{10,400})"')),
]

out = {}
for name, p in PATTERNS:
    for m in p.finditer(g):
        t = m.group(1)
        if not ok(t):
            continue
        out.setdefault(t, {"c": 0, "p": set(), "pos": m.start()})
        out[t]["c"] += 1
        out[t]["p"].add(name)

print("=" * 100)
print(f"共 {len(out)} 条")
print("=" * 100)
print()
for t, v in sorted(out.items(), key=lambda x: -x[1]["c"]):
    print(f"[{v['c']}x] ({','.join(sorted(v['p']))}) @{v['pos']}")
    print(f"    {t[:190]!r}")

with open(r"E:\TAML\_dol\work\_all_js_en.json", "w", encoding="utf-8") as f:
    json.dump({t: {"c": v["c"], "p": sorted(v["p"])} for t, v in out.items()},
              f, ensure_ascii=False, indent=1)
print(f"\n已保存 _all_js_en.json")
