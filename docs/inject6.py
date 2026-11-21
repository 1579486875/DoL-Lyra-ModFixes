import base64, io, json, re, zipfile

SRC = r"E:\TAML\_dol\work\index.html"
OUT = r"E:\TAML\_dol\work\index_modded6.html"
DEAD_FIND = "and $cheatsEnabled is true or $debug is 1"

# 需要提前到 Cheat-Lyra 之前的 mod（避免被 Cheat-Lyra 的整段删除破坏 findString）
EARLY = [
    (r"E:\TAML\_dol\mods2\FertilityExpansion-v1.7.0-Lite.mod.zip", "FertilityExpansion 1.7.0"),
    (r"E:\TAML\_dol\mods_fixed\DoLSims_v7.mod.zip", "DoLSims 0.8.1.7 (转化+性别锚点已修)"),
    (r"E:\TAML\_dol\mods_fixed\DomRobin_v4.mod.zip", "DomRobin 0.0.8 (Bailey 锚点已修)"),
]

LATE = [
    (r"E:\TAML\_dol\mods\maplebirch-5.6.2.mod.zip", "maplebirch 5.6.2"),
    (r"E:\TAML\_dol\mods\CombatSkills_v1.14.0.zip", "CombatSkills 1.14.0"),
    (r"E:\TAML\_dol\mods\LocationsExt_v1.8.1.zip", "LocationsExt 1.8.1"),
    (r"E:\TAML\_dol\mods\CombatActionsExt_0.9.6.mod.zip", "CombatActionsExt 0.9.6"),
    (r"E:\TAML\_dol\mods_fixed\BasicNeeds_v3.mod.zip", "BasicNeeds 0.5.0 (初始食物+饥饿联动)"),
    (r"E:\TAML\_dol\mods\MapleBirchCE-2.1.12.mod.zip", "MapleBirchCE 2.1.12"),
    (r"E:\TAML\_dol\mods2\MoreLoveInterests.mod.zip", "More Love Interests 0.1.8.0"),
    (r"E:\TAML\_dol\mods2\deadwood-reblooms-v2.5.8.modpack", "Deadwood 2.5.8"),
    (r"E:\TAML\_dol\mods3\NPC.Avatars.Mod.mod.zip", "NPC Avatars 1.4.1"),
    (r"E:\TAML\_dol\mods4\WraithsReflection.mod.zip", "Wraith's Reflection 1.3.4"),
    (r"E:\TAML\_dol\mods4\pc-bakery.mod.zip", "PC Bakery 2.0.0"),
    # BabyHawk 已移除：与 deadwood-reblooms 的 5 个鹰塔 widget 重名（GreatHawk / babyhawkicon /
    # babyhawks / babyhawksthem / babyhawksyou），且两者数据源不同（$childRecords vs
    # maplebirch.get('BirdTower')）。BabyHawk 加载更晚会覆盖枯木逢春的实现，导致鹰塔模块异常。
    # 枯木逢春自带完整的鹰崽成长/狩猎/飞行系统，故保留后者。
    (r"E:\TAML\_dol\mods_fixed\HandheldIdleFix.mod.zip", "手持物品 idle 补图 1.0.0"),
    (r"E:\TAML\_dol\mods_fixed\EffectsManNullGuard.mod.zip", "effectsman 空值保护 1.0.0"),
    (r"E:\TAML\_dol\mods_fixed\ToiletFix_v4.mod.zip", "全地点如厕补丁 1.4.0"),
    (r"E:\TAML\_dol\mods5\BeautyFixer.zip", "美化修正 1.0.2（服装错位自修）"),
    (r"E:\TAML\_dol\mods_fixed\ClothesExtra_v3.zip", "扩展服装 1.0.1（去重·兼容 BES）"),
    (r"E:\TAML\_dol\mods5\clothesicon.mod.zip", "随身衣柜 0.8.3"),
    (r"E:\TAML\_dol\mods_fixed\MissingWidgetStubs.mod.zip", "缺失 widget 补桩 1.0.0"),
    (r"E:\TAML\_dol\mods_fixed\DeadLinkStubs.mod.zip", "断链场景兜底 1.0.0"),
    (r"E:\TAML\_dol\mods_fixed\GameDeadLinkStubs.mod.zip", "本体断链兜底 1.0.0"),
    # 第12轮撤下 Quoted Link Fix：① 带引号的链接目标在 vanilla 引擎里本来就能用（Wikifier.helpers.evalPassageId
#   对不存在的目标会当表达式求值，"School Boy's Toilets" → School Boy's Toilets）；② 它的 findRegex 以未转义的 [[ 开头，
#   是字符类，第7轮删掉空 regexFlag 后 all:true 生效，把 4 个 passage 里所有「x]」替换成链接，破坏了 <<if>> 代码与链接。
# (r"E:\TAML\_dol\mods_fixed\QuotedLinkFix_v2.mod.zip", "引号链接修复 1.0.0"),
    (r"E:\TAML\_dol\mods_fixed\IconPathFix.mod.zip", "图标路径修复 1.0.0"),
    (r"E:\TAML\_dol\mods_fixed\NullGuardSettings.mod.zip", "设置页求值兜底 1.0.0"),
    (r"E:\TAML\_dol\mods_fixed\PartTypeGuard.mod.zip", "部位类型空值兜底 1.3.0"),
    (r"E:\TAML\_dol\mods_fixed\FaceVariantFill.mod.zip", "脸型表情补全 1.0.0"),
    (r"E:\TAML\_dol\mods_fixed\NpcNameCN.mod.zip", "NPC 名中文化 1.2.1"),
    (r"E:\TAML\_dol\mods_fixed\StatNameCN.mod.zip", "关系值名中文化 1.0.1"),
    (r"E:\TAML\_dol\mods_fixed\CheatFaceFix.mod.zip", "作弊菜单脸型修复 1.1.0"),
]

