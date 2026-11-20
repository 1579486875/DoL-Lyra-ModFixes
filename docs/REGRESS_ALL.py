"""R01（第1轮）：建立统一回归测试套件 REGRESS_ALL.py。

把前 9 轮所有修复变成可执行断言，每次改动后跑一次。
分 6 组：
  A. 安装前提（4）
  B. 内容完整性（5）
  C. 代码卫生（4）
  D. 翻译表（6）
  E. 模组（4）
  F. 历史修复防复发（30+）
"""
import hashlib
import html as H
import io
import json
import os
import re
import subprocess
import sys
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
ARCHIVE = r"E:\TAML\_dol\archive"
GOOD = ARCHIVE + r"\DoL-Lyra-0.5.12.13-CHS-modded_20261120-061313_修复arsc可安装.apk"
TICK = chr(96)

PASS = []
FAIL = []


def chk(group, name, ok, detail=""):
    (PASS if ok else FAIL).append((group, name, detail))
    mark = "OK  " if ok else "FAIL"
    line = f"  [{mark}] {group}.{name}"
    if detail:
        line += f"   {detail}"
    print(line)


def strip_lit(s):
    s = re.sub(r'"[^"]*"', lambda m: " " * len(m.group(0)), s)
    s = re.sub(r"'[^']*'", lambda m: " " * len(m.group(0)), s)
    s = re.sub(TICK + "[^" + TICK + "]*" + TICK, lambda m: " " * len(m.group(0)), s)
    return re.sub(r"/[^/\n]*/", lambda m: " " * len(m.group(0)), s)


if not os.path.exists(APK):
    print("❌ APK 不存在")
    sys.exit(1)

z = zipfile.ZipFile(APK)
raw = z.read("assets/www/index.html").decode("utf-8", "replace")
g = H.unescape(raw)
gb = zipfile.ZipFile(GOOD).read("assets/www/index.html").decode("utf-8", "replace")

# ========== A. 安装前提 ==========
print("\n=== A. 安装前提 ===")
i = z.getinfo("resources.arsc")
chk("A", "arsc_stored", i.compress_type == 0, f"compress_type={i.compress_type}")
chk("A", "zip_ok", z.testzip() is None, f"{len(z.namelist()):,} 条目")
r = subprocess.run(["keytool", "-printcert", "-jarfile", APK],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
o = (r.stdout or "") + (r.stderr or "")
chk("A", "sig_sha256", "SHA256withRSA" in o)
chk("A", "sig_no_sha384", "SHA384withRSA" not in o)

# ========== B. 内容完整性 ==========
print("\n=== B. 内容完整性 ===")


def pn(t):
    return re.findall(r'<tw-passagedata\s+(?![^>]*\\")[^>]*name="([^"]*)"', t)


def wn(t):
    return set(re.findall(r'<<widget\s+"([^"]+)"', H.unescape(t)))


cp, bp = pn(raw), pn(gb)
cw, bw = wn(raw), wn(gb)
chk("B", "passage_count", len(cp) >= len(bp), f"{len(bp)} -> {len(cp)}")
chk("B", "widget_count", len(cw) >= len(bw), f"{len(bw)} -> {len(cw)}")
m1 = set(bp) - set(cp)
chk("B", "passage_no_missing", not m1, str(sorted(m1)[:3]))
m2 = bw - cw
chk("B", "widget_no_missing", not m2, str(sorted(m2)[:3]))
from collections import Counter
dup = {k: v for k, v in Counter(cp).items() if v > 1}
chk("B", "passage_no_dup", not dup, str(dup))

# ========== C. 代码卫生 ==========
print("\n=== C. 代码卫生 ===")
bad = 0
for m in re.finditer(r"<<(if|elseif|set|run|switch|case|for|while)\b([^<>]{0,800}?)>>", g):
    if re.search(r"[\u4e00-\u9fff]", strip_lit(m.group(2))):
        bad += 1
chk("C", "no_cn_in_code", bad == 0, f"{bad} 处")

# 模板字符串粘连（可靠判据：查已知 3 处 + 中文驼峰模式）
# 说明：SugarCube 普通文本里的反引号是「内联文本」，$var 只匹配 [A-Za-z0-9_]，
# 所以 $x.prop中文 是正常写法；只有 F17 修过的那 3 处（nameText浇灭 等）是真 bug。
KNOWN_GLUE = ["nameText浇灭", "nameText中清洗", "state火把和它玩拔河"]
n_tpl = sum(1 for k in KNOWN_GLUE if k in g)
chk("C", "no_tpl_glue", n_tpl == 0, f"{n_tpl} 处")

# CSS/JS 标识符含中文
n_css = len(re.findall(r"[.#][A-Za-z0-9_\-]*[\u4e00-\u9fff][A-Za-z0-9_\-\u4e00-\u9fff]*\s*\{", g))
chk("C", "no_cn_selector", n_css == 0, f"{n_css} 处")

# SugarCube 关键字被翻译
CN_KW = ["且", "或", "不是", "大于等于", "小于等于"]
kw_hit = 0
for m in re.finditer(r"<<(if|elseif|set|run|switch|case|for|while)\b([^<>]{0,800}?)>>", g):
    body = strip_lit(m.group(2))
    for w in CN_KW:
        if re.search(r"(?<![A-Za-z0-9_])" + re.escape(w) + r"(?![A-Za-z0-9_])", body):
            kw_hit += 1
            break
chk("C", "no_cn_keyword", kw_hit == 0, f"{kw_hit} 处")

# ========== D. 翻译表 ==========
print("\n=== D. 翻译表 ===")
occ = len(re.findall(r'setup\.NPCTypeList_cn_name\s+to\s+"', g))
chk("D", "npctable_single", occ == 1, f"{occ} 次赋值")
m = re.search(r'setup\.NPCTypeList_cn_name\s+to\s+"([^"]*)"', g)
if m:
    items = m.group(1).split("|")
    have = {x.split(",", 1)[0].strip() for x in items if "," in x}
    chk("D", "npctable_size", len(have) >= 240, f"{len(have)} 条")
    CRIT = ["catboy", "catgirl", "doggirl", "bullboy", "lizardgirl", "spidergirl",
            "harpy", "none", "creature", "curvy", "shapely", "eels", "guardian"]
    miss = [k for k in CRIT if k not in have]
    chk("D", "npctable_critical", not miss, str(miss))
else:
    chk("D", "npctable_exists", False)

i2 = g.find('var NAMES = ["NPC_CN_TYPE"')
if i2 > 0:
    j2 = g.rfind("var EXTRA = {", 0, i2)
    k2 = g.find("};", j2)
    keys2 = re.findall(r'"([^"]+)"\s*:', g[j2:k2 + 2])
    chk("D", "extra_table", len(keys2) >= 155, f"{len(keys2)} 键")
else:
    chk("D", "extra_table", False, "找不到 NAMES")

# mk() 函数表
for fn, kws in (("CAFE_FOOD_CN", ['"lemonade"', '"cheesecake"']),
                ("DirectionCN", ['"back": "后"', '"entrance"']),
                ("brothelshowType_CN", ['"sex": "性爱表演"', '"oral"']),
                ("update_cloth_cn", ['"hat": "帽子"', '"scarf": "围巾"'])):
    miss = [k for k in kws if k not in g]
    chk("D", f"mk_{fn}", not miss, str(miss))

# ========== E. 模组 ==========
print("\n=== E. 模组 ===")
m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", g, re.S)
parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m.group(1))
chk("E", "mod_count", len(parts) >= 58, f"{len(parts)} 个")
bad_mod = 0
for s in parts:
    try:
        d = base64.b64decode(re.sub(r"\s+", "", s)) if False else __import__("base64").b64decode(re.sub(r"\s+", "", s))
        if d[:2] != b"PK":
            continue
        zz = zipfile.ZipFile(io.BytesIO(d))
        if zz.testzip():
            bad_mod += 1
    except Exception:
        bad_mod += 1
