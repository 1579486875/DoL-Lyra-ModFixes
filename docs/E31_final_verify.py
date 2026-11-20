"""E31：最终完整验证（文件形式，避免 shell 转义）。"""
import html as H
import re

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")
g = H.unescape(raw)

TICK = chr(96)  # 反引号

def strip_literals(body):
    """挖掉字符串字面量和正则字面量。"""
    s = re.sub(r'"[^"]*"', lambda m: " " * len(m.group(0)), body)
    s = re.sub(r"'[^']*'", lambda m: " " * len(m.group(0)), s)
    s = re.sub(TICK + r"[^" + TICK + r"]*" + TICK, lambda m: " " * len(m.group(0)), s)
    s = re.sub(r"/[^/\n]*/", lambda m: " " * len(m.group(0)), s)
    return s


print("=" * 90)
print("1) index 形态")
print("=" * 90)
print(f"  passage (带 name): {len(re.findall(r'<tw-passagedata[^>]*name=', raw))}")
print(f"  passage (全部)    : {len(re.findall(r'<tw-passagedata', raw))}")
print(f"  大小: {len(raw)/1048576:.2f} MB")

print("\n" + "=" * 90)
print("2) 已知错误残留（应为 0）")
print("=" * 90)
BAD = ["_下体。", "_下体", "C.npc.罗宾", "C.npc.艾弗里", ".火坑前面",
       ".额头上", "applyClothingShop过滤", "tanning启用d", "次序:",
       "_精液，", "我的arousal", "$speech冲撞着", "$speechrammalentrance",
       "Tendrils of 深色ness", "Your eyes itch", 'curvy: "Curvy"',
       "<<br>>", "flesh_text", "printNobody", "<<</if>>"]
for kw in BAD:
    c = g.count(kw)
    print(f"  {'✅' if c == 0 else '❌'} {kw!r}: {c}")

print("\n" + "=" * 90)
print("3) 修复生效（应 >0）")
print("=" * 90)
GOOD = ["catboy,猫男", "catgirl,猫娘", "doggirl,狗娘", "harpygirl,鹰身女妖",
        "curvy,曲线玲珑", "shapely,曲线优美", "黑暗的触须", "你的眼睛发痒",
        'curvy: "曲线"']
for kw in GOOD:
    c = g.count(kw)
    print(f"  {'✅' if c > 0 else '❌'} {kw!r}: {c}")

print("\n" + "=" * 90)
print("4) 代码位置含中文（致命语法错误）")
print("=" * 90)
bad = []
for m in re.finditer(r"<<(if|elseif|set|run|switch|case|for|while)\b([^<>]{0,800}?)>>", g):
    if re.search(r"[\u4e00-\u9fff]", strip_literals(m.group(2))):
        bad.append(m.group(0)[:200])
print(f"  {'✅' if not bad else '❌'} {len(bad)} 处")
for b in bad[:10]:
    print(f"    {b!r}")

print("\n" + "=" * 90)
print("5) 其他中文污染")
print("=" * 90)
PATTERNS = [
    (r"\.[\u4e00-\u9fff]{2,10}\.", ".中文属性."),
    (r"C\.npc\.[\u4e00-\u9fff]", "C.npc.中文"),
    (r"\$[A-Za-z0-9]*[\u4e00-\u9fff]+[A-Za-z]", "$变量含中文"),
    (r"<<\s*/?\s*[\u4e00-\u9fff][^<>]{0,30}>>", "<<中文宏名>>"),
]
for p, label in PATTERNS:
    hs = list(re.finditer(p, g))
    print(f"  {label}: {len(hs)}")
    for h in hs[:5]:
        print(f"    {h.group(0)!r}")

print("\n" + "=" * 90)
print("6) widget / macro 数量")
print("=" * 90)
print(f"  widget: {len(set(re.findall(r'<<widget\\s+\"([^\"]+)\"', g)))}")
print(f"  macro : {len(set(re.findall(r'Macro\\.add\\(\\s*\"([^\"]+)\"', g)))}")
