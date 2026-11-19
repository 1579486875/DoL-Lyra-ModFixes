"""第 13-20 轮：运行时未定义符号。

检查：
  A) setup.xxx 被引用但从未定义
  B) 宏 <<xxx>> 被调用但从未定义（排除 SugarCube 内置）
  C) <<include>> 目标不存在
  D) <<optionsfrom>> 参数是 undefined 风险
  E) $var 在 <<if>> 里被读但从未被赋值（粗筛）
"""
import html
import re
import zipfile
from collections import Counter, defaultdict

MOD = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"

# SugarCube 内置宏
BUILTIN = set("""
if elseif else unless switch case default for break continue
set run print =
link button include display replace append prepend remove
silently nobr capture widget script stylesheet
textbox textarea numberbox listbox radiobutton checkbox
optionsfrom remember
goto display back return
timed continue
type typewriter
audio cacheaudio masteraudio track
createplaylist playlist masterplaylist
setplaylist stopsoundstop
click undo redo
save restore restart
meter bar
icon
nobr
done
silently
""".split())


def load(p):
    z = zipfile.ZipFile(p)
    raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    out = {}
    for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
        b = html.unescape(m.group(2))
        for pat in (r"/\*.*?\*/", r"<!--.*?-->", r"/%.*?%/"):
            b = re.sub(pat, " ", b, flags=re.S)
        out[html.unescape(m.group(1))] = b
    return html.unescape(raw), out


mg, mb = load(MOD)
vg, vb = load(VAN)


def check_setup(raw, blocks, label):
    print("=" * 90)
    print(f"A) setup.xxx 引用 vs 定义  [{label}]")
    print("=" * 90)
    refs = set(re.findall(r"setup\.(\w+)", raw))
    # 定义方式：<<set setup.x to/=>>、setup.x =、setup["x"]=
    defs = set(re.findall(r"<<set\s+setup\.(\w+)\s*(?:to|=)", raw))
    defs |= set(re.findall(r"setup\.(\w+)\s*=[^=]", raw))
    defs |= set(re.findall(r'setup\[\s*["\'](\w+)["\']\s*\]\s*=', raw))
    # 内置
    defs |= {"test", "history"}
    missing = sorted(refs - defs)
    print(f"  引用 {len(refs)}，定义 {len(defs)}，缺失 {len(missing)}")
    for m in missing[:30]:
        print(f"    {m}")
    return set(missing)


m_missing = check_setup(mg, mb, "modded")
print()
v_missing = check_setup(vg, vb, "vanilla")

print("\n" + "=" * 90)
print("A2) modded 独有的缺失（才是我们引入的）")
print("=" * 90)
only_mod = m_missing - v_missing
print(f"  {len(only_mod)} 个")
for x in sorted(only_mod):
    print(f"    {x}")
    # 找引用处
    for mm in list(re.finditer(r"setup\." + x + r"\b", mg))[:2]:
        print(f"      {mg[max(0,mm.start()-100):mm.start()+120]!r}")


def check_macros(raw, blocks, label):
    print("\n" + "=" * 90)
    print(f"B) 宏调用 vs 定义  [{label}]")
    print("=" * 90)
    defs = set(re.findall(r'<<widget\s+"([^"]+)"', raw))
    calls = set(re.findall(r"<<([A-Za-z_][\w]*)", raw))
    missing = sorted(calls - defs - BUILTIN)
    print(f"  定义 {len(defs)}，调用 {len(calls)}，未定义 {len(missing)}")
    for m in missing[:30]:
        print(f"    {m}")
    return set(missing), defs


m_mis, m_defs = check_macros(mg, mb, "modded")
print()
v_mis, v_defs = check_macros(vg, vb, "vanilla")

print("\n" + "=" * 90)
print("B2) modded 独有的未定义宏")
print("=" * 90)
only_mis = m_mis - v_mis
print(f"  {len(only_mis)} 个")
for x in sorted(only_mis):
    print(f"    {x}")
    for mm in list(re.finditer(r"<<" + x + r"\b", mg))[:2]:
        print(f"      {mg[max(0,mm.start()-100):mm.start()+120]!r}")

print("\n" + "=" * 90)
print("C) <<include>> 目标")
print("=" * 90)
for label, raw, blocks in (("modded", mg, mb), ("vanilla", vg, vb)):
    targets = set()
    for b in blocks.values():
        targets |= set(re.findall(r'<<include\s+"([^"]+)"', b))
        targets |= set(re.findall(r"<<include\s+([A-Za-z_][\w]*)", b))
    missing = sorted(t for t in targets if t not in blocks)
    print(f"  {label}: 目标 {len(targets)}，缺失 {len(missing)}  {missing}")
