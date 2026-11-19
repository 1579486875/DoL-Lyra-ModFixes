import subprocess, sys

STEPS = [
    (r"E:\TAML\_dol\work\inject6.py", "重建 index（模组数组）"),
    (r"E:\TAML\_dol\work\U13_inject.py", "补 i18n 在 Widgets variablesStatic 漏掉的 163 条"),
    (r"E:\TAML\_dol\work\BE_bake_i18n.py", "把 i18n 烤进 index（让 TweeReplacer 看到中文，多命中 72 条补丁）"),
    (r"E:\TAML\_dol\work\AD_direct_patch.py", "直接注入：5 张映射表 / 关系值名 / 状态名 / 脸型键"),
    (r"E:\TAML\_dol\work\CB01_link_fix_direct.py", "直接注入：修复 i18n 漏掉的 10 处宏闭合"),
    (r"E:\TAML\_dol\work\CC01_return_fix.py", "按 passage 精确补闭合（Asylum Return）"),
    (r"E:\TAML\_dol\work\DB02_translate.py", "翻译 i18n 未覆盖的 Pub Avery 剧情"),
    (r"E:\TAML\_dol\work\DB03_fake_stones.py", "翻译 Fake Stones + 移除多余 */"),
    (r"E:\TAML\_dol\work\HB01_face_variant_fix.py", "修复 faceVariant 的 undefined 连锁（撤销 17 键 + 动态取键）"),
    (r"E:\TAML\_dol\work\HD01_cheats_npcs_fix.py", "修复 cheats-npcs 的 listbox undefined"),
    (r"E:\TAML\_dol\work\IB01_var_bugs.py", "修复 i18n 引入的变量 bug（compoundWraith / worn 丢 \$）"),
    (r"E:\TAML\_dol\work\IF01_settings_dollar.py", "修复 settings.watersportsEnabled 丢 \$（失禁场景失效）"),
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
    (r"E:\TAML\_dol\work\TF01_nest_guard.py", "检查并修复 widget 嵌套（必须最后）"),
]

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
