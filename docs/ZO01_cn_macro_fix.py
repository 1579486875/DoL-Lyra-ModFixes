"""修中文宏名 + 加通用检测（并入 build_all 和 validate.py）。

已知：
  <<保持了安静>>  -> <<silently>>
  <<他>>          -> <<He>>

通用规则：<<中文...>> 一律是非法宏名。用 vanilla 对照还原；
找不到对照的表直接改成最接近的已知宏（silently / He）。
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"

CJK = re.compile(r"[\u4e00-\u9fff]")

# 手工映射（经 vanilla 对照确认）
MANUAL = {
    "保持了安静": "silently",
    "他": "He",
    "她": "She",
    "它": "It",
    "他们": "They",
}

# 常用代词宏（供模糊匹配）
PRONOUNS = ["He", "She", "It", "They", "His", "Her", "Him", "Them", "Hers"]


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    g = H.unescape(data)

    hits = []
    for m in re.finditer(r"<<([\u4e00-\u9fff][^>]{0,60})>>", g):
        hits.append((m.group(1), m.start()))

    print(f"中文宏名: {len(hits)} 处")
    for name, pos in hits:
        print(f"  <<{name[:40]}>>  @{pos}")
        print(f"    {g[max(0,pos-150):pos+120]!r}")

    print("\n=== 修复 ===")
    total = 0
    for cn, en in MANUAL.items():
        for pat in (f"<<{cn}>>",):
            for a, b in ((H.escape(pat, quote=False), H.escape(f"<<{en}>>", quote=False)),
                         (pat, f"<<{en}>>")):
                if a in data:
                    n = data.count(a)
                    data = data.replace(a, f"<<{en}>>" if not a.startswith("&") else H.escape(f"<<{en}>>", quote=False))
                    total += n
                    print(f"  ✅ {pat} -> <<{en}>>  ({n})")
                    break

    if total:
        open(HTML, "wb").write(data.encode("utf-8"))
        print(f"\n合计 {total} 处")

    # 校验
    g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
    remain = re.findall(r"<<([\u4e00-\u9fff][^>]{0,60})>>", g2)
    print(f"\n剩余中文宏名: {len(remain)}")
    for r in remain[:10]:
        print(f"  <<{r}>>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
