"""修 penisdesc 的英文子串判断：改成中英兼容。

原版：penisdesc.includes("horse")
modded 的 _pd 已中文化（"马屌"），所以英文判断恒 false。
改成：penisdesc.includes("horse") || penisdesc.includes("马")
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

# 英文子串 -> 中文对应（来自 modded 的 _pd 数组）
MAP = {
    "horse": "马",
    "knotted": "锁结",
    "tentacle": "触手",
    "strap-on": "穿戴式",
    "dolphin": "海豚",
}


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    total = 0

    for en, cn in MAP.items():
        # 匹配 xxx.penisdesc.includes("en")
        # 已经是 || 兼容写法的跳过
        pat = re.compile(
            r'([\w$.\[\]]*penisdesc)\s*\.\s*includes\(\s*["\']' + re.escape(en) + r'["\']\s*\)'
        )
        hits = list(pat.finditer(data))
        if not hits:
            print(f"  （无）{en}")
            continue

        n = 0
        out = []
        last = 0
        for m in hits:
            obj = m.group(1)
            # 检查后面是否已经跟了 || .includes("中文")
            tail = data[m.end():m.end() + 80]
            if re.match(r'\s*\|\|\s*' + re.escape(obj) + r'\s*\.\s*includes\(\s*["\']' + re.escape(cn) + r'["\']', tail):
                continue
            rep = (f'({obj}.includes("{en}") || {obj}.includes("{cn}"))')
            out.append(data[last:m.start()])
            out.append(rep)
            last = m.end()
            n += 1
        if n:
            out.append(data[last:])
            data = "".join(out)
            total += n
            print(f"  ✅ {en} -> 中英兼容  ({n} 处)")

    if total:
        open(HTML, "wb").write(data.encode("utf-8"))
        print(f"\n合计 {total} 处，写出 {HTML}")
    else:
        print("\n（无改动）")

    # 校验
    g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
    print("\n=== 校验 ===")
    for en, cn in MAP.items():
        n1 = len(re.findall(r'penisdesc\.includes\("' + re.escape(en) + r'"\)', g))
        n2 = len(re.findall(r'penisdesc\.includes\("' + re.escape(cn) + r'"\)', g))
        print(f"  {en!r}: 纯英文判断 {n1}  中文判断 {n2}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
