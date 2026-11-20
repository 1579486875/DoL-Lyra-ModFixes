"""F01（第1轮）：宏语法完整性 —— 开闭配对 + 嵌套层级。

检查 <<if>>/<</if>>、<<for>>/<</for>>、<<widget>>/<</widget>>、
<<switch>>/<</switch>>、<<link>>/<</link>>、<<script>>/<</script>> 等。
"""
import html as H
import re
import zipfile
from collections import Counter, defaultdict

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
raw = zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace")
g = H.unescape(raw)

# 提取所有 passage
PASSAGES = {}
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
    PASSAGES[m.group(1)] = H.unescape(m.group(2))

print(f"passage 总数: {len(PASSAGES)}")

# 需要配对的宏
PAIRED = {
    "if": "if", "for": "for", "widget": "widget", "switch": "switch",
    "link": "link", "button": "button", "script": "script", "silently": "silently",
    "nobr": "nobr", "capture": "capture", "replace": "replace", "append": "append",
    "prepend": "prepend", "timed": "timed", "repeat": "repeat", "cycle": "cycle",
    "else": None, "elseif": None, "break": None, "continue": None,
}

print("\n" + "=" * 100)
print("1) 逐个 passage 检查宏配对")
print("=" * 100)

issues = []
for pname, body in PASSAGES.items():
    # 从 body 里提取所有宏（第一次扫描，不处理嵌套）
    # 用状态机更准确
    stack = []
    i = 0
    L = len(body)
    while i < L:
        j = body.find("<<", i)
        if j < 0:
            break
        # 跳过 <<= 和 <<- 和 <<[
        if j + 2 < L and body[j + 2] in "=-[!":
            # <<= expr>> 或 <<- ...>>；<<= 是表达式输出，无配对
            if body[j + 2] == "=":
                k = body.find(">>", j + 3)
                i = k + 2 if k > 0 else L
                continue
            # <<-- 注释 -->>
            if body.startswith("<<--", j):
                k = body.find("-->>", j + 4)
                i = k + 4 if k > 0 else L
                continue
        # 找宏结束 >>
        k = j + 2
        depth = 0
        while k < L:
            if body.startswith(">>", k):
                break
            k += 1
        if k >= L:
            break
        macro = body[j:k + 2]
        i = k + 2

        # 解析宏名
        mm = re.match(r"<<\s*(/?)\s*([A-Za-z_][A-Za-z0-9_\-]*)", macro)
        if not mm:
            continue
        is_close = mm.group(1) == "/"
        name = mm.group(2).lower()

        if name in ("else", "elseif", "break", "continue", "case", "default"):
            continue  # 中间宏，不配对

        if name in PAIRED and PAIRED[name]:
            if is_close:
                if stack and stack[-1][0] == name:
                    stack.pop()
                else:
                    issues.append((pname, "多余闭合", macro[:80], j,
                                   stack[-1][0] if stack else "空栈"))
            else:
                stack.append((name, j, macro[:80]))

    if stack:
        for nm, pos, txt in stack:
            issues.append((pname, "未闭合", txt, pos, "文件结束"))

print(f"  发现问题: {len(issues)} 处")
by_type = Counter(x[1] for x in issues)
for t, c in by_type.most_common():
    print(f"    {t}: {c}")

print("\n" + "=" * 100)
print("2) 明细（前 30 条）")
print("=" * 100)
for pname, typ, txt, pos, extra in issues[:30]:
    print(f"\n  [{pname}] {typ}  @{pos}  ({extra})")
    print(f"    {txt!r}")

# 保存
with open(r"E:\TAML\_dol\work\_macro_pair_issues.txt", "w", encoding="utf-8") as f:
    for it in issues:
        f.write("\t".join(str(x) for x in it) + "\n")
print(f"\n已保存 _macro_pair_issues.txt")
