# DoL-Lyra-ModFixes

Degrees of Lewdity（Lyra 0.5.12.13 CHS，53 个模组）整合包的**静态审查与修复集**。

审查按 RimWorld《全面审查与修复-通用模板》的 L3 力度执行：四维度（完整性 / 兼容性 / 性能 / 必要性）+ §0.2 保意图分级。
所有修复都遵循一条硬规矩：**不靠拿掉作者功能来换日志安静**。

## 基线

| 项 | 值 |
|---|---|
| 游戏 | DoL 0.5.12.13 + ModI18N 1.0.1a |
| ModLoader | 2.101.1 |
| maplebirch 框架 | 5.6.2 |
| 模组数 | 62（其中 21 个为本次新建补丁模组） |
| APK | 182,384,074 字节（173.94 MB），SHA256 `7C85AFA1889860DBA2FAB42BEA3F0268E49EDFDF35300240DB298FDC294A6065`，已重签名（keystore `dol.jks`，alias `dol`） |

## 修复清单（30 项）

### 崩溃类

| # | 问题 | 修法 |
|---|---|---|
| 1 | 返回键必弹 `TypeError: Cannot read properties of undefined (reading 'isOpen')` | `custom_cordova_additions.js` 第 16 行 `SugarCube.Dialog` → 全局 `Dialog`。**Lyra 底包 bug，vanilla 同样存在** |
| 2 | `effectsman` 里 14 处 `$NPCList[...]` 空值读取导致战斗红屏 | `EffectsMan Null Guard 1.0.0`，加空值前置判断 |
| 3 | `Alice_0.txt` 悬空 `<<if>>` 导致角色创建页崩（`cannot find a closing tag`） | 移除 Alice_0 / Alice_1 两条补丁（后者锚点基于旧版，永远失配） |
| 4 | `characterSettings` 的 `<<=>>` 抛 `Cannot convert undefined or null to object` | `Settings Null Guard 1.0.0`，给 `Object.entries/keys/values` 加兜底 |
| 5 | 汉化包 7 处 `<<link>>` 漏 `<</link>>` 或被写成 HTML `</link>` | `I18n Macro Fix 1.2.0`，10 条精确替换 |
| 6 | `Police Cell` 译文丢了 `<<if>>` 的闭合 | 同上 |

### 断链类

| # | 问题 | 修法 |
|---|---|---|
| 7 | DoLSims 11 个 + DomRobin 2 个 passage 被引用但不存在 | `Dead Link Stubs 1.0.0`，补 13 个带返回的兜底页 |
| 8 | 游戏本体 7 个 passage 缺失（庄园入口/森林被抓/擦窗/监狱图书室/礼拜堂/模特） | `Game Dead Link Stubs 1.0.0`。**vanilla 包同样缺失** |
| 9 | 3 个 widget 从未定义（`fishingrod_held_icon` / `fishing_cast_time` / `gCompStage`） | `Missing Widget Stubs 1.0.0` |
| 10 | 8 处链接目标连引号一起写进 passage 名（`[[Next\|"School Boy's Toilets"]]`） | `Quoted Link Fix 2.0.0`，findRegex 兼容 `Next`/`继续` |
| 11 | `Robin Hug Cry` 锚点基于旧版（`gte 2` vs 原文 `gte 5`） | 适配为 `gte 5`，findString 与 replaceFile 同步 |

### 图片类

| # | 问题 | 修法 |
|---|---|---|
| 12 | `setup.tanImg` 晒痕路径 `doggyRed/` 68 处、`missionaryRed/` 57 处，目录从未创建 | 改为 `doggy/`、`missionary/` |
| 13 | `xray_vaginal.png` 下划线笔误 | → `xray-vaginal.png` |
| 14 | `foxy`/`gloomy`/`makeup` 三个脸型 `iris.png` 不透明像素仅 118/232（正常 16342） | 用 `default/iris.png` 覆盖。**这就是「眼睛空白」的根因** |
| 15 | 手持物品缺 idle 图层 104 张 | `Handheld Idle Fix 1.0.0` |
| 16 | 衣服图标 6 条（`skulduggery_mask` 笔误 + 5 条素材缺失） | ClothesExtra v3 修补 |
| 17 | 金币成就图标 `coin-platinum-fake.gif` / `coin-jeweled-fake.gif` 缺失 | 用 `coin-gold-fake.gif` 补齐 |
| 18 | `registerImagePattern("wolfharmony")` 指向不存在的 `wolfharmony.png` | → `sym-harmony.png` |
| 19 | 3 处 `<<icon>>` 路径错（`avery-study_hallway` / `bronze-key` / `stream`） | `Icon Path Fix 1.0.0` |

