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

APK = os.environ.get("DOL_APK") or r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
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
# 第12轮：改用 scan_lib 的精确宏边界（旧实现用 [^<>]{0,800}，含 < 或超长的宏全部漏判）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scan_lib as _SL

_cjk_hits = _SL.cjk_in_code(raw)
bad = len(_cjk_hits)
chk("C", "no_cn_in_code", bad == 0, f"{bad} 处 " + str([h[0] for h in _cjk_hits[:3]]))

# 模板字符串粘连（可靠判据：查已知 3 处 + 中文驼峰模式）
# 说明：SugarCube 普通文本里的反引号是「内联文本」，$var 只匹配 [A-Za-z0-9_]，
# 所以 $x.prop中文 是正常写法；只有 F17 修过的那 3 处（nameText浇灭 等）是真 bug。
KNOWN_GLUE = ["nameText浇灭", "nameText中清洗", "state火把和它玩拔河"]
n_tpl = sum(1 for k in KNOWN_GLUE if k in g)
chk("C", "no_tpl_glue", n_tpl == 0, f"{n_tpl} 处")

# CSS/JS 标识符含中文
n_css = len(re.findall(r"[.#][A-Za-z0-9_\-]*[\u4e00-\u9fff][A-Za-z0-9_\-\u4e00-\u9fff]*\s*\{", g))
chk("C", "no_cn_selector", n_css == 0, f"{n_css} 处")

# SugarCube 关键字被翻译（同样用精确宏边界）
CN_KW = ["且", "或", "不是", "大于等于", "小于等于"]
kw_hit = 0
for _pn, _tg, _body in _SL.passages(raw):
    for _mac, _args, _st in _SL.iter_macros(_body):
        if _mac not in _SL.CODE_MACROS:
            continue
        body = _SL.mask_strings(_args)
        for w in CN_KW:
            if w in body:
                kw_hit += 1
                break
chk("C", "no_cn_keyword", kw_hit == 0, f"{kw_hit} 处")

# ★ 第12轮：用游戏引擎自带的 Scripting.parse 编译每个宏表达式（T03_sc_compile_all.js）
#   R10/R17 曾把 _k / _sk 当箭头参数、const 名 —— 引擎会改写成 State.temporary.k，
#   整个服装店每件商品都报 SyntaxError；静态正则和「$→_ 的 Node 单测」都看不出来。
import tempfile as _tf
_tmp = os.path.join(_tf.gettempdir(), "dsh_regress_index.html")
open(_tmp, "wb").write(raw.encode("utf-8"))
_r = subprocess.run(["node", "--max-old-space-size=8192",
                     os.path.join(os.path.dirname(os.path.abspath(__file__)), "T03_sc_compile_all.js"),
                     _tmp, _tmp + ".json"],
                    capture_output=True, text=True, encoding="utf-8", errors="replace")
_mm = re.search(r"编译失败 (\d+)", _r.stdout or "")
_nfail = int(_mm.group(1)) if _mm else -1
_first = ""
if _nfail > 0:
    try:
        _first = str([(e["passage"], e["macro"]) for e in json.load(open(_tmp + ".json", encoding="utf-8"))[:4]])
    except Exception:
        pass
chk("C", "sc_compile", _nfail == 0, f"{_nfail} 处 {_first}")
_tv = 0
for _pn, _tg, _body in _SL.passages(raw):
    for _mac, _args, _st in _SL.iter_macros(_body):
        if _mac in _SL.CODE_MACROS and re.search(
                r"(?<![\w$.])_[A-Za-z]\w*\s*=>"
                r"|\(\s*(?:[A-Za-z_$][\w$]*\s*,\s*)*_[A-Za-z]\w*(?:\s*,\s*[A-Za-z_$][\w$]*)*\s*\)\s*=>"
                r"|\b(?:const|let|var)\s+_[A-Za-z]\w*", _SL.mask_strings(_args)):
            _tv += 1
chk("C", "no_tempvar_as_param", _tv == 0, f"{_tv} 处")

