"""逐行检查 Widgets Wraith 里所有 <<set>> / <<=>> / <<if>> 的引号与括号配对。"""
import html
import re
import zipfile

MOD = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"


def get(path, name):
    z = zipfile.ZipFile(path)
    raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
        if html.unescape(m.group(1)) == name:
            return html.unescape(m.group(2))
    return ""


def check(path, label, name):
    b = get(path, name)
    print("=" * 94)
    print(f"{label} / {name}  (长度 {len(b)})")
    print("=" * 94)

    problems = []
    # 逐个宏提取，检查引号是否成对
    for m in re.finditer(r"<<(set|run|print|=|if|elseif)\b", b):
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
        # 统计未转义的引号
        for q in ('"', "'", "`"):
            # 去掉转义
            cleaned = re.sub(r"\\" + re.escape(q), "", expr)
            n = cleaned.count(q)
            if n % 2 != 0:
                problems.append((m.group(1), expr[:160], f"{q} 数量 {n} 为奇数"))
                break

    if problems:
        print(f"  ❌ 发现 {len(problems)} 处引号不成对：")
        for name_, expr, why in problems[:15]:
            print(f"\n    <<{name_}>> {why}")
            print(f"      {expr!r}")
    else:
        print("  ✅ 所有宏的引号都成对")

    # 检查 <<widget>> 数量
    o = len(re.findall(r"<<widget\b", b))
    c = b.count("<</widget>>")
    print(f"\n  <<widget>> {o}/{c}")


check(VAN, "vanilla", "Widgets Wraith")
print()
check(MOD, "modded", "Widgets Wraith")