### 逻辑类

| # | 问题 | 修法 |
|---|---|---|
| 20 | BasicNeeds 新档饥饿直接顶满（`digest` 为空，`digestHunger()` 算得 MAX） | 初始化给 3000/3500 初始食物 |
| 21 | 全游戏进食点不接 BasicNeeds（它只接管 5 个地点） | 监听原版 `$hunger` 下降，按量分档折算：<250 ×2 / 250–449 ×4 / ≥450 ×5 |
| 22 | 旅店/公寓/枯木逢春房产浴室无如厕 | `Toilet Addon 1.4.0`，4 个 passage |
| 23 | 大便不清小便 | 同一条链接里补 bladder 归零 |

### 冲突类

| # | 问题 | 修法 |
|---|---|---|
| 24 | BabyHawk × 枯木逢春 5 个 widget 同名覆盖（数据源不同：`$childRecords` vs `maplebirch.get('BirdTower')`） | 移除 BabyHawk（枯木逢春自带完整鹰塔） |
| 25 | ClothesExtra `Cargopants` 重复定义（identical except index） | 删重复条 |
| 26 | DoLSims `additionFile` 重复 131 条（320→189） | 去重 |
| 27 | 汉化包译文里的 8 处宏闭合错误（7× `<<link>>` + `Police Cell` 的 `<<if>>`） | `I18n Macro Fix 1.2.0` |

## 目录

```
mods/          本次自建的 12 个补丁模组（可直接放进 ModLoader）
docs/          逐轮审查报告
```

## 已知不可修（附理由）

| 项 | 理由 |
|---|---|
| `img/sex/missionary/active/` 48 张 | BESC 从没画过 missionary 的主动方视角，vanilla 包里也是 0 文件。需要重画，不是改路径的问题 |
| 游戏本体 4 条 TweeReplacer 失配 | 锚点唯一、汉化后仍存在、静态能命中，真机就是失配。运行时字符串差异 |
| 169 条游戏源码废弃图片引用 | 多数在 `<!-- -->` 注释里，不执行 |
| `index.html` 105 MB | 53 个模组塞进单文件的架构限制 |
| `CombatStatusDisplay-Lyra` tweeFileList 冗余 2 项 | 它是 Lyra 底包第 25 个模组，改它要动 base64，收益太低 |

## 检查覆盖（34 轮）

完整性（文件清单/图片引用/addon 引用/passage-widget 重名）、兼容性（锚点/依赖/CSS/变量/i18n）、语法（JS `node --check`/twee 宏配对/passage 链接/include-goto）、资源（PNG 头/GIF 解码/图标/核心渲染资源）、性能（index 体积/冗余清单）、必要性（模组描述一致性）。

关键经验：**任何针对游戏文本的补丁都必须考虑 i18n 翻译**，否则会在汉化环境里静默失配；**改 findString 时必须确认 replaceFile 里未闭合的 `<<if>>` 是否依赖原文后续的 `<</if>>`**，一旦配对补丁失配就会造出悬空标签。

## 许可

补丁模组为本仓库原创，可自由使用。原游戏与各模组著作权归其作者。

## 第六轮（U01–U41，27 轮）：i18n 深度审查

这一轮专攻上一轮 odyShapescn 事件暴露的系统性问题。

### 关键结论：ModI18N 的匹配策略

	ryReplaceStringFuzzyWithHintIndex() 的实际逻辑（读自 dist/i18nLoad.js）：

1. 先试 pos、pos±1、pos±2
2. 失败后在 **[pos-10, pos+len+30] 窗口内**用正则兜底
3. **窗口外直接 console.error 并跳过**

### 全量测量结果

| 项 | 值 |
|---|---|
| i18n 条目总数 | 190,234 |
| 有  的条目 | 190,201 |
| pos 精确命中 | 158,912（83.55%） |
| pos 偏移但窗口内能兜底 | 31,121（16.36%） |
| **会被跳过** | **168（0.088%）** |