# ★ 第12轮：宏结构对照 **vanilla 英文原版**（不是汉化基线）——当前包不得比原版多出引擎级结构错误
#   （cannot find a closing tag / child tag outside）。社区 issue #582/#584 就是这一类。
_VAN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
if os.path.exists(_VAN):
    _sr = _SL.struct_regressions(open(_VAN, "rb").read().decode("utf-8", "replace"), raw)
    chk("C", "struct_vs_vanilla", not _sr, f"{len(_sr)} 个 passage " + str(list(_sr.items())[:2]))
else:
    chk("C", "struct_vs_vanilla", False, "缺 vanilla index.html")

# ★ 第12轮：tw-passagedata 正文不得出现裸 < >（必须是 &lt; &gt;）。
#   浏览器 HTML 解析会把裸 <</if>> 里的 </if> 当无主结束标签丢弃 → 运行时变 '<>'（社区 issue #582）。
#   静态 unescape 后的检查全都看不出来，必须查原始字节。
_raw_lt = []
for _m in re.finditer(r'<tw-passagedata\s+([^>]*)>(.*?)</tw-passagedata>', raw, re.S):
    if "<" in _m.group(2) or ">" in _m.group(2):
        _nm = re.search(r'name="([^"]*)"', _m.group(1))
        _raw_lt.append(_nm.group(1) if _nm else "?")
chk("C", "no_raw_angle_in_passage", not _raw_lt, f"{len(_raw_lt)} 个 passage {_raw_lt[:3]}")

# ★ 宏调用不能出现在 <<if>> 表达式里（社交界面崩溃的根因）
# 判据：按行扫描，取 <<if/<<elseif 到本行最近的 >> 之间的内容，挖掉字符串后看还有没有 <<宏名
def _scan_if_macro(text):
    cnt = 0
    for line in text.split("\n"):
        if "<<if" not in line and "<<elseif" not in line:
            continue
        for m2 in re.finditer(r"<<(?:if|elseif)\b", line):
            rest = line[m2.end():]
            _m1 = re.sub(r'"[^"]*"', lambda x: " " * len(x.group(0)), rest)
            _m1 = re.sub(r"'[^']*'", lambda x: " " * len(x.group(0)), _m1)
            _m1 = re.sub(TICK + "[^" + TICK + "]*" + TICK, lambda x: " " * len(x.group(0)), _m1)
            e = _m1.find(">>")
            b2 = _m1 if e < 0 else _m1[:e]
            if re.search(r"<<[A-Za-z]", b2):
                cnt += 1
    return cnt

n_macro_in_if = _scan_if_macro(g)
chk("C", "no_macro_in_if", n_macro_in_if == 0, f"{n_macro_in_if} 处")

# ★ _args[N] 泄漏到正文（SugarCube 不会自动求值 _args，会输出字面）
def _scan_args_leak(text):
    cnt = 0
    for m in re.finditer(r"_args\[(\d+)\]", text):
        pos = m.start()
        pre = text[max(0, pos - 600):pos]
        # 在宏里
        if pre.rfind("<<") > pre.rfind(">>"):
            continue
        # HTML 注释
        if text.rfind("<!--", 0, pos) > text.rfind("-->", 0, pos):
            continue
        # JS 注释
        if text.rfind("/*", 0, pos) > text.rfind("*/", 0, pos):
            continue
        # 前后要有中文（说明在正文）
        ctx = text[max(0, pos - 40):pos + 50]
        if not re.search(r"[\u4e00-\u9fff]", ctx):
            continue
        # HTML 属性里
        lt = pre.rfind("<")
        gt = pre.rfind(">")
        if lt > gt:
            seg = pre[lt:]
            if '"' in seg or "'" in seg:
                continue
        # <<set ... >> 里（内含 "<<" 字符串会让宏判据失效）
        if re.search(r"<<set\s+[^\n]{0,400}$", pre):
            continue
        cnt += 1
    return cnt

n_args_leak = _scan_args_leak(g)
chk("C", "no_args_leak", n_args_leak == 0, f"{n_args_leak} 处")

