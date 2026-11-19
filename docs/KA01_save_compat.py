"""第 1-6 轮：存档兼容性审计。

检查：
  1) 模组新增的 $ 变量有无初始化（老存档进入会 undefined）
  2) setup.* 新表是否在 Widgets variablesStatic / StoryInit 里定义
  3) 变量被读了但从未 <<set>> 的（且不是 V.xxx 别名）
  4) 存档迁移分支（$version.schema）覆盖情况
"""
import base64
import html
import io
import json
import re
import zipfile
from collections import Counter, defaultdict

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VANILLA = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"

z = zipfile.ZipFile(APK)
raw = z.read("assets/www/index.html")
g = html.unescape(raw.decode("utf-8", "replace"))


def load_blocks(apk):
    zz = zipfile.ZipFile(apk)
    r = zz.read("assets/www/index.html").decode("utf-8", "replace")
    out = {}
    for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', r, re.S):
        out[html.unescape(m.group(1))] = html.unescape(m.group(2))
    return out


vb = load_blocks(VANILLA)
mb = load_blocks(APK)

print("=" * 94)
print("第 1 轮：模组新增 passage（相对 vanilla）")
print("=" * 94)
new_ps = set(mb) - set(vb)
print(f"  新增 passage: {len(new_ps)}")
print(f"  丢失 passage: {len(set(vb) - set(mb))}")

print("\n" + "=" * 94)
print("第 2 轮：模组新增的 $ 变量及其初始化情况")
print("=" * 94)
VAR = re.compile(r"\$([A-Za-z_][A-Za-z0-9_]{2,40})")


def collect(blocks):
    sets, reads = Counter(), Counter()
    for b in blocks.values():
        for m in re.finditer(r"<<set\s+\$([A-Za-z_]\w*)\s+(?:to|\+=|-=|\*=|/=|=)", b):
            sets[m.group(1)] += 1
        for m in re.finditer(r"<<run\s+\$([A-Za-z_]\w*)\s*=", b):
            sets[m.group(1)] += 1
        for m in VAR.finditer(b):
            reads[m.group(1)] += 1
    return sets, reads


vset, vread = collect(vb)
mset, mread = collect(mb)

new_vars = {v for v in mread if v not in vread}
print(f"  modded 新增变量: {len(new_vars)}")
risky = []
for v in sorted(new_vars):
    if mset.get(v, 0) == 0:
        risky.append((v, mread[v]))
print(f"  其中从未 <<set>> 的: {len(risky)}")
for v, c in sorted(risky, key=lambda x: -x[1])[:20]:
    print(f"    ${v:<28} 读 {c:>4} 次  ❌ 无初始化")

print("\n" + "=" * 94)
print("第 3 轮：vanilla 里就有的『只读不写』变量（可能是 V.xxx 别名，误报）")
print("=" * 94)
vrisky = [(v, vread[v]) for v in vread if vset.get(v, 0) == 0 and vread[v] >= 5]
print(f"  vanilla 只读不写: {len(vrisky)}")
for v, c in sorted(vrisky, key=lambda x: -x[1])[:12]:
    print(f"    ${v:<28} 读 {c:>5}")

print("\n" + "=" * 94)
print("第 4 轮：setup.* 定义位置")
print("=" * 94)
setup_defs = Counter()
for pn, b in mb.items():
    for m in re.finditer(r"<<set\s+setup\.([A-Za-z_]\w*)\s+to", b):
        setup_defs[(m.group(1), pn)] += 1
where = defaultdict(list)
for (name, pn), c in setup_defs.items():
    where[name].append(pn)
critical = ["NPCTypeList_cn_name", "NPCNameList_cn_name", "NPCTitleList_cn_name",
            "majorAreas_cn_name", "CafeFoodList_cn_name", "bodyShapescn",
            "faceVariantOptions", "faceStyleOptions", "crimeNames"]
for c in critical:
    print(f"  setup.{c:<28} 定义于 {where.get(c, ['❌ 无'])}")

print("\n" + "=" * 94)
print("第 5 轮：$version.schema 迁移分支")
print("=" * 94)
mig = re.findall(r"\$version\.schema\s+lt\s+(\d+)", g)
print(f"  迁移判断: {sorted(set(mig))}")
cur = re.findall(r"<<set\s+\$version\.schema\s+to\s+(\d+)", g)
print(f"  当前 schema: {sorted(set(cur))}")

print("\n" + "=" * 94)
print("第 6 轮：模组脚本里的 $ 变量是否在 StoryInit 有默认值")
print("=" * 94)
# 找模组 scriptFileList 里的 V.xxx = 赋值
j = raw.find(b"[", raw.find(b"window.modDataValueZipList"))
k = raw.find(b"]", j)
parts = re.findall(r'"([A-Za-z0-9+/=\s]+)"', raw[j + 1:k].decode("utf-8", "replace"))
mod_vars = defaultdict(set)
for s in parts:
    b = base64.b64decode(re.sub(r"\s+", "", s))
    if b[:2] != b"PK":
        continue
    zz = zipfile.ZipFile(io.BytesIO(b))
    if "boot.json" not in zz.namelist():
        continue
    bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
    name = bj.get("name") or "?"
    for f in bj.get("scriptFileList") or []:
        try:
            t = zz.read(f).decode("utf-8", "ignore")
        except Exception:
            continue
        for m in re.finditer(r"\bV\.([A-Za-z_]\w*)\s*=", t):
            mod_vars[name].add(m.group(1))
print(f"  在脚本里给 V.* 赋值的模组: {len(mod_vars)}")
for name, vs in list(mod_vars.items())[:10]:
    print(f"    [{name}] {sorted(vs)[:8]}")
