"""D01：统一修复（转义形态）—— 替代 ZZ02/Z03/A26/B04/C04。

index_modded6.html 的正确形态：passage 标签明文 + 内容 HTML 转义（&lt;&lt;if）。
所有字符串替换按转义形态做。
"""
import base64
import html as H
import io
import json
import os
import re
import sys
import zipfile

WORK = r"E:\TAML\_dol\work"
HTML = os.path.join(WORK, "index_modded6.html")
ARCHIVE = r"E:\TAML\_dol\archive"
GOOD = os.path.join(ARCHIVE, "DoL-Lyra-0.5.12.13-CHS-modded_20261120-061313_修复arsc可安装.apk")

# 0) 从好包恢复基线
z = zipfile.ZipFile(GOOD)
data = z.read("assets/www/index.html").decode("utf-8", "replace")
z.close()
n_pass = len(re.findall(r"<tw-passagedata", data))
n_esc_pass = len(re.findall(r"&lt;tw-passagedata", data))
print(f"基线: passage {n_pass} 明文 / {n_esc_pass} 转义, {len(data)/1048576:.2f} MB")
if n_pass < 16000:
    print("❌ 基线异常")
    sys.exit(1)

total = 0


def rep(old, new, label=""):
    """在转义形态上替换（自动处理两态）。"""
    global data, total
    hit = 0
    for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)),
                 (old, new)):
        if a in data:
            c = data.count(a)
            data = data.replace(a, b)
            hit += c
    if hit:
        total += hit
        print(f"  ✅ {hit}x {label or old[:50]!r}")
    return hit


# ========== 1. 运算符 bug（最高优先） ==========
print("\n=== 1. 运算符 ===")
rep("<<if $audience gte 0 且 $audience lte 5>>",
    "<<if $audience gte 0 and $audience lte 5>>", "且 -> and")

# 通用：<<if 里的 且/或
for cn, en in (("且", "and"), ("或", "or")):
    pat = re.compile(r"(<<if\b[^<>]{1,400}?)\s+" + cn + r"\s+([^<>]{1,400}?>>)")
    c = len(pat.findall(data))
    if c:
        data = pat.sub(lambda m: m.group(1) + " " + en + " " + m.group(2), data)
        total += c
        print(f"  ✅ {c}x 通用 <<if>> {cn} -> {en}")

# ========== 2. Tendrils ==========
print("\n=== 2. Tendrils ===")
rep("Tendrils of 深色ness whip and writhe against your skin as",
    "黑暗的触须抽打着你的皮肤，缠绕扭动，同时")
rep("Tendrils of 深色ness writhe against your skin as",
    "黑暗的触须缠绕扭动着你的皮肤，同时")

# ========== 3. You've gained ==========
print("\n=== 3. You've gained ===")
for pat in (re.compile(r"You\\'ve gained (?=(?:<<|&lt;&lt;)moneyGain)"),):
    c = len(pat.findall(data))
    if c:
        data = pat.sub("你获得了 ", data)
        total += c
        print(f"  ✅ {c}x You've gained -> 你获得了")

# ========== 4. textMap 身形 ==========
print("\n=== 4. textMap ===")
Q = chr(34)
rep('textMap: { classic: "Classic", slender: "Slender", curvy: "Curvy", soft: "Soft" }',
    'textMap: { classic: "经典", slender: "瘦长", curvy: "曲线", soft: "柔软" }')
rep("{ 0: " + Q + "Slender" + Q + ", 1: " + Q + "Slim" + Q + ", 2: " + Q + "Modest" + Q + ", 3: " + Q + "Cushioned" + Q + " }",
    "{ 0: " + Q + "纤细" + Q + ", 1: " + Q + "瘦削" + Q + ", 2: " + Q + "适中" + Q + ", 3: " + Q + "丰满" + Q + " }")
