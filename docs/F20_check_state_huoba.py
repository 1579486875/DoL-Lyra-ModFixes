"""F20（第16轮）：查 state火把 的剩余 2 处。"""
import html as H
import re

HTML = r"E:\TAML\_dol\work\index_modded6.html"
g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))

print("=" * 90)
print("state火把 的所有出现")
print("=" * 90)
for m in re.finditer(r"state火把", g):
    print(f"\n@{m.start()}")
    print(f"  {g[max(0,m.start()-250):m.start()+250]!r}")

print("\n" + "=" * 90)
print("模板字符串里「属性+中文」的全量（真 bug）")
print("=" * 90)
TICK = chr(96)
n = 0
for m in re.finditer(TICK + "[^" + TICK + "]*" + TICK, g):
    tpl = m.group(0)
    # 只在 ${...} 外找 .xxx中文
    in_expr = 0
    i = 0
    while i < len(tpl):
        if tpl.startswith("${", i):
            in_expr += 1
            i += 2
            continue
        if tpl[i] == "}" and in_expr > 0:
            in_expr -= 1
            i += 1
            continue
        if in_expr == 0:
            mm = re.match(r"\.([A-Za-z_$][A-Za-z0-9_$]*)([\u4e00-\u9fff]+)", tpl[i:])
            if mm:
                n += 1
                if n <= 15:
                    print(f"  ❌ {mm.group(0)!r}")
                    print(f"     模板片段: {tpl[max(0,i-60):i+80]!r}")
                i += len(mm.group(0))
                continue
        i += 1
print(f"\n  共 {n} 处")
