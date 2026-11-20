"""R05：列出 <<script>>/<<run>> 里 4 处模板字符串粘连。"""
import html as H
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
g = H.unescape(zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace"))
TICK = chr(96)

JS = []
for m in re.finditer(r"<<script>>(.*?)<</script>>", g, re.S):
    JS.append(("script", m.start(), m.group(1)))
for m in re.finditer(r"<<run\b([^<>]{0,2000}?)>>", g):
    JS.append(("run", m.start(), m.group(1)))

print(f"扫描 {len(JS)} 个 JS 块")

n = 0
for kind, base, blk in JS:
    for m in re.finditer(TICK + "[^" + TICK + "\\n]{1,400}" + TICK, blk):
        tpl = m.group(0)
        in_expr = 0
        k = 0
        while k < len(tpl):
            if tpl.startswith("${", k):
                in_expr += 1
                k += 2
                continue
            if tpl[k] == "}" and in_expr > 0:
                in_expr -= 1
                k += 1
                continue
            if in_expr == 0:
                mm = re.match(r"\.([A-Za-z_$][A-Za-z0-9_$]{2,})([\u4e00-\u9fff]+)", tpl[k:])
                if mm:
                    n += 1
                    pos = base + m.start() + k
                    print(f"\n[{n}] {kind} @{pos}")
                    print(f"  匹配: {mm.group(0)!r}")
                    print(f"  模板: {tpl[:300]!r}")
                    print(f"  上下文: {g[max(0,pos-150):pos+250]!r}")
                    k += len(mm.group(0))
                    continue
            k += 1

print(f"\n共 {n} 处")

# 对照：这 4 处是不是我之前 F17 修的
print("\n" + "=" * 90)
print("F17 修的 3 处是否还在")
print("=" * 90)
for kw in ("nameText浇灭", "nameText中清洗", "state火把和它玩拔河"):
    print(f"  {kw!r}: {g.count(kw)}")