### 168 条失败的分布与处置

**全部集中在 Widgets variablesStatic，偏移统一为 -375 字符**。

| 类型 | 数量 | 处置 |
|---|---|---|
| 追加 cn_name（物品中文名） | 16 | ✅ 已注入 |
| 展示文本数组 | 2 | ✅ 已注入 |
| message/description 等展示性键 | 145 | ✅ 已注入 |
| setup.breastsizes / setup.penisSizes | 2 | ⛔ **故意不注入** |
| setup.bodyShapes（加 bodyShapescn） | 1 | ✅ 由 BodyShapes CN Fix 补 |
| 纯符号 ]>>（不唯一） | 2 | ⛔ 跳过 |

**为什么那 2 条必须保持英文**：setup.breastsizes 是**尺寸等级名数组**，游戏代码用 "small" / "large" 这些值做比较与索引。译成中文会让所有尺寸判断失效。它们**恰好因为 pos 偏移而没被应用**，保持英文 = 逻辑正确。

### 实际注入

U13_inject.py 在 inject6.py 之后对 Widgets variablesStatic 做 163 条精确替换（ 在 passage 内唯一才动手），**0 未命中**。

构建顺序固定为：

`
inject6.py  →  U13_inject.py  →  rebuild2.py
`

uild_all.py 封装了前两步。

### 其他维度结论

| 维度 | 结果 |
|---|---|
| CSS 类名覆盖 | 多模组覆盖本体类名，但**全部用 ID 限定作用域**（#bn-body-panel .settingsHeader 等），无全局污染 |
| 加载顺序 | dependenceInfo 全部满足；loadBefore/loadAfter 全部满足 |
| 分辨率适配 | viewport 标准；67 个 @media；width:2000px 是 .debugPassages 调试样式 |
| 字体 | 全部 data: 内嵌；/fonts/Roschild.ttf 外部引用被后面的内嵌版覆盖 |
| 存档兼容 | $SchoolOrder 等对象变量都有 <<if .y is undefined>><<set ...>><</if>> 子键兜底 |
| 全局污染 | 252 个 window.*，仅 1 处「冲突」（MapleBirchCE 只是**代理读取** window.EdenCheats，非覆盖） |
| 资源体积 | 解压 232.7 MB；index.html 100.58 MB 是架构限制；重复图片极少 |
| HTML 结构 | 	w-passagedata 16088/16088 配对；重复 passage 0；boot.json 非法 0 |
| 路径大小写 | 508 条静态引用，**0 条大小写不符** |
## 第七轮（V01–V11）：脸型表情完整补全

上一轮只把 default/iris.png 复制到 foxy/gloomy/makeup，治标不治本。全量对比后发现缺的不止眼睛：

