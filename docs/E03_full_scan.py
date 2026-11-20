"""E03：全量导出剩余的「标识符被翻译」+「且」的所有形态。"""
import html as H
import json
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
raw = zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace")
g = H.unescape(raw)
CJK = "[\u4e00-\u9fff]"

print("=" * 100)
print("1) 所有「且」的出现（含上下文判断是否在代码里）")
print("=" * 100)
n_if = 0
for m in re.finditer(r"且", g):
    ctx = g[max(0, m.start() - 250):m.start() + 250]
    # 判断是否在 <<...>> 内
    before = g[:m.start()]
    last_open = before.rfind("<<")
    last_close = before.rfind(">>")
    in_macro = last_open > last_close
    if in_macro:
        n_if += 1
        # 提取所在宏
        macro_end = g.find(">>", m.start())
        macro_start = last_open
        macro = g[macro_start:macro_end + 2]
        # 挖掉字符串
        stripped = re.sub(r'"[^"]*"|\'[^\']*\'|`[^`]*`', '""', macro)
        if "且" in stripped:
            print(f"\n  ❌ 代码位置 @{m.start()}")
            print(f"     {macro[:250]!r}")
print(f"\n  宏内「且」总数: {n_if}")

print("\n" + "=" * 100)
print("2) 所有含全角标点的宏（，。：；！？）")
print("=" * 100)
for m in re.finditer(r"<<(if|elseif|set|run|switch|case|for|while|print)\b([^<>]{0,800}?)>>", g):
    body = m.group(2)
    stripped = re.sub(r'"[^"]*"|\'[^\']*\'|`[^`]*`', '""', body)
    # 正则字面量 /.../ 也是合法内容
    stripped2 = re.sub(r"/[^/\n]*/", '""', stripped)
    if re.search(r"[，。：；！？]", stripped2):
        print(f"\n  ⚠️ {m.group(0)[:250]!r}")

print("\n" + "=" * 100)
print("3) 所有 _下体。 / 类似的中文标识符残留")
print("=" * 100)
PATTERNS = [
    (r"_[A-Za-z0-9]*" + CJK + r"+[。，、]", "变量名+全角标点"),
    (r"\$[A-Za-z0-9]*" + CJK + r"+[。，、]", "$变量+全角标点"),
    (r"\.[" + CJK + r"]+[。，、]", ".属性+全角标点"),
    (r"C\.npc\.[" + CJK + r"]+", "C.npc.中文"),
]
for p, label in PATTERNS:
    hs = list(re.finditer(p, g))
    print(f"\n  {label}: {len(hs)}")
    seen = {}
    for m in hs:
        seen[m.group(0)] = seen.get(m.group(0), 0) + 1
    for t, c in sorted(seen.items(), key=lambda x: -x[1])[:15]:
        print(f"    {c:>3}x {t!r}")

print("\n" + "=" * 100)
print("4) d. 检查 danceaudience widget 的 <<if>>")
print("=" * 100)
m = re.search(r'<<widget "danceaudience">>(.*?)<</widget>>', g, re.S)
if m:
    body = m.group(1)
    print(f"  widget 长度 {len(body)}")
    for mm in re.finditer(r"<<if\b([^<>]{0,400})>>", body):
        b = mm.group(1)
        if "且" in b or "或" in b:
            print(f"    ❌ {mm.group(0)[:200]!r}")
        else:
            print(f"    {mm.group(0)[:150]!r}")
