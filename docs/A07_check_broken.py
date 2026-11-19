"""A07：紧急排查 —— 当前包是否坏了，坏到什么程度，回滚到哪个包。"""
import hashlib
import html
import os
import re
import zipfile

OUT = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
ARCHIVE = r"E:\TAML\_dol\archive"


def check(path):
    z = zipfile.ZipFile(path)
    raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    n_raw = len(re.findall(r"<tw-passagedata", raw))
    n_esc = len(re.findall(r"&lt;tw-passagedata", raw))
    g = html.unescape(raw)
    n_un = len(re.findall(r"<tw-passagedata", g))
    return {
        "size": os.path.getsize(path),
        "raw_passages": n_raw,
        "escaped_passages": n_esc,
        "unescaped_passages": n_un,
        "head": raw[:60],
    }


print("=" * 100)
print("当前包")
print("=" * 100)
r = check(OUT)
h = hashlib.sha256(open(OUT, "rb").read()).hexdigest().upper()
for k, v in r.items():
    print(f"  {k}: {v}")
print(f"  SHA256: {h}")
print(f"  判定: {'❌ 坏的（passage 全被转义）' if r['raw_passages'] == 0 else '✅ 正常'}")

print("\n" + "=" * 100)
print("归档里最近 10 个包的 passage 状态")
print("=" * 100)
ars = sorted((f for f in os.listdir(ARCHIVE) if f.endswith(".apk")),
             key=lambda x: os.path.getmtime(os.path.join(ARCHIVE, x)), reverse=True)
for a in ars[:10]:
    p = os.path.join(ARCHIVE, a)
    try:
        rr = check(p)
        hh = hashlib.sha256(open(p, "rb").read()).hexdigest().upper()[:12]
        mark = "✅" if rr["raw_passages"] > 10000 else "❌"
        print(f"  {mark} {rr['raw_passages']:>6} passages  {hh}  {a[:70]}")
    except Exception as e:
        print(f"  ERR {a[:60]}: {e}")