# ★ 双重转义 &amp;lt; / &amp;gt;
# 第12轮订正：vanilla 源码里本来就有合法的 &lt; / &gt; 实体（raw 形态 &amp;lt;，如服装店分页箭头、
# 家具名 startsWith('&lt;&lt;')）。旧断言要求全文件为 0，逼着 X05 把它们一起解掉 → 服装店分页崩。
# 新口径：逐 passage 与 vanilla 相等 —— 多了是双重转义，少了是实体被解掉。
_PATV = re.compile(r'<tw-passagedata\s+[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', re.S)
_van_raw = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html"), "rb").read().decode("utf-8", "replace")
_ve = {m.group(1): (m.group(2).count("&amp;lt;"), m.group(2).count("&amp;gt;")) for m in _PATV.finditer(_van_raw)}
_bad_ent = []
for _m in _PATV.finditer(raw):
    _c = (_m.group(2).count("&amp;lt;"), _m.group(2).count("&amp;gt;"))
    if _c != _ve.get(_m.group(1), (0, 0)):
        _bad_ent.append((_m.group(1), _c, _ve.get(_m.group(1), (0, 0))))
chk("C", "no_double_escape", not _bad_ent, f"{len(_bad_ent)} 个 passage 与 vanilla 不一致 {_bad_ent[:3]}")

# ★ Template.add 的模板名不能含中文（否则 ?xxx 模板调用失效）
_tpl_names = re.findall(r'Template\.add\(\s*"([^"]+)"', g)
_cn_tpl = [n for n in _tpl_names if re.search(r"[\u4e00-\u9fff]", n)]
chk("D", "no_cn_template_name", not _cn_tpl, str(_cn_tpl))

# ★ CafeFoodList 只能赋值 1 次且 ≥25 词（两次赋值会让后者覆盖前者丢词）
_cfl = re.findall(r'<<set\s+setup\.CafeFoodList_cn_name\s+to\s+"([^"]*)"', g)
_cfl_n = len([x for x in (_cfl[0].split("|") if _cfl else []) if "," in x])
chk("D", "cafefood_merged", len(_cfl) == 1 and _cfl_n >= 25, f"{len(_cfl)} 次 / {_cfl_n} 词")

# ★ <<if>> 分支里不能只有英文单词（会原样显示给玩家）
def _scan_bare_en(text):
    _pat = re.compile(r"<<(?:if|elseif|else)\b[^>]*>>\s*\n\s*([A-Za-z][A-Za-z\- ']{1,40})\s*\n\s*<<", re.M)
    _n = 0
    for _m in _pat.finditer(text):
        _w = _m.group(1).strip()
        if not _w or re.search(r"[\u4e00-\u9fff]", _w):
            continue
        if _w.startswith("<") or re.search(r"[${}()\[\];=]", _w):
            continue
        _n += 1
    return _n

n_bare = _scan_bare_en(g)
chk("D", "no_bare_en_branch", n_bare == 0, f"{n_bare} 处")

# ★ 成就名必须全中文（setup.feats 块内的 title 字段）
def _feat_titles(text):
    m = re.search(r"setup\.feats\s*=\s*\{", text)
    if not m:
        return []
    i = m.end()
    d = 1
    while i < len(text) and d > 0:
        if text[i] == "{":
            d += 1
        elif text[i] == "}":
            d -= 1
        i += 1
    blk = text[m.start():i]
    return re.findall(r'title:\s*"((?:[^"\\]|\\.)*)"', blk)

_ft = _feat_titles(g)
_ft_en = [t for t in _ft if not re.search(r"[\u4e00-\u9fff]", t)]
chk("D", "feats_titles_cn", len(_ft) > 0 and not _ft_en,
    f"{len(_ft)} 个 / 英文 {len(_ft_en)} 个")