data = open(SRC, "rb").read()
j = data.find(b"[", data.find(b"window.modDataValueZipList"))
k = data.find(b"]", j)
parts = re.findall(r'"([A-Za-z0-9+/=\s]+)"', data[j + 1:k].decode("utf-8", "replace"))

out_parts = []
inserted_early = False
for s in parts:
    raw = base64.b64decode(re.sub(r"\s+", "", s))
    is_cheat = False
    if raw[:2] == b"PK":
        z = zipfile.ZipFile(io.BytesIO(raw))
        if "boot.json" in z.namelist():
            bj = json.loads(z.read("boot.json").decode("utf-8-sig"))
            if bj.get("name") == "Cheat-Lyra":
                is_cheat = True
                for a in bj.get("addonPlugin", []):
                    if a.get("addonName") == "TweeReplacerAddon":
                        a["params"] = [p for p in a["params"] if p.get("findString") != DEAD_FIND]
                buf = io.BytesIO()
                with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
                    for info in z.infolist():
                        if info.filename == "boot.json":
                            zo.writestr(info.filename, json.dumps(bj, ensure_ascii=False, indent=2).encode("utf-8"))
                        else:
                            zo.writestr(info.filename, z.read(info.filename))
                raw = buf.getvalue()

    # 在 Cheat-Lyra 之前插入 EARLY
    if is_cheat and not inserted_early:
        for path, label in EARLY:
            out_parts.append(base64.b64encode(open(path, "rb").read()).decode("ascii"))
            print(f"  [前置] + {label}")
        inserted_early = True
    out_parts.append(base64.b64encode(raw).decode("ascii"))

assert inserted_early

print("\n追加（尾部）：")
for path, label in LATE:
    b = open(path, "rb").read()
    out_parts.append(base64.b64encode(b).decode("ascii"))
    print(f"  + {label}")

new_array = ("[" + ",".join('"' + p + '"' for p in out_parts) + "]").encode("ascii")
new = data[:j] + new_array + data[k + 1:]

# [修复] 晒痕图层路径：setup.tanImg.doggy.t 的 68 条路径全部指向 img/sex/doggyRed/，
# 该目录在 vanilla 与 modded 里都不存在（两包图片数完全一致，0 个文件）。
# 同一 passage 里的 doggy.f 用的是 img/sex/doggy/（存在，3837 个文件），
# 说明上游把「晒痕版」的目录名写错了。全库 doggyRed 只出现在此处，全局替换安全。
# 同类问题：setup.tanImg 的 t（晒痕）子表把目录名写错，指向不存在的 *Red 目录。
# 已核实：doggy/ 有 3837 个文件、missionary/ 有 2688 个；doggyRed/ 与 missionaryRed/ 均为 0。
# closeRed/ 真实存在（68 个文件），不动。
for _bad, _good in ((b"img/sex/doggyRed/", b"img/sex/doggy/"),
                     (b"img/sex/missionaryRed/", b"img/sex/missionary/"),
                     (b"img/sex/machine/vaginal/xray_vaginal.png",
                      b"img/sex/machine/vaginal/xray-vaginal.png")):
    _n = new.count(_bad)
    new = new.replace(_bad, _good)
    print(f"[修复] {_bad.decode()} {_n} 处 -> 剩余 {new.count(_bad)} 处")

open(OUT, "wb").write(new)
print(f"\n元素总数 {len(out_parts)} | index.html {len(new)/1048576:.2f} MB")
