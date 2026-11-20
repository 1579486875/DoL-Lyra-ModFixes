"""R03：列出 12 处模板字符串粘连。"""
import html as H
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
g = H.unescape(zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace"))
TICK = chr(96)

n = 0
for m in re.finditer(TICK + "[^" + TICK + "\\n]{1,400}" + TICK, g):
    tpl = m.group(0)
    if "\n" in tpl:
        continue
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
                print(f"\n[{n}] @{m.start()}")
                print(f"  匹配: {mm.group(0)!r}")
                print(f"  模板: {tpl[:250]!r}")
                print(f"  上下文: {g[max(0,m.start()-150):m.start()+250]!r}")
                k += len(mm.group(0))
                continue
        k += 1

print(f"\n共 {n} 处")
