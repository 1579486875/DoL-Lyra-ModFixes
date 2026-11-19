"""核查 A 组的 1 处「<<if>> 含 <<」，并与 vanilla 对比。"""
import html
import re
import zipfile

MODDED = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VANILLA = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"


def load(apk):
    z = zipfile.ZipFile(apk)
    raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    out = {}
    for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
        out[html.unescape(m.group(1))] = html.unescape(m.group(2))
    return out


mb = load(MODDED)
vb = load(VANILLA)

TARGET = "Bully Spitroast 3"
print("=" * 94)
print(f"{TARGET} 里的 <<if>>")
print("=" * 94)
for name, blocks in (("modded", mb), ("vanilla", vb)):
    b = blocks.get(TARGET, "")
    print(f"\n--- {name} (长度 {len(b)}) ---")
    # 找含 << 的 if
    cnt = 0
    for m in re.finditer(r"<<if\b", b):
        # 往后找配对的 >>（考虑嵌套）
        i = m.end()
        depth = 1
        while i < len(b) and depth > 0:
            if b.startswith("<<", i):
                depth += 1
                i += 2
                continue
            if b.startswith(">>", i):
                depth -= 1
                i += 2
                continue
            i += 1
        expr = b[m.end():i - 2]
        if "<<" in expr:
            cnt += 1
            print(f"  ⚠️ {b[m.start():m.start()+400]!r}")
    if cnt == 0:
        print("  ✅ 无「<<if>> 内含 <<」")

print("\n" + "=" * 94)
print("全库用「配对大括号扫描」重新统计（更准）")
print("=" * 94)


def scan_bad_if(blocks):
    bad = []
    for pn, b in blocks.items():
        for m in re.finditer(r"<<(if|elseif|unless|while)\b", b):
            i = m.end()
            depth = 1
            while i < len(b) and depth > 0:
                if b.startswith("<<", i):
                    depth += 1
                    i += 2
                elif b.startswith(">>", i):
                    depth -= 1
                    i += 2
                else:
                    i += 1
            expr = b[m.end():i - 2]
            # 去掉字符串字面量再判断
            e = re.sub(r'"[^"]*"', '""', expr)
            e = re.sub(r"'[^']*'", "''", e)
            e = re.sub(r"`[^`]*`", "``", e)
            if "<<" in e:
                bad.append((pn, m.group(1), expr[:120]))
    return bad


mb_bad = scan_bad_if(mb)
vb_bad = scan_bad_if(vb)
print(f"  modded: {len(mb_bad)} 处")
for x in mb_bad[:10]:
    print(f"    [{x[0]}] <<{x[1]} {x[2]!r}")
print(f"  vanilla: {len(vb_bad)} 处")
for x in vb_bad[:10]:
    print(f"    [{x[0]}] <<{x[1]} {x[2]!r}")

print("\n" + "=" * 94)
print("结论")
print("=" * 94)
new_bad = {x[0] for x in mb_bad} - {x[0] for x in vb_bad}
print(f"  modded 独有（我引入的）: {len(new_bad)}")
for x in sorted(new_bad):
    print(f"    {x}")