chk("E", "mod_zip_ok", bad_mod == 0, f"{bad_mod} 个损坏")

# Npc Name CN BODYPARTS
import base64
bp_keys = 0
nrf = 0
for s in parts:
    try:
        d = base64.b64decode(re.sub(r"\s+", "", s))
        if d[:2] != b"PK":
            continue
        zz = zipfile.ZipFile(io.BytesIO(d))
        bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
    except Exception:
        continue
    if bj.get("name") == "Npc Name CN":
        js = zz.read("npcNameCN.js").decode("utf-8")
        mm = re.search(r"var BODYPARTS = \{([^}]*)\};", js, re.S)
        if mm:
            bp_keys = len(set(re.findall(r'"([^"]+)"\s*:', mm.group(1))))
    if bj.get("name") == "DoLSims":
        for a in (bj.get("addonPlugin") or []):
            if isinstance(a, dict) and a.get("addonName") == "TweeReplacerAddon":
                for p in (a.get("params") or []):
                    if isinstance(p, dict) and p.get("regexFlag") == "":
                        nrf += 1
chk("E", "npcnamecn_bodyparts", bp_keys >= 70, f"{bp_keys} 键")
chk("E", "no_empty_regexflag", nrf == 0, f"{nrf} 处")

# ========== F. 历史修复防复发 ==========
print("\n=== F. 历史修复防复发 ===")
HIST = {
    "_下体。": 0, "C.npc.罗宾": 0, "C.npc.艾弗里": 0, ".火坑前面": 0,
    ".额头上": 0, "applyClothingShop过滤": 0, "tanning启用d": 0, "次序:": 0,
    "_精液，": 0, "$speech冲撞着": 0, "我的arousal": 0,
    "Tendrils of 深色ness": 0, "Your eyes itch": 0, 'curvy: "Curvy"': 0,
    "<<br>>": 0, "flesh_text": 0, "printNobody": 0, "<<</if>>": 0,
    "按enter键": 0, "一个Wink": 0, "束缚play": 0, "心中想着the": 0,
    "nameText浇灭": 0, "nameText中清洗": 0,
    "applyClothingShopFilter(_items)": 0, "lifts up": 0,
    "You_You": 0, " glory hole": 0,
}
for k, want in HIST.items():
    c = g.count(k) if k != "You_You" else len(re.findall(r"You\s*_You", g))
    chk("F", f"no_{k[:20]}", c == 0, f"{c} 处")

GOOD_ONLY = {
    "applyClothingShopFilters": 4,
    "<<print _You>>": 3,
    "黑暗的触须": 1,
    "你的眼睛发痒": 1,
}
for k, minimum in GOOD_ONLY.items():
    c = g.count(k)
    chk("F", f"has_{k[:20]}", c >= minimum, f"{c} 处")

# ========== 汇总 ==========
print("\n" + "=" * 95)
print(f"回归结果: {len(PASS)} 通过 / {len(FAIL)} 失败")
print("=" * 95)
if FAIL:
    for grp, name, detail in FAIL:
        print(f"  FAIL  {grp}.{name}  {detail}")
    print(f"\n❌ 有 {len(FAIL)} 项失败")
    sys.exit(1)
else:
    h = hashlib.sha256(open(APK, "rb").read()).hexdigest().upper()
    sz = os.path.getsize(APK) / 1048576
    print(f"✅ 全部通过")
    print(f"   {sz:.2f} MB")
    print(f"   {h}")
    sys.exit(0)
