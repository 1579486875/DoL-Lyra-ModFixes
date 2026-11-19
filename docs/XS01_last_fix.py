"""修最后一轮：
  1) regress.py 的 either 检测只检查 <<...>> 宏内的调用
  2) 补最后 3 个 displayName
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
REGRESS = r"E:\TAML\_dol\work\regress.py"

LAST_DN = {
    "Starting season:": "起始季节：",
    "Game difficulty:": "游戏难度：",
    "Ironman mode:": "铁人模式：",
    "Natural Skintone:": "自然肤色：",
    "Freckles:": "雀斑：",
    "Cost of lewd clothes:": "淫秽衣物价格：",
    "Cost of school clothes:": "校服价格：",
    "Cost of underwear:": "内衣价格：",
    "Mouth:": "口腔：",
    "Hands:": "手部：",
    "Nipples:": "乳头：",
    "Penis:": "阴茎：",
    "Vagina:": "阴道：",
    "Anus:": "肛门：",
    "Thighs:": "大腿：",
    "Feet:": "足部：",
}


def fix_dn():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    total = 0
    for en, cn in LAST_DN.items():
        a = f'displayName: "{en}"'
        b = f'displayName: "{cn}"'
        if a in data:
            n = data.count(a)
            data = data.replace(a, b)
            total += n
            print(f"  ✅ {en!r} -> {cn!r} ({n})")
    if total:
        open(HTML, "wb").write(data.encode("utf-8"))
        print(f"  合计 {total} 处")
    else:
        print("  （无改动）")
    g = H.unescape(data)
    remain = sorted(set(re.findall(r'displayName:\s*"([A-Za-z][^"]{1,60})"', g)))
    print(f"\n剩余英文 displayName: {len(remain)}")


def fix_regress():
    s = open(REGRESS, encoding="utf-8").read()

    # 定位 either 检测块并整体替换
    start = s.find('    # 9 either() 全角逗号')
    if start < 0:
        start = s.find('    n = 0\n    for m in re.finditer(r"either\\\\("')
    if start < 0:
        print("  ⚠️ 未找到 either 检测块，尝试按内容定位")
        i = s.find('either(')
        print(f"  首个 either 出现位置: {i}")
        return

    end = s.find('(ok if n == 0 else bad)("[9] either() 参数无全角逗号"', start)
    if end < 0:
        print("  ⚠️ 未找到检测块结尾")
        return
    end = s.find("\n", end) + 1

    NEW = '''    # 9 either() 全角逗号 —— 只检查宏内的调用（JS 里的 either(a,b) 不算）
    n = 0
    for mm in re.finditer(r"<<[^>]{0,600}?>>", g):
        macro = mm.group(0)
        if "either(" not in macro:
            continue
        k = macro.find("either(")
        i2 = k + len("either(")
        d2 = 1
        while i2 < len(macro) and d2 > 0:
            if macro[i2] == "(":
                d2 += 1
            elif macro[i2] == ")":
                d2 -= 1
            i2 += 1
        inner = macro[k + len("either("):i2 - 1]
        base = re.sub(r'"(?:[^"\\\\]|\\\\.)*"', '""', inner)
        base = re.sub(r"'(?:[^'\\\\]|\\\\.)*'", "''", base)
        if "，" in base:
            n += 1
    (ok if n == 0 else bad)("[9] either() 参数无全角逗号", f"{n} 处")
'''
    s = s[:start] + NEW + s[end:]
    open(REGRESS, "w", encoding="utf-8").write(s)
    print("  ✅ regress.py 的 either 检测已重写（只查宏内）")


if __name__ == "__main__":
    print("=== 1) 补 displayName ===")
    fix_dn()
    print("\n=== 2) 修 regress.py ===")
    fix_regress()
