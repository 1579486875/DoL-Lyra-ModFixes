"""找所有「调用了但不存在」的宏（modded 独有）。

flight_text 就是这类问题，需要全量排查。
"""
import html
import re
import zipfile
from collections import Counter

MOD = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"

# SugarCube 2.36 内置宏（含 DoL 自定义的）
BUILTIN = set("""
if elseif else unless switch case default break continue
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
done
addclass removeclass toggleclass
copy
number
checkbox
cycle
once
setting
version
config
debug
story
""".split())


def load(p):
    z = zipfile.ZipFile(p)
    raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    g = html.unescape(raw)
    blocks = {}
    for m in re.finditer(r'<tw-passagedata([^>]*)>(.*?)</tw-passagedata>', raw, re.S):
        nm = re.search(r'name="([^"]+)"', m.group(1))
        if nm:
            blocks[html.unescape(nm.group(1))] = html.unescape(m.group(2))
    return g, blocks


mg, mb = load(MOD)
vg, vb = load(VAN)


def defined_macros(g, blocks):
    d = set()
    for b in blocks.values():
        d |= set(re.findall(r'<<widget\s+"([^"]+)"', b))
    # 也有 Macro.add 注册的
    d |= set(re.findall(r'Macro\.add\(\s*["\']([^"\']+)["\']', g))
    d |= set(re.findall(r'DefineMacro\(\s*["\']([^"\']+)["\']', g))
    return d


def called_macros(g):
    # 去掉 <script> 和注释
    t = re.sub(r"<script\b.*?</script>", " ", g, flags=re.S | re.I)
    t = re.sub(r"/\*.*?\*/", " ", t, flags=re.S)
    t = re.sub(r"/%.*?%/", " ", t, flags=re.S)
    return Counter(re.findall(r"<<([A-Za-z_][\w-]*)", t))


m_def = defined_macros(mg, mb)
v_def = defined_macros(vg, vb)
m_call = called_macros(mg)
v_call = called_macros(vg)

print(f"定义: modded {len(m_def)} / vanilla {len(v_def)}")
print(f"调用: modded {len(m_call)} / vanilla {len(v_call)}")

m_missing = set(m_call) - m_def - BUILTIN
v_missing = set(v_call) - v_def - BUILTIN

print("\n" + "=" * 88)
print(f"modded 调用了但不存在的宏: {len(m_missing)} 种")
print("=" * 88)
only = sorted(m_missing - v_missing, key=lambda x: -m_call[x])
print(f"\nmodded 独有（{len(only)} 种）—— 才是我们引入的：")
for x in only:
    print(f"  {x:<28} 调用 {m_call[x]:>4} 次")
    # 找引用处
    for m in list(re.finditer(r"<<" + re.escape(x) + r"\b", mg))[:2]:
        ctx = mg[max(0, m.start() - 80):m.start() + 80]
        print(f"      {ctx!r}")

print(f"\n两边都有（{len(m_missing & v_missing)} 种）—— 原版问题：")
for x in sorted(m_missing & v_missing):
    print(f"  {x:<28} modded {m_call[x]:>4} / vanilla {v_call.get(x, 0):>4}")