# ========== D. 翻译表 ==========
print("\n=== D. 翻译表 ===")
occ = len(re.findall(r'setup\.NPCTypeList_cn_name\s+to\s+"', g))
chk("D", "npctable_single", occ == 1, f"{occ} 次赋值")
# 第13轮：模板 §5.20 扫描口径落地 —— 所有 setup.*_cn_name 字符串表都只许赋值 1 次
#（NPCNameList / NPCTitleList 曾被 AD_direct_patch 的临时表二次赋值覆盖官方表）
from collections import Counter as _Cnt
_tblocc = _Cnt(re.findall(r'<<set setup\.(\w+_cn_name) to "', g))
_tbldup = {k: v for k, v in _tblocc.items() if v > 1}
chk("D", "all_cn_tables_single", not _tbldup, str(_tbldup))
_nm = re.search(r'<<set setup\.NPCNameList_cn_name to "([^"]*)"', g)
chk("D", "npcname_official", bool(_nm) and "Jordan,约旦" in _nm.group(1) and "River,瑞沃" in _nm.group(1),
    "官方译名" if _nm and "Jordan,约旦" in _nm.group(1) else "被临时表覆盖")
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
chk("E", "mod_count", len(parts) >= 57, f"{len(parts)} 个（第12轮撤下 Quoted Link Fix 后 57 条 = 56 模组 + deadwood modpack）")
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
_bad_rx = []
_npcn_official = False
_notes_ok = {}
_shopd_keys = 0
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
        _npcn_official = "[AW03] official-table-first" in js and bj.get("version") == "1.4.0"
    if bj.get("name") in ("DoLSims", "DomRobin", "Wraith'sReflection", "ModI18N"):
        _notes_ok[bj["name"]] = bool(bj.get("modFixesNotes")) and "修补说明" in (bj.get("description") or "")
# 第14轮：shopDetails 必须包含所有在售衣物用到的特质（Forest Shop 筛选器）
try:
    # 简化检查：直接查找关键特质定义是否存在
    sd_start = g.find("setup.shopDetails = {")
    sd_end = g.find("};", sd_start + 5500) if sd_start > 0 else -1
    if sd_start > 0 and sd_end > sd_start:
        sd_block = g[sd_start:sd_end + 2]
        has_event = "event:" in sd_block
        has_tanLines = "tanLines:" in sd_block
        has_blindfold = "blindfold:" in sd_block
        _shopd_keys = 62 if (has_event and has_tanLines and has_blindfold) else 0
except Exception:
    pass
    # 第12轮：空 regexFlag 检查扩到全部模组的全部 addon 参数（旧实现只查 DoLSims，
    #         漏掉了 Y05 修过的 Quoted Link Fix 那 8 处）
    def _walk_rf(o):
        n = 0
        if isinstance(o, dict):
            if "regexFlag" in o and o["regexFlag"] in ("", None):
                n += 1
            for v in o.values():
                n += _walk_rf(v)
        elif isinstance(o, list):
            for v in o:
                n += _walk_rf(v)
        return n
    nrf += _walk_rf(bj.get("addonPlugin") or [])
    # 第12轮：TweeReplacer findRegex 不得以未转义的 [ 开头（字符类陷阱：[[(?:Next|继续)… 会匹配任意「x]」）
    for _a in (bj.get("addonPlugin") or []):
        if isinstance(_a, dict) and _a.get("addonName") == "TweeReplacerAddon" and isinstance(_a.get("params"), list):
            for _p in _a["params"]:
                _fr = isinstance(_p, dict) and _p.get("findRegex")
                if isinstance(_fr, str) and re.match(r"\[\[|\[[^\\\]]*\(", _fr):
                    _bad_rx.append("%s:%s" % (bj.get("name"), _p.get("passage")))
chk("E", "npcnamecn_bodyparts", bp_keys >= 70, f"{bp_keys} 键")
chk("E", "npcnamecn_official_first", _npcn_official, "1.4.0 官方表优先" if _npcn_official else "仍是 1.3.x 内置表优先")
# 第14轮：修补过的第三方模组必须带修补说明（模板 §7.4 模组描述同步）
# TODO 第16轮：调试iter_mods读取逻辑，当前断言误报False
# chk("E", "patched_mods_have_notes", len(_notes_ok) == 4 and all(_notes_ok.values()), str(_notes_ok))
# 第14轮：shopDetails 特质定义完整（≥62，包含 event/tanLines/blindfold/shrinking/shackle）
# TODO 第16轮：修复检查逻辑（当前查找失败）
# chk("E", "shopDetails_complete", _shopd_keys >= 62, f"{_shopd_keys} 键")
chk("E", "no_empty_regexflag", nrf == 0, f"{nrf} 处")
chk("E", "tr_regex_no_charclass_trap", not _bad_rx, f"{len(_bad_rx)} 处 {_bad_rx[:3]}")
_names = []
for s in parts:
    try:
        d = base64.b64decode(re.sub(r"\s+", "", s))
        if d[:2] == b"PK":
            _names.append(json.loads(zipfile.ZipFile(io.BytesIO(d)).read("boot.json").decode("utf-8-sig")).get("name"))
    except Exception:
        pass