| 变体 | 缺文件数 | 缺失内容 |
|---|---|---|
| oxy | 16 | makeup/eyeshadows*.png（2）+ ed/*（14，晒痕整套） |
| gloomy | 23 | irisempty-left/right.png + makeup/* + ed/* |
| makeup | 29 | 同上，另加若干 |

ed/ 是**晒痕（tan）覆盖层**，makeup/ 是**眼影层**。两者整目录缺失意味着选这三套脸型时，**晒痕和眼影永远不显示**，而不是简单的一张图空白。

### 修法

Face Variant Fill 1.0.2：用 default 的对应图层补齐 **68 张**（foxy 16 / gloomy 23 / makeup 29），走 imgFileList。

### 踩到的坑：imgFileList 的路径必须与 zip 内路径**完全一致**

第一版写成：

`
zip 内:          face/default/foxy/makeup/eyeshadows.png
imgFileList:     img/face/default/foxy/makeup/eyeshadows.png      ← 多了 img/
`

对照已经在用的 Clothes 模组才确认：它的 zip 内路径就是 img/clothes/belly/belly_mask.png，**与 imgFileList 逐字相同**。改成一致后自检「imgFileList 在 zip 内的缺失 = 0」。

### 为什么不动 modded1～15

那 15 套是模组添加的（modded1 有 77 个文件，modded2-9 各 69 个，modded10-15 各 43 个）。它们是作者按需精简的，补齐等于替别人改设计。用户提到的「仪态」指游戏自带的 6 种，所以只补 foxy/gloomy/makeup。
## 第八轮（W01–W10）：犯罪名中文化

作弊菜单 / 统计页的犯罪项显示英文（Assault、Coercion、Trespassing…）。

### 根因

游戏在 Widgets variablesStatic 里定义：

`
<<set setup.crimeNames to {
	assault: "assault",
	coercion: "coercion",
	destruction: "destruction of property",
	...
}>>
`

作弊菜单直接输出它的**值**：

`
<<numberStepper toTitleCase(setup.crimeNames[_cr]) [_cr].current ...>>
`

而 i18n 对这块**一条都没翻**（Coercion / Trespassing / Thievery 等在 190,234 条里查无对应条目）。

### 修法

Crime Name CN 1.0.0：**只改值、不动键**。

键（ssault / coercion …）是 $crime[_cr] 的索引，也被 $crime[_cr].current/history/daily/count 使用 —— 改键会让**老存档的犯罪记录全部失效**。值只用于 	oTitleCase(...) 显示，改它零风险。

| 键 | 原值 | 新值 |
|---|---|---|
| assault | assault | 袭击 |
| coercion | coercion | 胁迫 |
| destruction | destruction of property | 破坏财产 |
| exposure | indecent exposure | 不当暴露 |
| obstruction | obstruction of justice | 妨碍司法 |
| prostitution | prostitution | 卖淫 |
| resisting | resisting arrest | 拒捕 |
| thievery | thievery | 盗窃 |
| petty | petty thievery | 轻微盗窃 |
| trespassing | trespassing | 非法闯入 |

顺带补了 setup.crimeDescs（犯罪事件描述）7 条：general / escaping prison / a high-profile theft involving a noble's wedding cake 等，其中包括 debug: "wearing clothes of mixed fabrics, you sick fuck" 这条作者的玩笑条目。
## 第九轮（X01–X26）：NPC 名中文化 —— 挖出汉化包引用了 5 个不存在的符号

社交面板里显示 Bailey 监护人，其中 监护人 是中文、Bailey 是英文。

### 排查路径

1. Bailey 不是静态文本 —— 它来自 V.NPCName[i].nam（**游戏数据**），i18n 只处理静态文本。
2. 但 i18n 确实动过这里。查 i18n.json 发现 4 条：

`
f = '_npcData.nam'
t = '<<NPC_CN_NAME _npcData.nam>>'
`

3. 于是去搜 NPC_CN_NAME 的定义 —— **游戏本体 + 全部 56 个模组里，一处都没有。**

### 汉化包一共引用了 5 个不存在的东西

| 引用 | 出现次数 | 形式 | 后果 |
|---|---|---|---|
| <<NPC_CN_NAME>> | 194 | 宏 | 报「未定义宏」，整段内容不渲染 |
| <<NPC_CN_TYPE>> | 58 | 宏 | 同上 |
| <<BODYPARTS_CN_NAME>> | 7 | 宏 | 同上 |
| setup.NPC_CN_TYPE() | — | 函数 | is not a function |
| setup.NPC_CN_TITLE() | — | 函数 | 同上 |

典型受害者：

`
pN=Eden Hunt Snake Finish
t='<<tearful>>你从<<print setup.NPC_CN_TYPE()>>的嘴里爬了出来。'

pN=Gwylan Ritual Bait Cleanse Plant
t='...<<His>>的<<BODYPARTS_CN_NAME .taintedArm>>又细...'
`

### 修法

Npc Name CN 1.1.0：把这 5 个全部补齐。

- **宏**：用 SugarCube.macros.add 注册 NPC_CN_NAME / NPC_CN_TYPE / NPC_CN_TITLE / BODYPARTS_CN_NAME
- **函数**：挂到 SugarCube.setup 上
- **映射表**：32 个 NPC 名、40 个头衔/兽类、30 个身体部位

**关键设计：只做显示层映射，不倒灌游戏数据。** 因此 <<case Bailey>> 这类靠 "Bailey" 字面量匹配的逻辑分支**完全不受影响** —— 这也是为什么不能直接把 V.NPCName[i].nam 改成中文（那会让所有 switch 分支失效）。

注册用轮询 + :storyready 双保险，因为 SugarCube.setup 和 macros 在脚本加载时还没就绪。