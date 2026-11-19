"""修全部残留问题：
A) <<= ... <<= ... >> ... >> 嵌套（折叠成一层）
B) <<=>> 里的全角括号 （ ）
C) 夹在中文里的英文单词
"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

# ---- C) 英文单词映射 ----
WORDS = {
    "Makeup": "妆容",
    "eyes": "眼睛",
    "a light": "浅色",
    "lizard": "蜥蜴",
    "eels": "鳗鱼",
    "eel": "鳗鱼",
    "whale": "鲸鱼",
    "Radio (c)": "单选（紧凑）",
    "Radio": "单选",
    "Lists": "列表",
    "List (w)": "列表（宽）",
    "Next": "继续",
    "left手": "左手",
    "right手": "右手",
    "Ass and legs.": "屁股和腿。",
    "girl": "女孩",
    "boy": "男孩",
}


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    total = 0

    # --- A) 折叠 <<= ... <<= X >> ... >> ---
    print("=" * 88)
    print("A) 折叠 <<= <<= ... >> ... >> 嵌套")
    print("=" * 88)
    before = data.count("<<= setup.colourName（<<=")
    # 具体模式：<<= setup.colourName（<<= INNER >>）OUTER >>
    pat_stack = re.compile(
        r"&lt;&lt;=\s*setup\.colourName（&lt;&lt;=\s*(setup\.colourName\([^&]*?\))&gt;&gt;）([^&]*?)&gt;&gt;"
    )
    n = 0
    def rep(m):
        nonlocal n
        n += 1
        return "&lt;&lt;=" + m.group(1) + m.group(2) + "&gt;&gt;"
    data = pat_stack.sub(rep, data)
    print(f"  折叠 {n} 处")
    total += n

    # --- B) <<=>> 里的全角括号 ---
    print("\n" + "=" * 88)
    print("B) <<=>> 表达式里的全角括号")
    print("=" * 88)
    g = H.unescape(data)
    bad = []
    for m in re.finditer(r"<<=\s*([^>]{1,400})>>", g):
        expr = m.group(1)
        base = re.sub(r'"(?:[^"\\]|\\.)*"', '""', expr)
        base = re.sub(r"'(?:[^'\\]|\\.)*'", "''", base)
        base = re.sub(r"`(?:[^`\\]|\\.)*`", "``", base)
        if "（" in base or "）" in base:
            bad.append(expr[:120])
    print(f"  剩余 {len(bad)} 处")
    for b in bad[:5]:
        print(f"    {b!r}")

    # --- C) 英文单词 ---
    print("\n" + "=" * 88)
    print("C) 夹在中文里的英文单词")
    print("=" * 88)
    for en, cn in WORDS.items():
        # 只在中文语境里替换：前后至少有一个中文字符
        pat = re.compile(r"(?<=[\u4e00-\u9fff])\s*" + re.escape(en) + r"\s*(?=[\u4e00-\u9fff])")
        for a in (H.escape(en, quote=False), en):
            p2 = re.compile(r"(?<=[\u4e00-\u9fff])\s*" + re.escape(a) + r"\s*(?=[\u4e00-\u9fff])")
            hits = p2.findall(data)
            if hits:
                data = p2.sub(cn, data)
                total += len(hits)
                print(f"  ✅ {en!r} -> {cn!r}  ({len(hits)})")
                break

    # Makeup 在 displayName / faceVariantOptions 里
    for a, b in (('"Makeup"', '"妆容"'), ("'Makeup'", "'妆容'")):
        if a in data:
            n2 = data.count(a)
            data = data.replace(a, b)
            total += n2
            print(f"  ✅ {a} -> {b}  ({n2})")

    if total:
        open(HTML, "wb").write(data.encode("utf-8"))
        print(f"\n合计 {total} 处，写出 {HTML}")
    else:
        print("\n（无改动）")

    # 校验
    g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
    print("\n=== 校验 ===")
    for w in ["Makeup", "lizard", "eels", "whale", "left手", "Ass and legs"]:
        n3 = g2.count(w)
        print(f"  {w!r}: {n3}")
    bad2 = 0
    for m in re.finditer(r"<<=\s*([^>]{1,400})>>", g2):
        expr = m.group(1)
        base = re.sub(r'"(?:[^"\\]|\\.)*"', '""', expr)
        base = re.sub(r"'(?:[^'\\]|\\.)*'", "''", base)
        if "（" in base or "）" in base:
            bad2 += 1
    print(f"  <<=>> 里全角括号: {bad2}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
