"""修用户报的剩余问题：
1) <<if>>: Unexpected token '<<'（宏嵌套）
2) <<=>>: Invalid or unexpected token（Wardrobe）
3) 英语单词夹中文（Makeup/eyes/a light/lizard/eels/whale/Radio/Next/left手 等）
"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))

print("=" * 88)
print("1) 宏嵌套（<<if>> 里含 <<xxx>> 且没有正确包裹）")
print("=" * 88)
# 找 <<if ... << ... >>> 形态
bad = []
for m in re.finditer(r"<<(?:if|elseif|unless)\s+([^>]{1,300})>>", g):
    expr = m.group(1)
    if "<<" in expr:
        bad.append((m.start(), expr[:120]))
print(f"  {len(bad)} 处")
for pos, e in bad[:10]:
    print(f"\n    @{pos}: {e!r}")
    print(f"      {g[max(0,pos-120):pos+200]!r}")

print("\n" + "=" * 88)
print("2) <<=>> 里的非法 token（中文/全角标点直接出现在表达式里）")
print("=" * 88)
bad2 = []
for m in re.finditer(r"<<=\s*([^>]{1,400})>>", g):
    expr = m.group(1)
    # 去掉字符串后看是否还有中文
    base = re.sub(r'"(?:[^"\\]|\\.)*"', '""', expr)
    base = re.sub(r"'(?:[^'\\]|\\.)*'", "''", base)
    base = re.sub(r"`(?:[^`\\]|\\.)*`", "``", base)
    if re.search(r"[\u4e00-\u9fff。，、；：！？（）【】「」『』]", base):
        bad2.append((m.start(), expr[:150], base[:100]))
print(f"  {len(bad2)} 处")
for pos, e, b in bad2[:15]:
    print(f"\n    @{pos}: {e!r}")
    print(f"      去字符串后: {b!r}")
    print(f"      上下文: {g[max(0,pos-100):pos+180]!r}")

print("\n" + "=" * 88)
print("3) 中英混杂的常见词")
print("=" * 88)
WORDS = ["Makeup", "eyes", "a light", "lizard", "eels", "whale", "Radio",
         "Lists", "List (w)", "Next", "left手", "Ass and legs"]
for w in WORDS:
    n = g.count(w)
    if n:
        print(f"\n  {w!r}: {n} 次")
        for m in list(re.finditer(re.escape(w), g))[:2]:
            print(f"    {g[max(0,m.start()-90):m.start()+90]!r}")
