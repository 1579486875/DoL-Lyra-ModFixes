import subprocess, sys

STEPS = [
    (r"E:\TAML\_dol\work\inject6.py", "重建 index（模组数组）"),
    # 第12轮：BE_bake_i18n → BE2_bake_i18n（按 ModI18N 运行时同款算法定位，修「替换第一处出现」造成的错位翻译），
    #         并移到 U13 之前（U13 改 variablesStatic 会让该 passage 的 pos 全部漂移）
    (r"E:\TAML\_dol\work\BE2_bake_i18n.py", "把 i18n 烤进 index（ModI18N 同款 ±2/窗口定位，失配只跳过该条）"),
    (r"E:\TAML\_dol\work\U13_inject.py", "补 i18n 在 Widgets variablesStatic 漏掉的 163 条（BE2 后基本已无可补）"),
    (r"E:\TAML\_dol\work\AP01_bake_js_i18n.py", "把 ModI18N 官方 JS 译文烤进 index（必须在任何改 JS 文本的脚本之前，第12轮）"),
    (r"E:\TAML\_dol\work\AD_direct_patch.py", "直接注入：5 张映射表 / 关系值名 / 状态名 / 脸型键"),
    (r"E:\TAML\_dol\work\CB01_link_fix_direct.py", "直接注入：修复 i18n 漏掉的 10 处宏闭合"),
    (r"E:\TAML\_dol\work\CC01_return_fix.py", "按 passage 精确补闭合（Asylum Return）"),
    (r"E:\TAML\_dol\work\DB02_translate.py", "翻译 i18n 未覆盖的 Pub Avery 剧情"),
    (r"E:\TAML\_dol\work\DB03_fake_stones.py", "翻译 Fake Stones + 移除多余 */"),
    (r"E:\TAML\_dol\work\HB01_face_variant_fix.py", "修复 faceVariant 的 undefined 连锁（撤销 17 键 + 动态取键）"),
    (r"E:\TAML\_dol\work\HD01_cheats_npcs_fix.py", "修复 cheats-npcs 的 listbox undefined"),
    (r"E:\TAML\_dol\work\IB01_var_bugs.py", "修复 i18n 引入的变量 bug（compoundWraith / worn 丢 $）"),
    (r"E:\TAML\_dol\work\IF01_settings_dollar.py", "修复 settings.watersportsEnabled 丢 $（失禁场景失效）"),
    (r"E:\TAML\_dol\work\JB01_translate_remaining.py", "翻译最后 37 句残留英文剧情"),
    (r"E:\TAML\_dol\work\JC01_split_sentences.py", "翻译被 HTML 标签拆开的 2 句"),
    (r"E:\TAML\_dol\work\JD01_last_one.py", "翻译最后 1 句（Temple Forgiveness）"),
    (r"E:\TAML\_dol\work\KB01_hairtype_guard.py", "给 fringetypeCN/hairtypeCN 加 undefined 兜底"),
    (r"E:\TAML\_dol\work\LB01_fix_nested_macros.py", "修复 i18n 宏嵌套爆炸 + 补 NPC_CN_* 宏与函数定义"),
    (r"E:\TAML\_dol\work\MF01_fix_either.py", "修复 i18n 破坏的 either() 反引号与字符串内嵌宏"),
    (r"E:\TAML\_dol\work\MG01_fix_fullwidth_comma.py", "修复 either()/random() 里的全角逗号"),
    (r"E:\TAML\_dol\work\MH01_last_two.py", "补齐剩余 2 处 either 反引号与 Wraith 内嵌宏"),
    (r"E:\TAML\_dol\work\MI01_backtick.py", "给 either() 裸宏参数补反引号"),
    (r"E:\TAML\_dol\work\MJ01_wraith.py", "修 Wraith 的字符串内嵌 <<= _line2>>"),
    (r"E:\TAML\_dol\work\NB01_wraith_full.py", "彻底修 _speechWraith 的两处赋值（变量拼接）"),
    (r"E:\TAML\_dol\work\NC01_wraith_b1.py", "精确修 B1 的字符串"),
    (r"E:\TAML\_dol\work\OM01_bus_fix.py", "修原版 bug: set bus 缺 to"),
    (r"E:\TAML\_dol\work\PE01_status_cn.py", "直接替换 widget 里硬编码的英文状态名"),
    (r"E:\TAML\_dol\work\PK01_headers_cn.py", "替换 settingsHeader 里的英文标题"),
    (r"E:\TAML\_dol\work\XJ01_dn_full.py", "翻 displayName（短标签，UB01 会跳过）"),
    (r"E:\TAML\_dol\work\XK01_more_dn.py", "补第二批 displayName"),
    (r"E:\TAML\_dol\work\YE02_all_dn.py", "一次性翻完剩余 103 个 displayName"),
    (r"E:\TAML\_dol\work\QO02_widget_cleanup.py", "兜底：修复被翻译破坏的 widget 名"),
    (r"E:\TAML\_dol\work\ADM01_fix_flight.py", "修 flight_text 被翻成 flesh_text"),
    (r"E:\TAML\_dol\work\ADQ01_fix6.py", "修 6 个调用但不存在的宏（printNobody 等）"),
    (r"E:\TAML\_dol\work\ADW01_fix_compound.py", "修 compoundWraith 被误改成 compound"),
    (r"E:\TAML\_dol\work\AEC01_cheatsbody_re.py", "修 cheatsBody 存中文首字（破坏 m/f/a 判断）"),
    (r"E:\TAML\_dol\work\SF01_missing_symbols.py", "补 setup.description_CN + wTimerProgress"),
    (r"E:\TAML\_dol\work\SI01_ui_cn.py", "修 Genitals/Makeup/a light/You have/寄生虫名"),
    (r"E:\TAML\_dol\work\SL01_fix_cache.py", "去掉 NPC_CN_* 的表缓存 + a light/You have"),
    (r"E:\TAML\_dol\work\SO01_js_templates.py", "替换 JS 运行时拼接的英文模板"),
    (r"E:\TAML\_dol\work\UB01_full_bake.py", "全量补齐：不看 pos 的二次翻译（查漏补缺）"),
    (r"E:\TAML\_dol\work\VF03_cjk_guard.py", "中文标识符守卫（属性名/数组比较）"),
    (r"E:\TAML\_dol\work\VL01_more_symbols.py", "补 7 个 i18n 引用但缺失的 setup 函数"),
    (r"E:\TAML\_dol\work\VP02_fix_penisdesc.py", "penisdesc 英文子串判断改中英兼容"),
    (r"E:\TAML\_dol\work\VS02_fix_text_includes.py", "文本字段英文 includes 改中英兼容"),
    (r"E:\TAML\_dol\work\XC01_collapse.py", "折叠多层宏嵌套（每次烤入都会多包一层）"),
    (r"E:\TAML\_dol\work\ZE01_fix_css_cn.py", "修 CSS 类名/变量名被翻译破坏"),
    (r"E:\TAML\_dol\work\ZO01_cn_macro_fix.py", "修中文宏名（<<保持了安静>> -> <<silently>>）"),
    (r"E:\TAML\_dol\work\AAD01_fix_setup_guard.py", "修 setup 守卫（SugarCube.setup 不存在）"),
    (r"E:\TAML\_dol\work\AAE01_fix_selfassign.py", "删掉 var st = st 自赋值"),
    (r"E:\TAML\_dol\work\AAH01_fix_all.py", "折叠 <<= 嵌套 + 修全角括号 + 英文单词"),
    (r"E:\TAML\_dol\work\ABC01_three_fixes.py", "战斗菜单键/Next time 台词/描述词扩充"),
    (r"E:\TAML\_dol\work\ZJ02_fix_babyrent.py", "补 babyRentDisplay 丢失的颜色参数"),
    (r"E:\TAML\_dol\work\ABB01_fix_wraith.py", "删除重复 wTimerProgress + JS 英文"),
    (r"E:\TAML\_dol\work\AAP01_final_table.py", "最终修复 NPCTypeList 粘连+补复数"),
    (r"E:\TAML\_dol\work\ADI01_safe_passage.py", "新建 Widgets Repair passage 承载注册失败的 widget"),
    (r"E:\TAML\_dol\work\ACE01_wrap_v3.py", "getter/setter 锁定 NPC_CN_*（防模组覆盖）"),
    (r"E:\TAML\_dol\work\ACG01_fix_getter.py", "修 getter 缓存（防栈溢出）"),
    (r"E:\\TAML\\_dol\\work\\R24_inject_tr.py", "翻译 19 条漏翻（Asylum/Wolf Cave/Brothel 等）"),
    (r"E:\TAML\_dol\work\R42_fix_npc_names.py", "修 NPC 名被翻译导致 case 永不命中"),
    (r"E:\TAML\_dol\work\R43_fix_npc2.py", "修组合 case + C.npc 中文索引 + nnpc 参数"),
    (r"E:\TAML\_dol\work\R46_fix_yourself.py", "修 === 你自己 -> Yourself"),
    (r"E:\TAML\_dol\work\D01_fix_all_escaped.py", "统一修复（转义形态：运算符/Tendrils/element152/最后28/EXTRA/模组NPC）"),
    (r"E:\TAML\_dol\work\E17_fix_npctypelist.py", "补 NPCTypeList_cn_name（75种兽人+体格词+复数）"),
    (r"E:\TAML\_dol\work\E02_fix_identifiers.py", "修复标识符被翻译成中文（_lower./C.npc.Robin./全角标点）"),    (r"E:\TAML\_dol\work\F12_cn_en_fix.py", "中文文本英文残留（回车/Wink/play/the）"),    (r"E:\TAML\_dol\work\F17_fix_template.py", "模板字符串变量名+中文粘连"),


    (r"E:\TAML\_dol\work\ZZ01_final_guard.py", "最终守卫：所有已知 bug 的幂等兜底（防顺序错）"),    (r"E:\TAML\_dol\work\F36_merge_table.py", "合并重复的 NPCTypeList_cn_name"),    (r"E:\TAML\_dol\work\F43_fix_extra.py", "补全 makeFn 的 EXTRA 表"),    (r"E:\TAML\_dol\work\F48_inline_part.py", "BODYPARTS_CN_NAME 内联部位表"),



    (r"E:\TAML\_dol\work\O05_fix_combatperson.py", "修 combatperson 的英文 description"),    (r"E:\TAML\_dol\work\P09_translate_templates.py", "翻译 Template.add 里的英文（chatter/sin/gwylanItem 等 46 条）"),

    (r"E:\TAML\_dol\work\N08_fix_two.py", "修 The person masturbates + description_CN 赋英文 title"),
    (r"E:\TAML\_dol\work\K17_remove_regexflag.py", "删 TweeReplacer 补丁的空 regexFlag（修 DoLSims fallenTransform）"),
    (r"E:\TAML\_dol\work\J06_fix_two.py", "修战斗英文残留 + You _You 重复"),
    (r"E:\TAML\_dol\work\I06_fix_mk_tables.py", "补全 5 个 mk() 翻译函数的表缺口"),
    (r"E:\TAML\_dol\work\H06_fix_mod.py", "补全 Npc Name CN 模组的 BODYPARTS 表（30->76 键）"),
    (r"E:\TAML\_dol\work\Q03_fix_two.py", "修 Lewd 颤抖 ripple + 跪在你身边 you"),    (r"E:\TAML\_dol\work\Q07_fix_relation_box.py", "修 relation-box 里 NPC_CN_NAME 宏嵌套（社交界面崩溃根因）"),

    (r"E:\TAML\_dol\work\R10_fix_clothing_slot.py", "补全 mod 服装缺失的 slot（clothingShopv2 侧）"),
    (r"E:\TAML\_dol\work\R17_fix_slot_fallback.py", "generateshoppage 的 slot 兜底（Forest Shop 崩溃）"),
    (r"E:\TAML\_dol\work\T10_fix_templates.py", "Template.add 英文清理 + 恢复被翻的模板名"),
    (r"E:\TAML\_dol\work\T16_fix_links.py", "翻译 link 的英文按钮文本（29 条）"),
    (r"E:\TAML\_dol\work\T25_fix_foodlist.py", "合并 CafeFoodList 丢词 + 三重尖括号"),
    (r"E:\TAML\_dol\work\U12_fix_bare_en.py", "清除裸英文副词（<<if>> 分支里的英文，72 处）"),
    (r"E:\TAML\_dol\work\V11_fix_npcexpose.py", "修 npcexposetext 中英混杂"),
    (r"E:\TAML\_dol\work\W06_fix_tooltip.py", "修 tooltip 英文 + 正文代码泄漏"),
    (r"E:\TAML\_dol\work\X05_fix_leaks.py", "_args 泄漏 + 双重转义"),
    (r"E:\TAML\_dol\work\Y05_fix_regexflag.py", "删所有模组的空 regexFlag（Quoted Link Fix 8 处）"),
    (r"E:\TAML\_dol\work\Z05_fix_strapon.py", "翻译假阳具尺寸选项"),
    (r"E:\TAML\_dol\work\AB13_fix_js_text.py", "翻译玩家可见的 JS 硬编码英文（30 条）"),
    (r"E:\TAML\_dol\work\AC06_translate_feats.py", "翻译 256 个成就名"),
    (r"E:\TAML\_dol\work\AD10_fix_compile.py", "修复引擎 parse 后无法编译的宏表达式（第12轮）"),
    (r"E:\TAML\_dol\work\AF01_fix_wraith_conch.py", "修 Wraith'sReflection 银海螺对话的跨行字符串（第12轮）"),
    (r"E:\TAML\_dol\work\AI01_fix_cn_logic.py", "修汉化值兼作逻辑值的判断（社区 issue #579/#583 + 同类，第12轮）"),
    (r"E:\TAML\_dol\work\AR02_maplebirch_compat.py", "DoLSims/DomRobin 4 条补丁兼容 maplebirch 5.6.2 抢先改写（第12轮）"),
    (r"E:\TAML\_dol\work\AK09_restore_entities.py", "恢复被 X05 一起解掉的 vanilla 合法实体 &lt;/&gt;（服装店分页崩，第12轮）"),
    (r"E:\TAML\_dol\work\AU09_translate_residue.py", "补译运行时仍为英文且官方无条目的 2 处玩家可见文本（第13轮）"),
    (r"E:\TAML\_dol\work\AW02_merge_dup_tables.py", "合并被临时表覆盖的官方 NPCNameList/NPCTitleList（第13轮）"),
    (r"E:\TAML\_dol\work\AW03_npcnamecn_official.py", "Npc Name CN 1.4.0：官方映射表优先（鱼名/角色名与正文一致，第13轮）"),
    (r"E:\TAML\_dol\work\AY03_mod_notes.py", "给修补过的第三方模组写修补说明（模组描述同步，第14轮）"),
    (r"E:\TAML\_dol\work\BA01_add_shopdetails.py", "补全 shopDetails 缺失的5个特质定义（Forest Shop筛选器崩溃，第14轮）"),
    (r"E:\TAML\_dol\work\BA02_loadfilter_guard.py", "loadFiltersMenu widget 加防护（未注册特质不崩溃，第14轮）"),
    (r"E:\TAML\_dol\work\TF01_nest_guard.py", "检查并修复 widget 嵌套（必须最后）"),
    # 注：R10/R17 原本在 TF01 之后又重复登记了一次（幂等跳过、无实际作用），
    #     违反「TF01 永远最后」—— 第12轮移除，二者已在上方 TF01 之前执行。
]

import os
_FROM = os.environ.get("BUILD_FROM")   # 调试用：从某个脚本（文件名包含该串）开始续跑；正式构建不要设置
if _FROM:
    _i = next((k for k, (p, _) in enumerate(STEPS) if _FROM in p), None)
    if _i is None:
        print("BUILD_FROM 找不到:", _FROM)
        sys.exit(1)
    print(f"⚠ 续跑模式：从第 {_i + 1} 步 {STEPS[_i][0]} 开始")
    STEPS = STEPS[_i:]

for path, desc in STEPS:
    print(f"\n=== {desc} ===")
    r = subprocess.run([sys.executable, path], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    for line in (r.stdout or "").strip().split("\n")[-8:]:
        print("  " + line)
    if r.returncode != 0:
        print("  ❌ 失败:", (r.stderr or "")[:400])
        sys.exit(1)
print("\n✅ 全部完成")
