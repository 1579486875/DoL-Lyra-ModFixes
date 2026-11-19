"""修复 i18n 破坏的 <<print either(...)>> 参数（缺反引号）。

判据（很保守，只修确定的）：
  参数里含 `<<` 宏
  且不以 ` / " / ' 开头
  且不是三元表达式（不含 ` ? `）
  → 这个参数是裸 TwineScript 文本，必须用反引号包起来

同时修 <<set>> 里字面量化的 <<= _xxx>>。
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"


def split_args(body):
    """按顶层逗号切分（考虑括号/引号/反引号）。"""
    parts, buf = [], ""
    depth = 0
    in_str, q = False, ""
    i = 0
    while i < len(body):
        ch = body[i]
        if in_str:
            buf += ch
            if ch == "\\" and i + 1 < len(body):
                buf += body[i + 1]
                i += 2
                continue
            if ch == q:
                in_str = False
            i += 1
            continue
        if ch in "`'\"":
            in_str, q = True, ch
            buf += ch
            i += 1
            continue
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(buf)
            buf = ""
            i += 1
            continue
        buf += ch
        i += 1
    if buf.strip():
        parts.append(buf)
    return parts


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")

    # 找所有 <<print either( ... )>>
    out = []
    pos = 0
    fixed = 0
    while True:
        m = re.search(r"<<print\s+either\(", data[pos:])
        if not m:
            break
        start = pos + m.end()
        # 找匹配的右括号
        i = start
        depth = 1
        in_str, q = False, ""
        while i < len(data) and depth > 0:
            ch = data[i]
            if in_str:
                if ch == "\\":
                    i += 2
                    continue
                if ch == q:
                    in_str = False
                i += 1
                continue
            if ch in "`'\"":
                in_str, q = True, ch
                i += 1
                continue
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            i += 1
        body = data[start:i - 1]
        args = split_args(body)

        changed = False
        new_args = []
        for a in args:
            s = a.strip()
            if (s and "<<" in s
                    and not s.startswith("`") and not s.startswith('"') and not s.startswith("'")
                    and " ? " not in s):
                new_args.append("`" + s + "`")
                changed = True
            else:
                new_args.append(a)

        if changed:
            new_body = ",".join(new_args)
            data = data[:start] + new_body + data[i - 1:]
            pos = start + len(new_body) + 1
            fixed += 1
        else:
            pos = i

    print(f"✅ 修复 <<print either>> 缺反引号的参数: {fixed} 处")

    # 修 <<set X to "_line1<<= _line2>>" >> 这种字面量化
    def fix_set(mm):
        var, lit = mm.group(1), mm.group(2)
        # "_line1<<= _line2>>" -> "_line1" + _line2 + ""
        m2 = re.match(r'^"([^"<]*)<<=\s*([\w.$_\[\]]+)\s*>>([^"<]*)"$', lit)
        if m2:
            pre, expr, post = m2.group(1), m2.group(2), m2.group(3)
            return f'<<set {var} to "{pre}" + {expr} + "{post}">>'
        return mm.group(0)

    before = data.count("<<= _line2>>")
    data = re.sub(r"<<set\s+([\w$_.\[\]]+)\s+to\s+(\"(?:[^\"\\]|\\.)*\")>>", fix_set, data)
    after = data.count("<<= _line2>>")
    if before != after:
        print(f"✅ 修复 _speechWraith 字符串内嵌宏: {before} -> {after}")

    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"\n写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
