"""给 either() 里「含宏但无引号」的参数补反引号。

文件里宏是转义形态 &lt;&lt;He&gt;&gt;，判据要认这个。
"""
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"


def split_args(body):
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
    fixed = 0
    pos = 0
    for prefix in (r"&lt;&lt;print\s+either\(", r"<<print\s+either\("):
        pos = 0
        while True:
            m = re.search(prefix, data[pos:])
            if not m:
                break
            start = pos + m.end()
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
                has_macro = ("&lt;&lt;" in s) or ("<<" in s)
                quoted = s.startswith("`") or s.startswith('"') or s.startswith("'")
                ternary = " ? " in s or " &amp;&amp; " in s
                if s and has_macro and not quoted and not ternary:
                    indent = a[:len(a) - len(a.lstrip())]
                    trail = a[len(a.rstrip()):]
                    new_args.append(indent + "`" + s + "`" + trail)
                    changed = True
                else:
                    new_args.append(a)

            if changed:
                new_body = ",".join(new_args)
                data = data[:start] + new_body + data[i - 1:]
                fixed += 1
                pos = start + len(new_body) + 1
            else:
                pos = i

    print(f"✅ 给 either() 裸宏参数补反引号: {fixed} 处")
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
