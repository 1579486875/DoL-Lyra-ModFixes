"""第 14 轮：修复 settings.watersportsEnabled 丢 $ 的 3 处（含 HTML 转义形态）。

证据：
  $settings.watersportsEnabled 出现 17 次（正确写法）
  裸 settings.watersportsEnabled 出现 3 次，全部在 <<if>> / ! 里
→ 裸 settings 是 window.settings（不存在）→ undefined → 条件恒假
→ 失禁场景永不触发（功能失效）

不动 version.major：$version 只有 schema 字段，改成 $version.major 同样是 undefined。
"""
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")

    before = len(re.findall(r"(?<![\w$.])settings\.watersportsEnabled", data))
    print(f"修复前裸 settings.watersportsEnabled: {before} 处")

    # 覆盖：未转义 <<if / 转义 &lt;&lt;if / ! 前缀 / <<elseif 两种
    pats = [
        (r"(&lt;&lt;if\s+)settings\.watersportsEnabled", r"\1$settings.watersportsEnabled"),
        (r"(&lt;&lt;elseif\s+)settings\.watersportsEnabled", r"\1$settings.watersportsEnabled"),
        (r"(<<if\s+)settings\.watersportsEnabled", r"\1$settings.watersportsEnabled"),
        (r"(<<elseif\s+)settings\.watersportsEnabled", r"\1$settings.watersportsEnabled"),
        (r"(!)settings\.watersportsEnabled", r"\1$settings.watersportsEnabled"),
    ]
    total = 0
    for p, r in pats:
        pat = re.compile(p)
        n = len(pat.findall(data))
        if n:
            data = pat.sub(r, data)
            total += n
            print(f"  ✅ {p[:36]}... 替换 {n} 处")

    after = len(re.findall(r"(?<![\w$.])settings\.watersportsEnabled", data))
    print(f"修复后残留: {after} 处")
    print(f"合计修复 {total} 处")

    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
