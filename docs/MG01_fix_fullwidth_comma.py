"""修复 i18n 把 either() 参数分隔符换成全角逗号（处理 HTML 转义形态）。

index.html 里宏是 &lt;&lt;print 这种转义形态，正则必须两种都兼容。
"""
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"


def fix_call(data, fn):
    count = 0
    for prefix in (r"&lt;&lt;print\s+", r"<<print\s+"):
        pos = 0
        while True:
            m = re.search(prefix + fn + r"\(", data[pos:])
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

            out, in_s, qq, j = [], False, "", 0
            while j < len(body):
                ch = body[j]
                if in_s:
                    out.append(ch)
                    if ch == "\\" and j + 1 < len(body):
                        out.append(body[j + 1])
                        j += 2
                        continue
                    if ch == qq:
                        in_s = False
                    j += 1
                    continue
                if ch in "`'\"":
                    in_s, qq = True, ch
                    out.append(ch)
                    j += 1
                    continue
                if ch == "，":
                    out.append(",")
                    j += 1
                    continue
                out.append(ch)
                j += 1
            new_body = "".join(out)
            if new_body != body:
                data = data[:start] + new_body + data[i - 1:]
                pos = start + len(new_body) + 1
                count += 1
            else:
                pos = i
    return data, count


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    total = 0
    for fn in ("either", "random"):
        data, n = fix_call(data, fn)
        if n:
            print(f"  ✅ <<print {fn}(...)>> 全角逗号修正: {n} 处")
            total += n
    if total == 0:
        print("  （仍未匹配，检查是否还有别的函数名）")
        # 诊断：打印所有 <<print 后跟的标识符
        for pat in (r"&lt;&lt;print\s+([a-zA-Z_][\w.]*)", r"<<print\s+([a-zA-Z_][\w.]*)"):
            names = set(re.findall(pat, data))
            print(f"    {pat[:14]}... 出现 <</print>> 后的标识符: {sorted(names)[:15]}")

    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