rep("{ 0: " + Q + "Slender" + Q + ", 1: " + Q + "Slim" + Q + ", 2: " + Q + "Modest" + Q + ", 3: " + Q + "Cushioned" + Q + ", 4: " + Q + "Soft" + Q + ", 5: " + Q + "Round" + Q + ", 6: " + Q + "Plump" + Q + ", 7: " + Q + "Large" + Q + ", 8: " + Q + "Huge" + Q + " }",
    "{ 0: " + Q + "纤细" + Q + ", 1: " + Q + "瘦削" + Q + ", 2: " + Q + "适中" + Q + ", 3: " + Q + "丰满" + Q + ", 4: " + Q + "柔软" + Q + ", 5: " + Q + "圆润" + Q + ", 6: " + Q + "丰腴" + Q + ", 7: " + Q + "硕大" + Q + ", 8: " + Q + "巨大" + Q + " }")

# ========== 5. element("span", ...) 152 条 ==========
print("\n=== 5. element 身体变化提示 ===")
try:
    with open(os.path.join(WORK, "_element_map.json"), "r", encoding="utf-8") as f:
        ELEM = json.load(f)
except FileNotFoundError:
    ELEM = {}

if ELEM:
    c_all = 0
    for en, cn in ELEM.items():
        c_all += rep(en, cn, "")
    if c_all:
        print(f"  ✅ element 共 {c_all} 处")
else:
    print("  ⚠️ 缺 _element_map.json")

# ========== 6. 最后 28 条 ==========
print("\n=== 6. 最后 28 条 ===")
try:
    with open(os.path.join(WORK, "_last_map.json"), "r", encoding="utf-8") as f:
        LAST = json.load(f)
except FileNotFoundError:
    LAST = {}

if LAST:
    c_all = 0
    for en, cn in LAST.items():
        c_all += rep(en, cn, "")
    if c_all:
        print(f"  ✅ 最后 28 条共 {c_all} 处")
else:
    print("  ⚠️ 缺 _last_map.json")

# ========== 7. 兽人类型 + 体格词（EXTRA 表） ==========
print("\n=== 7. EXTRA 表 ===")
m = re.search(r"var EXTRA = \{(.*?)\};", data, re.S)
if m:
    body = m.group(1)
    have = set(re.findall(r'"([a-z][a-z \-]*)"\s*:', body))
    ADD = {}
    # 兽人
    for k, v in {"doggirl": "狗娘", "dogboy": "狗男", "catgirl": "猫娘", "catboy": "猫男",
                 "wolfgirl": "狼娘", "wolfboy": "狼男", "beargirl": "熊娘", "bearboy": "熊男",
                 "pigboy": "猪男", "piggirl": "猪娘", "foxgirl": "狐娘", "foxboy": "狐男",
                 "dolphingirl": "海豚娘", "dolphinboy": "海豚男", "horsegirl": "马娘", "horseboy": "马男",
                 "harpygirl": "鹰身女妖", "harpyboy": "鹰身男妖", "slimegirl": "史莱姆娘", "slimeboy": "史莱姆男",
                 "plantgirl": "植物娘", "plantboy": "植物男"}.items():
        if k not in have:
            ADD[k] = v
    # 体格词
    for k, v in {"slight": "瘦小", "lithe": "轻盈", "lean": "精瘦", "thin": "瘦削",
                 "slender": "纤细", "lissome": "柔韧", "slim": "苗条", "taut": "紧实",
                 "graceful": "优雅", "trim": "匀称", "mousy": "怯生生", "cute": "可爱",
                 "fit": "健硕", "petite": "娇小", "toned": "结实", "shapely": "曲线优美",
                 "robust": "强健", "plump": "丰腴", "wide-eyed": "睁大眼睛", "vulgar": "粗鄙",
                 "minor demon": "小恶魔", "muscular": "肌肉发达", "curvy": "曲线玲珑",
                 "plush": "柔软丰满", "voluptuous": "妖娆", "lush": "丰茂",
                 "demon": "恶魔", "bulky": "魁梧", "broad": "宽阔", "lanky": "瘦长",
                 "brutish": "粗野", "tutorial": "教程", "debug": "调试"}.items():
        if k not in have:
            ADD[k] = v

    if ADD:
        lines = "\n".join('            "%s": "%s",' % (k, v) for k, v in ADD.items())
        nb = body.rstrip()
        if not nb.endswith(","):
            nb += ","
        nb += "\n" + lines + "\n        "
        data = data[:m.start(1)] + nb + data[m.end(1):]
        total += len(ADD)
        print(f"  ✅ 补 {len(ADD)} 个键")
    else:
        print("  （已全有）")

