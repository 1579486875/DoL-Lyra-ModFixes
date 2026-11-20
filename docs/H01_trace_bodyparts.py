"""H01：彻底摸清 BODYPARTS_CN_NAME 的所有定义与执行时序。"""
import html as H
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
raw = zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace")
g = H.unescape(raw)

print("=" * 95)
print("1. 所有 BODYPARTS_CN_NAME 出现位置")
print("=" * 95)
for m in re.finditer(r"BODYPARTS_CN_NAME", g):
    ctx = g[max(0, m.start() - 120):m.start() + 120]
    kind = "定义" if re.search(r"(st|setup)\.BODYPARTS_CN_NAME\s*=", ctx) else "引用/其它"
    print(f"  @{m.start():>9}  [{kind}]  {ctx[:150]!r}")

print("\n" + "=" * 95)
print("2. 每个定义所属的 <script> 块与执行时机")
print("=" * 95)
# 找所有 script 块
blocks = []
for m in re.finditer(r"<<script>>(.*?)<</script>>", g, re.S):
    blocks.append((m.start(), m.end(), m.group(1)))
print(f"  共 {len(blocks)} 个 <<script>> 块")

for m in re.finditer(r"(st|setup)\.BODYPARTS_CN_NAME\s*=", g):
    pos = m.start()
    owner = None
    for bs, be, body in blocks:
        if bs <= pos <= be:
            owner = (bs, be, len(body))
            break
    if owner:
        # 该块是否在 widget 里
        pre = g[max(0, owner[0] - 400):owner[0]]
        wm = re.search(r'<<widget "([^"]+)"', pre)
        widget = wm.group(1) if wm else "(非 widget，顶层)"
        print(f"  @{pos:>9}  <- script 块 {owner[0]}~{owner[1]} (len {owner[2]})  widget={widget}")
    else:
        print(f"  @{pos:>9}  <- **不在任何 <<script>> 块里**")

print("\n" + "=" * 95)
print("3. 块外执行 vs 块内（判断谁最后跑）")
print("=" * 95)
# <<script>> 在 passage 渲染时执行；不在块内的裸 JS 在页面加载时执行
first = g.find("st.BODYPARTS_CN_NAME = mk(")
second = g.find("st.BODYPARTS_CN_NAME = function (x)")
print(f"  第一个定义（mk）  @{first}")
print(f"  第二个定义（内联）@{second}")

# 第二个是否在 script 块内
for bs, be, body in blocks:
    if bs <= second <= be:
        pre = g[max(0, bs - 500):bs]
        wm = re.search(r'<<widget "([^"]+)"', pre)
        print(f"  第二个在 script 块 {bs}~{be}  widget={wm.group(1) if wm else '?'}")
        # 该 widget 被调用过吗
        if wm:
            wname = wm.group(1)
            calls = len(re.findall(r'<<' + re.escape(wname) + r'\b', g))
            print(f"    该 widget 被调用 {calls} 次")
        break

print("\n" + "=" * 95)
print("4. 两个定义所在的 widget 是否真的会被执行")
print("=" * 95)
for bs, be, body in blocks:
    if "BODYPARTS_CN_NAME" in body:
        pre = g[max(0, bs - 600):bs]
        wm = re.search(r'<<widget "([^"]+)"', pre)
        if not wm:
            continue
        wname = wm.group(1)
        # 该 widget 的调用次数（排除定义本身）
        calls = len(re.findall(r'<<' + re.escape(wname) + r'(?:\s|>>)', g)) - 1
        print(f"  widget {wname!r}  被调用 {calls} 次")
