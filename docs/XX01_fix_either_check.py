"""重写 regress.py 的 either 检测：直接按括号配平提取，不看 <<>> 边界。"""
import re
import sys

REGRESS = r"E:\TAML\_dol\work\regress.py"
s = open(REGRESS, encoding="utf-8").read()

start = s.find("    # 9 either() 全角逗号")
if start < 0:
    print("❌ 未找到 either 检测块")
    sys.exit(1)

# 找到该块结尾（(ok if n == 0 else bad) 那一行）
end = s.find('("[9] either() 参数无全角逗号"', start)
if end < 0:
    print("❌ 未找到块尾")
    sys.exit(1)
end = s.find("\n", end) + 1

NEW = '''    # 9 either() 全角逗号 —— 按括号配平提取，不受内嵌宏影响
    n = 0
    samples = []
    pos = 0
    while True:
        k = g.find("either(", pos)
        if k < 0:
            break
        pos = k + 1
        # 前面必须是 << 开头（说明在宏里）
        head = g[max(0, k - 40):k]
        if "<<" not in head:
            continue
        i2 = k + len("either(")
        d2 = 1
        in_dq = False
        in_sq = False
        esc = False
        while i2 < len(g) and d2 > 0:
            ch = g[i2]
            if esc:
                esc = False
            elif ch == "\\\\":
                esc = True
            elif in_dq:
                if ch == '"':
                    in_dq = False
            elif in_sq:
                if ch == "'":
                    in_sq = False
            elif ch == '"':
                in_dq = True
            elif ch == "'":
                in_sq = True
            elif ch == "(":
                d2 += 1
            elif ch == ")":
                d2 -= 1
            i2 += 1
        inner = g[k + len("either("):i2 - 1]
        base = re.sub(r'"(?:[^"\\\\]|\\\\.)*"', '""', inner)
        base = re.sub(r"'(?:[^'\\\\]|\\\\.)*'", "''", base)
        if "，" in base:
            n += 1
            if len(samples) < 3:
                samples.append(inner[:80])
    (ok if n == 0 else bad)("[9] either() 参数无全角逗号", f"{n} 处: {samples}")
'''

s = s[:start] + NEW + s[end:]
open(REGRESS, "w", encoding="utf-8").write(s)
print("✅ regress.py 的 either 检测已重写（括号配平）")