# ========== 8. 生育拓展模组 NPC 名 ==========
print("\n=== 8. 生育拓展模组 ===")
m2 = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", data, re.S)
if m2:
    block_start, block_end = m2.start(1), m2.end(1)
    block = m2.group(1)
    parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', block)
    TARGETS = [
        ("Bailey、Leighton 与 Gwylan 可按原版生理与怀孕规则参与受孕或授孕；Gwylan 的裸手牵手",
         "贝利、礼顿与格威岚可按原版生理与怀孕规则参与受孕或授孕；格威岚的裸手牵手"),
        ("Bailey、Leighton 与 Gwylan", "贝利、礼顿与格威岚"),
        ("Gwylan 的裸手牵手", "格威岚的裸手牵手"),
    ]
    new_block = block
    fixed = 0
    for s in parts:
        raw = base64.b64decode(re.sub(r"\s+", "", s))
        if raw[:2] != b"PK":
            continue
        try:
            zz = zipfile.ZipFile(io.BytesIO(raw))
            bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
            if bj.get("name") != "FertilityExpansion":
                continue
        except Exception:
            continue
        buf = io.BytesIO()
        changed = []
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
            for info in zz.infolist():
                d = zz.read(info.filename)
                if info.filename.endswith((".twee", ".js", ".json", ".css", ".html", ".txt")):
                    try:
                        txt = d.decode("utf-8")
                        orig = txt
                        for a, b in TARGETS:
                            txt = txt.replace(a, b)
                        if txt != orig:
                            d = txt.encode("utf-8")
                            changed.append(info.filename)
                    except Exception:
                        pass
                zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
                zi.compress_type = info.compress_type
                zi.external_attr = info.external_attr
                zo.writestr(zi, d)
        if changed:
            nb64 = base64.b64encode(buf.getvalue()).decode("ascii")
            pat = re.compile(r'"' + re.escape(s[:80]) + r'[A-Za-z0-9+/=\s]*"')
            new_block = pat.sub(lambda _: '"' + nb64 + '"', new_block, count=1)
            fixed += len(changed)
            print(f"  ✅ 修 {changed}")
    if fixed:
        data = data[:block_start] + new_block + data[block_end:]
        total += fixed

# ========== 写回 + 校验 ==========
open(HTML, "wb").write(data.encode("utf-8"))
print("\n" + "=" * 90)
print(f"共修 {total} 处")
print("=" * 90)

g = open(HTML, "rb").read().decode("utf-8", "replace")
print(f"  passage 明文: {len(re.findall(r'<tw-passagedata', g))}")
print(f"  passage 转义: {len(re.findall(r'&lt;tw-passagedata', g))}")
print(f"  大小: {len(g)/1048576:.2f} MB")

BAD = {
    "且 in <<if>>": sum(1 for m in re.finditer("且", g)
                       if "<<" in g[max(0, m.start() - 200):m.start() + 200]
                       and re.search(r"audience", g[max(0, m.start() - 200):m.start() + 200] or "")),
    "Tendrils of 深色ness": g.count("Tendrils of 深色ness"),
    "Your eyes itch": g.count("Your eyes itch"),
    'curvy: "Curvy"': g.count('curvy: "Curvy"'),
}
for k, v in BAD.items():
    print(f"  {'✅' if v == 0 else '❌'} {k}: {v}")

GOODCHECK = {
    "黑暗的触须": g.count("黑暗的触须"),
    "你的眼睛发痒": g.count("你的眼睛发痒"),
    'curvy: "曲线"': g.count('curvy: "曲线"'),
    "doggirl": g.count("doggirl"),
}
for k, v in GOODCHECK.items():
    print(f"  {'✅' if v > 0 else '❌'} {k}: {v}")