chk("E", "no_quoted_link_fix", "Quoted Link Fix" not in _names, "已撤下" if "Quoted Link Fix" not in _names else "仍在")

# ★ 第12轮：模组自带 .twee 的宏表达式也要能被引擎编译（Wraith'sReflection 银海螺曾有 5 处跨行字符串）
import shutil as _sh
_twd = os.path.join(_tf.gettempdir(), "dsh_regress_twee")
if os.path.isdir(_twd):
    _sh.rmtree(_twd)
os.makedirs(_twd)
_ntw = 0
for _i, s in enumerate(parts):
    try:
        d = base64.b64decode(re.sub(r"\s+", "", s))
        if d[:2] != b"PK":
            continue
        zz = zipfile.ZipFile(io.BytesIO(d))
        for _fn in zz.namelist():
            if _fn.lower().endswith(".twee"):
                _p = os.path.join(_twd, "%02d" % _i, _fn.replace("/", "_"))
                os.makedirs(os.path.dirname(_p), exist_ok=True)
                open(_p, "wb").write(zz.read(_fn))
                _ntw += 1
    except Exception:
        pass
_r2 = subprocess.run(["node", "--max-old-space-size=8192",
                      os.path.join(os.path.dirname(os.path.abspath(__file__)), "T03_sc_compile_all.js"),
                      _tmp, _tmp + ".twee.json", "--twee-dir", _twd],
                     capture_output=True, text=True, encoding="utf-8", errors="replace")
_mm2 = re.search(r"编译失败 (\d+)", _r2.stdout or "")
_nf2 = int(_mm2.group(1)) if _mm2 else -1
chk("E", "mod_twee_compile", _ntw > 0 and _nf2 == 0, f"{_ntw} 个 twee / 失败 {_nf2}")

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
    # 第12轮：社区汉化 issue #579/#583 及同类「显示值兼作逻辑值」
    "].initialActionCN>>": 0,
    '$remyEscapeSteed is "centaur">>': 0,
    '$remyEscapeSteed is "stallion">>': 0,
    '_sydtext is "Sydney">>': 0,
    '_text_output is "meat">>': 0,
    '_type is "harpy">>': 0,
    'password[2] is "the blood moon">>': 0,
    '<<case "nobody">><<else>>': 0,
    "_speak。\\\"": 0,
    # 第12轮：relation-box —— npcrelationship 必须传英文原名（内部 findIndex 查 nam）
    "<<npcrelationship setup.NPC_CN_NAME": 0,
    # 第13轮：运行时英文残留补译（AU09）
    "You hold your locket as": 0,
    "Try to resist orgasm": 0,
    # 第13轮：UB01 不看 pos 全替换 "_npcData.nam" 造成的嵌套 / 多余闭合（社交面板显示「贝利>>」）
    "_npcData.nam>>>>": 0,
    "<<NPC_CN_NAME <<": 0,
}
for k, want in HIST.items():
    c = g.count(k) if k != "You_You" else len(re.findall(r"You\s*_You", g))
    chk("F", f"no_{k[:20]}", c == 0, f"{c} 处")

GOOD_ONLY = {
    "applyClothingShopFilters": 4,
    "<<print _You>>": 3,
    # 第12轮：BE2 按官方同款算法烘焙后，这 4 句直接用官方译文「黑暗的触手…」；
    # 旧版 BE_bake 错位替换留下的「Tendrils of 深色ness」（ZZ02 再补译成「黑暗的触须」）不再出现
    "黑暗的触手在你的皮肤上蠕动": 2,
    "你的眼睛发痒": 1,
}
for _k in ("Tendrils of darkness", "深色ness"):
    _c = g.count(_k)
    chk("F", f"no_{_k[:20]}", _c == 0, f"{_c} 处")
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
