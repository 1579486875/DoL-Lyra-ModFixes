"""E33：查 exec_verify 的所有测试用例，补齐 NPCTypeList_cn_name。"""
import html as H
import os
import re

WORK = r"E:\TAML\_dol\work"
HTML = os.path.join(WORK, "index_modded6.html")
EV = os.path.join(WORK, "exec_verify.py")

# 1) 提取 exec_verify 的测试用例
src = open(EV, encoding="utf-8").read()
cases = re.findall(r'\(\s*"([a-z][a-z \-]*)"\s*,\s*"([^"]+)"\s*\)', src)
print("=" * 90)
print(f"exec_verify 测试用例 {len(cases)} 个")
print("=" * 90)
for k, v in cases:
    print(f"  {k!r} -> {v!r}")

# 2) 读当前表
data = open(HTML, "rb").read().decode("utf-8", "replace")
g = H.unescape(data)
m = re.search(r'<<set setup\.NPCTypeList_cn_name to "([^"]*)"', g)
if not m:
    raise SystemExit("❌ 找不到 NPCTypeList_cn_name")

cur = m.group(1)
have = {}
for item in cur.split("|"):
    if "," in item:
        k, v = item.split(",", 1)
        have[k.strip()] = v.strip()

print("\n" + "=" * 90)
print(f"当前表 {len(have)} 项")
print("=" * 90)

# 3) 找缺失
missing = []
for k, v in cases:
    if k not in have:
        missing.append((k, v))
    elif have[k] != v:
        print(f"  ⚠️ 不一致: {k!r} 表={have[k]!r} 期望={v!r}")

print(f"\n缺失 {len(missing)} 个:")
for k, v in missing:
    print(f"  {k} -> {v}")

# 4) 额外补一批常见复数/变体
EXTRA = {
    "eels": "鳗鱼", "dogs": "狗", "wolves": "狼", "cats": "猫", "bears": "熊",
    "horses": "马", "cows": "奶牛", "bulls": "公牛", "pigs": "猪", "foxes": "狐狸",
    "sheep": "绵羊", "deer": "鹿", "spiders": "蜘蛛", "slimes": "史莱姆",
    "plants": "植物", "snakes": "蛇", "frogs": "青蛙", "birds": "鸟",
    "tentacles": "触手", "humans": "人类", "creatures": "生物",
    "wolfgirls": "狼娘", "doggirls": "狗娘", "catgirls": "猫娘",
    "wolfboys": "狼男", "dogboys": "狗男", "catboys": "猫男",
}

need_add = []
for k, v in missing:
    need_add.append((k, v))
for k, v in EXTRA.items():
    if k not in have and k not in [x[0] for x in need_add]:
        need_add.append((k, v))

print(f"\n要补 {len(need_add)} 个")

if need_add:
    items = [f"{k},{v}" for k, v in need_add]
    new_str = cur.rstrip("|") + "|" + "|".join(items) + "|"
    # 直接在 data 上按位置替换（用 m 是从 g 来的，需重新在 data 上定位）
    m2 = None
    for pat in (r'(<<set setup\.NPCTypeList_cn_name to ")([^"]*)(">>)',
                r'(&lt;&lt;set setup\.NPCTypeList_cn_name to ")([^"]*)("&gt;&gt;)'):
        m2 = re.search(pat, data)
        if m2:
            break
    if not m2:
        raise SystemExit("❌ 在 data 上找不到")
    data = data[:m2.start(2)] + new_str + data[m2.end(2):]
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"✅ 已写入，新长度 {len(new_str)}")

# 5) 校验
gg = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
m3 = re.search(r'<<set setup\.NPCTypeList_cn_name to "([^"]*)"', gg)
if m3:
    s = m3.group(1)
    have2 = {}
    for item in s.split("|"):
        if "," in item:
            k, v = item.split(",", 1)
            have2[k.strip()] = v.strip()
    print(f"\n=== 校验（{len(have2)} 项）===")
    allok = True
    for k, v in cases:
        got = have2.get(k, "❌缺")
        ok = (got == v)
        if not ok:
            allok = False
            print(f"  ❌ {k!r}: 表={got!r} 期望={v!r}")
    print(f"  {'✅ 全部测试用例通过' if allok else '❌ 仍有缺失'}")
    print(f"  passage: {len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML,'rb').read().decode('utf-8','replace')))}")
