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
