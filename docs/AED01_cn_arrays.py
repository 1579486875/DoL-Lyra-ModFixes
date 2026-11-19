"""找所有「中文数组被 charAt/indexOf/includes 当键用」的地方。

_bodyTypes 就是这种：["男性化",...].charAt(0) -> "男"，但代码要 "m"。
"""
import html
import re
import zipfile

MOD = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"

CJK = re.compile(r"[\u4e00-\u9fff]")


def load(p):
    z = zipfile.ZipFile(p)
    return html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))


mg = load(MOD)
vg = load(VAN)

# 1) 找含中文的字符串数组
print("=" * 88)
print("含中文的字符串数组（可能是显示用，也可能是键）")
print("=" * 88)
arrs = []
for m in re.finditer(r'\[((?:\s*"[^"]*"\s*,?)+)\]', mg):
    body = m.group(1)
    if CJK.search(body) and body.count('"') >= 4:
        arrs.append((m.start(), m.group(0)))

print(f"  共 {len(arrs)} 个")
for pos, a in arrs[:15]:
    ctx = mg[max(0, pos - 120):pos + len(a) + 120]
    print(f"\n  @{pos} {a[:90]}")
    print(f"    上下文: {ctx[100:340]!r}")

# 2) 关键：找 charAt/indexOf/includes 作用在数组上的
print("\n" + "=" * 88)
print("charAt(0) 作用在变量上（高风险）")
print("=" * 88)
for m in list(re.finditer(r"(\w+)\.charAt\(0\)", mg))[:30]:
    var = m.group(1)
    ctx = mg[max(0, m.start() - 150):m.start() + 150]
    # 只看中文相关的
    if CJK.search(ctx):
        print(f"\n  {var}.charAt(0)")
        print(f"    {ctx!r}")

# 3) 对比 vanilla：找 modded 把英文数组换成中文的
print("\n" + "=" * 88)
print("modded 里含中文的数组 vs vanilla 同位置")
print("=" * 88)
# 提取 vanilla 的所有字符串数组
va = {}
for m in re.finditer(r'\[((?:\s*"[^"]*"\s*,?)+)\]', vg):
    body = m.group(1)
    if not CJK.search(body) and body.count('"') >= 4:
        # 用长度和首项做 key
        items = re.findall(r'"([^"]*)"', body)
        if items:
            va[tuple(items)] = m.group(0)

print(f"  vanilla 英文数组: {len(va)} 个")

# 找 modded 里「长度相同但内容全中文」的数组
ma = []
for m in re.finditer(r'\[((?:\s*"[^"]*"\s*,?)+)\]', mg):
    body = m.group(1)
    items = re.findall(r'"([^"]*)"', body)
    if items and CJK.search(body) and not any(re.match(r'^[A-Za-z0-9_\- ]+$', x) for x in items):
        ma.append((m.start(), items, body))

print(f"  modded 全中文数组: {len(ma)} 个")
print("\n  前 20 个：")
for pos, items, body in ma[:20]:
    ctx = mg[max(0, pos - 100):pos + len(body) + 100]
    print(f"    {items[:5]}  ←  {ctx[90:260]!r}")
