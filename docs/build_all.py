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
    (r"E:\TAML\_dol\work\QO02_widget_cleanup.py", "兜底：修复被翻译破坏的 widget 名"),
    (r"E:\TAML\_dol\work\SF01_missing_symbols.py", "补 setup.description_CN + wTimerProgress"),
    (r"E:\TAML\_dol\work\SI01_ui_cn.py", "修 Genitals/Makeup/a light/You have/寄生虫名"),
    (r"E:\TAML\_dol\work\SL01_fix_cache.py", "去掉 NPC_CN_* 的表缓存 + a light/You have"),
    (r"E:\TAML\_dol\work\SO01_js_templates.py", "替换 JS 运行时拼接的英文模板"),
    (r"E:\TAML\_dol\work\UB01_full_bake.py", "全量补齐：不看 pos 的二次翻译（查漏补缺）"),
    (r"E:\TAML\_dol\work\TF01_nest_guard.py", "检查并修复 widget 嵌套"),
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
