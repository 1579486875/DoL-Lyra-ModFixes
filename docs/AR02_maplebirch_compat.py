"""AR02（第12轮）：修 DoLSims / DomRobin 被 maplebirch 5.6.2 抢先改写导致失配的 4 条 TweeReplacer 补丁（幂等）。

运行时日志（ModLoader）：
  [DoLSims]  findRegex <<widget "fallenTransform">>\\s*<<if \\$angel gte 6>>            in Transformation Widgets
  [DomRobin] findString <<if $robinpaid isnot 1 and $robindebtknown is 1>>               in Bailey's Office
  [DomRobin] findString <<if $robinpaid isnot 1>>                                         in Widgets Robin (robinpay)
  [DomRobin] findRegex  <<if (…$money gte 300|…VanillaPlus).finance.canPay(300,"cafe"))>> in Ocean Breeze
根因（运行时 passage 导出实测）：maplebirch 的 zone 补丁先于 TweeReplacer 执行，把
  · fallenTransform 开头包了一层 <<if not ($settings.transformDivineEnabled and …trinity)>>
  · 两处 robinpaid 条件追加了 and !maplebirch.get("Finance").orphanage.*Free
  · $money gte 300 换成了 maplebirch.get("Finance").canPay(300, "cafe")（新 API，DomRobin 只认旧的 VanillaPlus.finance）
修法（① 保意图：两边的改动都保留）：
  · DoLSims：正则把 maplebirch 外层 <<if not …>> 捕获为 $1，替换文本首行改为 $1（不吞掉 maplebirch 的开标签，否则其 <</if>> 落单）
  · DomRobin：robinpaid 两处改用「不含 >> 的前缀」匹配，只在条件开头插入 !$robinPaySelfTalked and，后续条件原样保留
  · DomRobin：Ocean Breeze 正则加上 maplebirch.get("Finance").canPay(300, "cafe") 分支（替换文件本就用 $& 保留原条件）
"""
import json
import os
import re
import sys

sys.path.insert(0, r"E:\TAML\_dol\work")
import modzip_lib as MZ

HTML = os.environ.get("DOL_HTML") or r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")
if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[AR02] index 形态异常")
    sys.exit(1)

MARK = "AR02-maplebirch-compat"
miss = []


def patch_boot(mod, edits):
    """edits: [(predicate(p)->bool, mutate(p)->None, 说明)]"""
    hit = {i: 0 for i in range(len(edits))}

    def fn(name, d):
        if name != "boot.json":
            return None
        bj = json.loads(d.decode("utf-8-sig"))
        if bj.get("_ar02") == MARK:
            return None
        for a in bj.get("addonPlugin") or []:
            if a.get("addonName") != "TweeReplacerAddon" or not isinstance(a.get("params"), list):
                continue
            for p in a["params"]:
                for i, (pred, mut, _) in enumerate(edits):
                    if pred(p):
                        mut(p)
                        hit[i] += 1
        bj["_ar02"] = MARK
        return json.dumps(bj, ensure_ascii=False, indent=2).encode("utf-8")
    return fn, hit


# ---------- DoLSims ----------
DS_OLD = '<<widget "fallenTransform">>\\s*<<if \\$angel gte 6>>'
DS_NEW = ('(<<widget "fallenTransform">>(?:<<if not \\(\\$settings\\.transformDivineEnabled[^\\n]*?>>)?)'
          '\\s*<<if \\$angel gte 6>>')


def ds_mut(p):
    p["findRegex"] = DS_NEW
    p["_comment_ar02"] = "第12轮：兼容 maplebirch 在 fallenTransform 开头加的 <<if not …>>，用 $1 保留"


ds_fn, ds_hit = patch_boot("DoLSims", [(lambda p: p.get("findRegex") == DS_OLD, ds_mut, "fallenTransform")])
already = False
cur_boot = MZ.read_mod_file(data, "DoLSims", "boot.json")
if cur_boot and MARK in cur_boot.decode("utf-8-sig"):
    already = True


def ds_all(name, d):
    if name == "game/base-combat/bookSims_4.txt":
        t = d.decode("utf-8")
        first = '<<widget "fallenTransform">>'
        if t.startswith(first):
            return ("$1" + t[len(first):]).encode("utf-8")
        return None
    return ds_fn(name, d)


# ---------- DomRobin ----------
DR_OCEAN_OLD_TAIL = "maplebirch\\.get\\([\"']VanillaPlus[\"']\\)\\.finance\\.canPay\\(300,\\s*[\"']cafe[\"']\\))\\s*>>"
DR_OCEAN_NEW_TAIL = ("maplebirch\\.get\\([\"']VanillaPlus[\"']\\)\\.finance\\.canPay\\(300,\\s*[\"']cafe[\"']\\)"
                     "|maplebirch\\.get\\([\"']Finance[\"']\\)\\.canPay\\(300,\\s*[\"']cafe[\"']\\))\\s*>>")


def dr_ocean_pred(p):
    return p.get("passage") == "Ocean Breeze" and isinstance(p.get("findRegex"), str) and p["findRegex"].endswith(DR_OCEAN_OLD_TAIL)


def dr_ocean_mut(p):
    p["findRegex"] = p["findRegex"][:-len(DR_OCEAN_OLD_TAIL)] + DR_OCEAN_NEW_TAIL


def dr_bailey_pred(p):
    return p.get("passage") == "Bailey's Office" and p.get("findString") == "<<if $robinpaid isnot 1 and $robindebtknown is 1>>"


def dr_bailey_mut(p):
    p["findString"] = "<<if $robinpaid isnot 1 and $robindebtknown is 1"
    p["replace"] = "<<if !$robinPaySelfTalked and $robinpaid isnot 1 and $robindebtknown is 1"


def dr_robin_pred(p):
    return p.get("passage") == "Widgets Robin" and p.get("findString") == "<<if $robinpaid isnot 1>>"


def dr_robin_mut(p):
    p["findString"] = '<<widget "robinpay">>\n\t<<if $robinpaid isnot 1'
    p["replace"] = '<<widget "robinpay">>\n\t<<if !$robinPaySelfTalked and $robinpaid isnot 1'


dr_fn, dr_hit = patch_boot("DomRobin", [(dr_ocean_pred, dr_ocean_mut, "Ocean Breeze"),
                                        (dr_bailey_pred, dr_bailey_mut, "Bailey's Office"),
                                        (dr_robin_pred, dr_robin_mut, "robinpay")])
cur_boot2 = MZ.read_mod_file(data, "DomRobin", "boot.json")
if already and cur_boot2 and MARK in cur_boot2.decode("utf-8-sig"):
    print("[AR02] 已存在，跳过")
    sys.exit(0)

data, ch1 = MZ.patch_mod(data, "DoLSims", ds_all)
data, ch2 = MZ.patch_mod(data, "DomRobin", dr_fn)
if ds_hit[0] != 1:
    miss.append("DoLSims fallenTransform 命中 %d" % ds_hit[0])
if "game/base-combat/bookSims_4.txt" not in ch1:
    miss.append("bookSims_4.txt 未改")
for i, nm in enumerate(["Ocean Breeze", "Bailey's Office", "robinpay"]):
    if dr_hit[i] != 1:
        miss.append("DomRobin %s 命中 %d" % (nm, dr_hit[i]))
if miss:
    for x in miss:
        print("[AR02] MISS", x)
    print("[AR02] FAIL（未写盘）")
    sys.exit(1)
open(HTML, "wb").write(data.encode("utf-8"))
print("[AR02] DoLSims %s / DomRobin %s  OK" % (ch1, ch2))
