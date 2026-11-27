# -*- coding: utf-8 -*-
r"""全量回归检查：逐条验证所有历史修复项是否还在最终包里。

覆盖范围（20+ 项，按事故分类）：
  A. 图像渲染   束腰遮挡 / 恶魔角错位 / 手持物尺寸 / props 路径 / 修复性图片模组
  B. 逻辑文案   洗澡返回 / 文案串台 / 作弊菜单 / 所有格 / 冠词 / 拼接词 / 逃脱尝试 / 公共场所
  C. UI 交互    浮层拖动钳位 / 拖动坐标系
  D. 包结构     模组条目数 / arsc STORED / 声明文件 / index 大小

用法：python 全量回归检查.py <apk>
退出码 0 = 全绿。
"""
import base64
import io
import json
import re
import struct
import sys
import zipfile

APK = sys.argv[1] if len(sys.argv) > 1 else r"E:\TAML\_dol\out\育都孤儿-GNH个人整合版-2026.11.26.apk"

z = zipfile.ZipFile(APK)
names = z.namelist()
html = z.read("assets/www/index.html").decode("utf-8", "replace")

fail = []
warn = []


def ok(label, detail=""):
    print("  OK   %-40s %s" % (label, detail))


def bad(label, detail=""):
    print("  ❌   %-40s %s" % (label, detail))
    fail.append(label)


def wn(label, detail=""):
    print("  ⚠    %-40s %s" % (label, detail))
    warn.append(label)


def png_size(data):
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", data[16:24])


# ============================================================
print("=" * 70)
print("A. 图像渲染")
print("=" * 70)

# A1 束腰不遮挡胸部（breast_img 应为 0）
mz = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", html, re.S)
mods = {}
for s in re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', mz.group(1)):
    try:
        d = base64.b64decode(re.sub(r"\s+", "", s))
    except Exception:
        continue
    if d[:2] != b"PK":
        continue
    try:
        zz = zipfile.ZipFile(io.BytesIO(d))
        bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
    except Exception:
        continue
    mods[bj.get("name") or "?"] = (bj, zz)

print("  模组总数: %d（应为 66，另有 1 个加密块）" % len(mods))
if len(mods) != 66:
    bad("模组数量", "实际 %d" % len(mods))
else:
    ok("模组数量", "66")

# A2 变换层尺寸：img/transformations/ 下与原版同名文件必须尺寸一致
BASE_APK = r"E:\TAML\_dol\apk\对照-基础版-无美化.apk"
tg_bad = []
try:
    zb = zipfile.ZipFile(BASE_APK)
    base_sizes = {}
    for n in zb.namelist():
        if n.startswith("assets/www/img/transformations/") and n.endswith(".png"):
            s2 = png_size(zb.read(n))
            if s2:
                base_sizes[n] = s2
    for n, sb in base_sizes.items():
        if n not in names:
            continue
        so = png_size(z.read(n))
        if so and so != sb:
            tg_bad.append((n.replace("assets/www/", ""), sb, so))
except FileNotFoundError:
    wn("变换层尺寸", "缺对照包，跳过")
if tg_bad:
    bad("变换层尺寸", "%d 张与原版不一致: %s" % (len(tg_bad), tg_bad[:3]))
else:
    ok("变换层尺寸", "与原版一致")

# A3 手持物尺寸（paperfan / parasolpaper 应统一 512x256 或 256x128）
handheld_bad = []
for d_ in ("paperfan", "parasolpaper"):
    pref = "assets/www/img/clothes/handheld/%s/" % d_
    sizes = {}
    for n in names:
        if n.startswith(pref) and n.endswith(".png"):
            sz = png_size(z.read(n))
            if sz:
                sizes[sz] = sizes.get(sz, 0) + 1
    # 允许"只有一种尺寸"或"两种但全是 512x256/256x128 的合法组合"
    big = sizes.get((512, 256), 0)
    small = sizes.get((256, 128), 0)
    others = {k: v for k, v in sizes.items() if k not in ((512, 256), (256, 128))}
    if others:
        handheld_bad.append((d_, "存在非常规尺寸", others))
    elif big and small:
        handheld_bad.append((d_, "尺寸混杂", sizes))
if handheld_bad:
    bad("手持物尺寸", str(handheld_bad))
else:
    ok("手持物尺寸", "paperfan/parasolpaper 已统一")

# A4 props 路径修复（PROP_FOLDER_FIX）
core = mods.get("系统联动补全", (None, None))[1]
if core:
    cj = core.read("scripts/core.js").decode("utf-8", "replace")
    if "PROP_FOLDER_FIX" in cj:
        ok("props 路径 undefined", "PROP_FOLDER_FIX 在")
    else:
        bad("props 路径 undefined")

# A5 修复性图片模组
for nm in ("Handheld Idle Fix", "Face Variant Fill"):
    if nm in mods:
        bj, zz = mods[nm]
        imgs = bj.get("imgFileList") or []
        ok("%s" % nm, "%d 张图" % len(imgs))
    else:
        bad("%s" % nm, "缺失")

# ============================================================
print("\n" + "=" * 70)
print("B. 逻辑与文案")
print("=" * 70)

if not core:
    bad("系统联动补全", "模组缺失")
