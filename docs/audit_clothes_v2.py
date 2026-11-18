import zipfile, re, json, collections

P = r"E:\TAML\_dol\mods5\ClothesExtra.zip"
z = zipfile.ZipFile(P)
names = set(z.namelist())


def normalize(s):
    """把 JSON5 转成标准 JSON —— 先扫字符串边界，只对字符串外的部分做键加引号/去尾逗号。"""
    out = []
    i = 0
    n = len(s)
    in_str = False
    quote = ""
    while i < n:
        c = s[i]
        if in_str:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(s[i + 1]); i += 2; continue
            if c == quote:
                in_str = False
            i += 1
            continue
        if c in "\"'":
            in_str = True
            quote = c
            out.append('"' if c == "'" else c)
            i += 1
            continue
        out.append(c)
        i += 1
    t = "".join(out)
    # 去注释
    t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
    t = re.sub(r"(?m)^\s*//.*$", "", t)
    # 无引号键
    t = re.sub(r'([{,]\s*)([A-Za-z_$][A-Za-z0-9_$\u4e00-\u9fff]*)\s*:', r'\1"\2":', t)
    # 尾逗号
    t = re.sub(r",(\s*[}\]])", r"\1", t)
    return t


img_dirs = set()
for n in names:
    if n.startswith("img/clothes/"):
        p = n.split("/")
        if len(p) >= 4:
            img_dirs.add((p[2], p[3]))

tot = 0
bad = []
missing = []
dup = collections.Counter()
shop = collections.Counter()
byshop = collections.Counter()

for jf in sorted(n for n in names if n.startswith("clothes/") and n.endswith(".json")):
    raw = z.read(jf).decode("utf-8-sig")
    try:
        arr = json.loads(normalize(raw))
    except Exception as e:
        bad.append((jf, str(e)[:100]))
        continue
    cat = jf.split("/")[1].replace(".json", "")
    print(f"{jf:<26} {len(arr):>3} 件")
    for it in arr:
        if not isinstance(it, dict):
            continue
        var = it.get("variable")
        if not var:
            continue
        tot += 1
        dup[(cat, var)] += 1
        for s2 in (it.get("shop") or []):
            shop[s2] += 1
        if (cat, var) not in img_dirs:
            missing.append((cat, var, it.get("cn_name_cap") or it.get("name"), it.get("outfitSecondary")))

print(f"\n定义总数: {tot}")
print(f"解析失败: {len(bad)}")
for b in bad:
    print("   ", b)
print(f"\n无图片目录: {len(missing)}")
for m in missing:
    print(f"   {m[0]}/{m[1]}  {m[2]!r}  outfitSecondary={m[3]}")

d = {k: v for k, v in dup.items() if v > 1}
print(f"\n同部位 variable 重复: {len(d)}")
print("\n购买地点:", dict(shop))
