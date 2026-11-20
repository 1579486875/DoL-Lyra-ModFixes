"""F05（第5轮）：多维度深挖。

1. sugarCube 关键字被翻译（is/isnot/gte/lte/to/and/or/not/true/false）
2. $变量名含中文
3. setup.xxx 函数引用是否都存在
4. 宏名是否都注册了
5. passage 名重复
6. <<widget>> 重复定义
7. 中文里嵌的英文单词（玩家可见文本）
"""
import html as H
import re
import zipfile
from collections import Counter, defaultdict

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
raw = zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace")
g = H.unescape(raw)
TICK = chr(96)

PASSAGES = {}
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
    PASSAGES[m.group(1)] = H.unescape(m.group(2))


def strip_lit(s):
    s = re.sub(r'"[^"]*"', lambda m: " " * len(m.group(0)), s)
    s = re.sub(r"'[^']*'", lambda m: " " * len(m.group(0)), s)
    s = re.sub(TICK + "[^" + TICK + "]*" + TICK, lambda m: " " * len(m.group(0)), s)
    return re.sub(r"/[^/\n]*/", lambda m: " " * len(m.group(0)), s)


print("=" * 100)
print("1) SugarCube 关键字被翻译")
print("=" * 100)
CN_KW = {"且": "and", "或": "or", "不是": "isnot", "等于": "is", "大于等于": "gte",
         "小于等于": "lte", "大于": "gt", "小于": "lt", "真": "true", "假": "false",
         "未定义": "undefined", "并且": "and", "至": "to", "到": "to"}
hits = defaultdict(list)
for m in re.finditer(r"<<(if|elseif|set|run|switch|case|for|while)\b([^<>]{0,800}?)>>", g):
    body = strip_lit(m.group(2))
    for cn, en in CN_KW.items():
        if re.search(r"(?<![A-Za-z0-9_])" + re.escape(cn) + r"(?![A-Za-z0-9_])", body):
            hits[cn].append((m.group(0)[:150], en))
for cn, lst in hits.items():
    print(f"  ❌ {cn!r} (应为 {lst[0][1]}): {len(lst)} 处")
    for txt, _ in lst[:3]:
        print(f"      {txt!r}")
if not hits:
    print("  ✅ 无")

print("\n" + "=" * 100)
print("2) $变量名 / _变量名 含中文")
print("=" * 100)
n = 0
for m in re.finditer(r"[$_][A-Za-z0-9_]*[\u4e00-\u9fff]+[A-Za-z0-9_]*", g):
    n += 1
    if n <= 10:
        print(f"  {m.group(0)!r} @{m.start()}")
        print(f"    {g[max(0,m.start()-100):m.start()+100]!r}")
print(f"  共 {n} 处（多数是 变量名+中文文本 紧邻，正常）")

print("\n" + "=" * 100)
print("3) setup.xxx 函数引用检查")
print("=" * 100)
# 收集所有 setup.xxx 引用
refs = Counter()
for m in re.finditer(r"\bsetup\.([A-Za-z_][A-Za-z0-9_]*)", g):
    refs[m.group(1)] += 1
print(f"  setup.* 引用 {len(refs)} 个不同名")

# 收集 setup 上的定义
defined = set()
for m in re.finditer(r"<<set\s+setup\.([A-Za-z_][A-Za-z0-9_]*)\s+to\b", g):
    defined.add(m.group(1))
for m in re.finditer(r"\bsetup\.([A-Za-z_][A-Za-z0-9_]*)\s*=", g):
    defined.add(m.group(1))
for m in re.finditer(r"\bsetup\.([A-Za-z_][A-Za-z0-9_]*)\s*:", g):
    defined.add(m.group(1))
print(f"  setup.* 定义 {len(defined)} 个")

# 函数调用形式 setup.xxx(...) 但没定义
CALL = Counter()
for m in re.finditer(r"\bsetup\.([A-Za-z_][A-Za-z0-9_]*)\s*\(", g):
    CALL[m.group(1)] += 1
undef = [k for k in CALL if k not in defined]
print(f"  setup.xxx(...) 调用 {len(CALL)} 个不同名")
print(f"  未在 index 里定义: {len(undef)}")
for k in sorted(undef)[:20]:
    print(f"    {k}  ({CALL[k]} 次)")

print("\n" + "=" * 100)
print("4) 宏名注册检查")
print("=" * 100)
# <<xxx>> 用法
used = Counter()
for m in re.finditer(r"<<\s*([A-Za-z_][A-Za-z0-9_\-]*)\b", g):
    used[m.group(1).lower()] += 1
# 定义
defined_macros = set()
for m in re.finditer(r'<<widget\s+"([^"]+)"', g):
    defined_macros.add(m.group(1).lower())
for m in re.finditer(r'Macro\.add\(\s*"([^"]+)"', g):
    defined_macros.add(m.group(1).lower())
# SugarCube 内建
BUILTIN = set("""if elseif else for while until switch case default break continue
set run print = include display goto link button checkbox radiobutton textbox textarea
listbox cycle option optionsfrom repeat timed silent silently nobr capture replace
append prepend remove removeclass addclass toggleclass copy to clipboard audio
cacheaudio playlist mastervolume save load restart title history undo redo
back forward return widget script style endwidget endscript endstyle
class id draggable droppable sortable slider mouseover mouseout click dblclick
keydown keyup keypress focus blur change submit reset
either random visited visitedtags tags hasvisited previous next
brokenlink nobrokenlink storytitle storyready actions
""".split())
unknown = [(k, v) for k, v in used.items() if k not in defined_macros and k not in BUILTIN]
unknown.sort(key=lambda x: -x[1])
print(f"  使用 {len(used)} 个不同宏名")
print(f"  未注册（可能自定义 macro 或拼写错误）: {len(unknown)}")
for k, v in unknown[:25]:
    print(f"    <<{k}>>  {v} 次")

print("\n" + "=" * 100)
print("5) passage 名重复")
print("=" * 100)
all_names = re.findall(r'<tw-passagedata[^>]*name="([^"]*)"', raw)
dup = {k: v for k, v in Counter(all_names).items() if v > 1}
print(f"  {'✅ 无重复' if not dup else f'❌ {len(dup)} 个重复'}")
for k, v in list(dup.items())[:10]:
    print(f"    {k!r} × {v}")

print("\n" + "=" * 100)
print("6) <<widget>> 重复定义")
print("=" * 100)
wd = Counter(re.findall(r'<<widget\s+"([^"]+)"', g))
wdup = {k: v for k, v in wd.items() if v > 1}
print(f"  {'✅ 无重复' if not wdup else f'❌ {len(wdup)} 个重复'}")
for k, v in list(wdup.items())[:15]:
    print(f"    {k!r} × {v}")
