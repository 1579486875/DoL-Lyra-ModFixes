"""变量名对比（只取 ASCII，避免误报）。"""
import html
import re
import zipfile
from collections import Counter

MOD = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"


def load(p):
    z = zipfile.ZipFile(p)
    return html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))


mg = load(MOD)
vg = load(VAN)

VAR_RE = re.compile(r"\$([A-Za-z_][A-Za-z0-9_]*)")


def vars_of(g):
    t = re.sub(r"<script\b.*?</script>", " ", g, flags=re.S | re.I)
    t = re.sub(r"/\*.*?\*/", " ", t, flags=re.S)
    t = re.sub(r"/%.*?%/", " ", t, flags=re.S)
    return Counter(VAR_RE.findall(t))


mv = vars_of(mg)
vv = vars_of(vg)

print(f"变量: modded {len(mv)} / vanilla {len(vv)}")

only = sorted(set(mv) - set(vv), key=lambda x: -mv[x])
onlyv = sorted(set(vv) - set(mv), key=lambda x: -vv[x])

print(f"\nmodded 独有变量: {len(only)} 种")
for k in only[:25]:
    m = VAR_RE.search(r"$" + k, mg) if False else None
    ctx = ""
    mm = re.search(r"\$" + re.escape(k) + r"\b", mg)
    if mm:
        ctx = repr(mg[max(0, mm.start() - 60):mm.start() + 60])
    print(f"  ${k:<32} ×{mv[k]:>4}  {ctx}")

print(f"\nvanilla 独有变量: {len(onlyv)} 种")
for k in onlyv[:20]:
    print(f"  ${k:<32} ×{vv[k]:>4}")