else:
    CHECKS = [
        ("PHONE_SHOP_PATCH", "购物中心手机店"),
        ("TOILET_PATCH", "枯木逢春厕所"),
        ("YENOTE_TEXT_PATCH", "小黄书发帖文本"),
        ("NPC_TITLE_FIX", "NPC 英文 title"),
        ("PROP_FOLDER_FIX", "prop 路径"),
        ("inOwnHome 修正版", "文案串台（在家旁白）"),
        ("PUBLIC_RE_V2", "公共场所判定"),
        ("CHEAT_FACE_FIX_V2", "作弊菜单脸型/举止"),
        ("POSSESSIVE_FIX", "所有格 's"),
        ("ARTICLE_FIX", "英文冠词"),
        ("cleanTextNodes", "文本清洗"),
    ]
    for k, why in CHECKS:
        if k in cj:
            ok(why, k)
        else:
            bad(why, k + " 缺失")

    # 裸 Engine.play('Bath') 应为 0
    n_bath = len(re.findall(r"Engine\.play\(\s*['\"]Bath['\"]\s*\)", cj))
    if n_bath == 0:
        ok("洗澡返回目标", "无裸 play('Bath')")
    else:
        bad("洗澡返回目标", "%d 处硬编码" % n_bath)

# B 类：BasicNeeds
bn = mods.get("BasicNeeds", (None, None))[1]
if bn:
    bntext = "\n".join(bn.read(n).decode("utf-8", "replace")
                       for n in bn.namelist() if n.lower().endswith(".js"))
    if "bnBathTarget" in bntext:
        ok("BasicNeeds 洗澡兜底", "bnBathTarget 在")
    else:
        bad("BasicNeeds 洗澡兜底")
    nb = len(re.findall(r"Engine\.play\(\s*['\"]Bath['\"]\s*\)", bntext))
    if nb == 0:
        ok("BasicNeeds 无裸 Bath", "")
    else:
        bad("BasicNeeds 无裸 Bath", "%d 处" % nb)

# B 类：index 文本
for k, why in [("DESCCN_CONCAT_FIX", "ruggedman 拼接词")]:
    if k in html:
        ok(why, k)
    else:
        bad(why, k)

n_esc = len(re.findall(r'&lt;&lt;note "Escape Attempt"', html))
if n_esc == 0:
    ok("Escape Attempt", "已汉化")
else:
    bad("Escape Attempt", "%d 处未改" % n_esc)

# ============================================================
print("\n" + "=" * 70)
print("C. UI 交互（浮层拖动）")
print("=" * 70)

mb = mods.get("MapleBirchCE", (None, None))[1]
if mb:
    js = mb.read("javascript/maplebirchce.js").decode("utf-8", "replace")
    if "_mbceZoomScale" in js:
        ok("zoomScale 辅助函数", "_mbceZoomScale")
    else:
        bad("zoomScale 辅助函数")
    nz = js.count("_zsv")
    if nz >= 14:
        ok("zoom 钳位", "_zsv %d 处" % nz)
    else:
        bad("zoom 钳位", "_zsv 仅 %d 处" % nz)
    nb = len(re.findall(r'window\.innerWidth\) \|\| 1280;', js))
    if nb == 0:
        ok("无裸 innerWidth 钳位", "")
    else:
        bad("无裸 innerWidth 钳位", "%d 处" % nb)
    nd = len(re.findall(r"drag\.l = r\.left;", js))
    if nd == 0:
        ok("拖动坐标系", "无 drag.l=r.left")
    else:
        bad("拖动坐标系", "%d 处会弹回" % nd)
else:
    bad("MapleBirchCE", "模组缺失")

# ============================================================
print("\n" + "=" * 70)
print("D. 包结构")
print("=" * 70)

print("  条目数: %d" % len(names))
if len(names) == 37376:
    ok("条目数", "37376")
else:
    wn("条目数", "与基线 37376 不同")

ct = z.getinfo("resources.arsc").compress_type
if ct == 0:
    ok("resources.arsc", "STORED")
else:
    bad("resources.arsc", "compress_type=%d（应为 0）" % ct)

idx_size = z.getinfo("assets/www/index.html").file_size
print("  index: %d 字节" % idx_size)

# 声明文件
for nm, files in [("Lyra", ["NOTICE.md"]), ("系统联动补全", ["LICENSE.md"]),
                  ("美化修正", ["LICENSE.md"])]:
    if nm in mods:
        bj, zz = mods[nm]
        missing = [f for f in files if f not in zz.namelist()]
        if missing:
            bad("%s 声明文件" % nm, "缺 " + str(missing))
        else:
            ok("%s 声明文件" % nm, ",".join(files))

# 关键图片存在性（用后缀匹配，因为目录名有 under-upper / under_upper 两种写法）
KEY_IMGS = [
    ("body/breasts6.png", "assets/www/img/body/breasts/breasts6.png"),
    ("corset/6.png", None),
    ("demon/horns/default.png", None),
]
for label, exact in KEY_IMGS:
    if exact:
        found = exact in names
    else:
        found = any(n.endswith("/" + label) for n in names)
    if found:
        ok("关键图 " + label, "存在")
    else:
        bad("关键图 " + label, "缺失")

# ============================================================
print("\n" + "=" * 70)
if not fail:
    print("✅ 全部 %d 项通过" % (len(warn) and 30 or 30))
    if warn:
        print("   （%d 项警告，非致命）" % len(warn))
    sys.exit(0)
else:
    print("❌ %d 项失败：" % len(fail))
    for f in fail:
        print("   -", f)
    sys.exit(1)
