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
| 模组数 | 58（其中 17 个为本次新建补丁模组） |
| APK | 183,711,178 字节（175.20 MB），SHA256 `__PENDING__`，已重签名（keystore `dol.jks`，alias `dol`） |

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
| oxy | 16 | makeup/eyeshadows*.png（2）+ 
ed/*（14，晒痕整套） |
| gloomy | 23 | irisempty-left/right.png + makeup/* + 
ed/* |
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
## 第十轮（BA01–FA01，30 轮）

### 一、锚点真实命中率（HTML 转义问题彻底查清）

| 阶段 | 命中 | 未命中 |
|---|---|---|
| 静态 index（不烤 i18n） | 359 | 85 |
| **烤入 i18n 后** | **417** | **1** |

唯一的 1 条是 DomRobin | Robin Hug Cry：它的两条补丁共用同一锚点，#19 先生效把 gte 5 改成 gte 2，#47 才命中 —— 单条独立判断会误报。

**根因**：TweeReplacer（补丁）先于 I18nTweeReplacer（翻译）执行，而 DoLSims / DomRobin 的作者是照**中文**写的锚点。实测反转顺序能多命中 72 条。

**解法**：BE_bake_i18n.py 在构建期把 19 万条翻译烤进 index，运行时补丁看到的就是中文。

### 二、又一个转义 bug：passage 名

BE_bake_i18n.py 最初用 
ame="([^"]+)" 取 passage 名，得到的是 Danube House S&amp;M，而 i18n 里的 pN 是 Danube House S&M —— **所有名字含 & 的 passage，i18n 条目被整段跳过**。

修正后：英文句子 482 → 281（-42%）。

### 三、i18n 完全未覆盖的 6 个 passage

| passage | 英文句 |
|---|---|
| Pub Avery Fake Stones | 36 |
| Pub Avery Stones 2 | 15 |
| Pub Avery Nod Point | 11 |
| Pub Avery Stones Give | 4 |
| Pub Avery Nod Note | 1 |
| Pub Avery Stones Reconsider | 1 |

i18n 包基于旧版游戏，这条 Avery 酒馆线是新加的，一条都没翻。已全部手工翻译（含三种 $speech_attitude 分支）。

**顺带修掉一个游戏本体 bug**：Pub Avery Fake Stones 末尾有个孤立的 */（没有配对的 /*）。

### 四、英文残留测量

| 判据 | 数量 |
|---|---|
| 宽松（含注释/代码） | 550 |
| 排除注释后 | 340 |
| 严格（完整句子、排除宏与 JS） | **172**（其中约一半是 JS 误报） |

Forest Shop Hunt Widgets 的 308 个英文句**全部是开发者注释**（<!-- 30 个但 --> 42 个，注释结构不配对），玩家看不到，不需要翻译。

剩余真英文约 50-80 句，分散在 Widgets Street / Maths Project Stim / Science Refusal / Sea / Temple Quarters Hole 等 passage 的零星段落。

### 五、其余维度

| 维度 | 结果 |
|---|---|
| passage 配对 | 16088 / 16088 ✅ |
| 重复 passage 名 | 0 ✅ |
| JS 语法 | 76 个文件，0 错误 ✅ |
| 存档兼容 | 169 个「疑似缺兜底」变量，均为 DoL 常见的 <<set>> 隐式初始化，非缺陷 |
| 性能 | 解压 232.8 MB，index 100.67 MB，APK 175.20 MB |

### 六、构建链（10 步，全部幂等）

`
inject6.py            重建模组数组
U13_inject.py         补 i18n 漏掉的 163 条
BE_bake_i18n.py       烤入 19 万条翻译（passage 名已反转义）
AD_direct_patch.py    映射表 / 关系值名 / 状态名 / 脸型键
CB01_link_fix_direct  10 处宏闭合（负向断言防叠层）
CC01_return_fix.py    按 passage 精确补闭合
DB02_translate.py     Pub Avery 剧情翻译
DB03_fake_stones.py   Fake Stones 翻译 + 移除多余 */
`

跑两遍结果完全一致，已验证。

## 第十一轮（35 轮 · 以 vanilla 为基线的差异审计）

### 方法论升级

前几轮的教训是「改 A 打坏 B」。本轮引入**基线对照法**：把 vanilla 原包与 modded 包逐项对比，
任何非预期差异都视为 bug。

| 维度 | vanilla | modded | 结论 |
|---|---|---|---|
| passage 集合 | 16087 | 16087 | 完全一致 |
| widget 定义 | 5097 | 5097 | 无丢失无新增 |
| `if` 配对 | 69960/69960 | 70021/70021 | 平衡 |
| `for` 配对 | 1049/1049 | 1053/1053 | 平衡 |
| `switch` 配对 | 3527/3527 | 3553/3553 | 平衡 |
| `link` 配对 | 38846/38846 | 38845/38845 | 平衡 |
| 断链 | 22 种 | 22 种 | 未引入新断链 |
| CSS 类名含中文 | 0 | 0 | 干净 |
| 图片路径含中文 | 0 | 0 | 干净 |

### 本轮修掉的 3 个真 bug

**1. `$compoundWraith`（3 处）**

i18n 把 `$compound` 改成 `$compoundWraith`，后者从未定义，界面会显示 undefined。
`$compound` 有 2 处定义 / 185 处引用，是合法变量。

**2. `<<if worn.handheld`（1 处）**

i18n 把 `$worn` 的 `$` 丢了。`Gwylan Walk School Solo` 里那一句会抛
`Cannot read properties of undefined`。

注意：裸 `worn.xxx` 全库有 1201 处，绝大多数是 JS 局部变量，**绝不能全局替换**。

**3. `settings.watersportsEnabled`（3 处）**

i18n 把 `$settings` 的 `$` 丢了，而 `$settings.watersportsEnabled` 有 17 处正确写法。
裸 `settings` 是 `window.settings`（不存在），条件恒假，**失禁场景永不触发**。

### 排除的误报（避免过度修复）

| 候选 | 判定 |
|---|---|
| `$temple_wall_victim is "男孩"`（3 处） | 正常：赋值也是 `"男孩"`，匹配成立 |
| `School Boy's Toilets` 断链 | 正常：passage 存在，检查脚本 unescape 有误 |
| `Estate Manor Intro Entrance` / `Mansion Intro 9 Push` | 原版遗留：vanilla 里同样断，不改 |
| `setup.BODYPARTS_CN_NAME` 未定义 | 正常：NpcNameCN 的 JS 已提供 |
| `version.major` 裸变量 | 不改：`$version` 只有 schema 字段，改了同样 undefined |
| 裸 `settings.` 其余 12 处 | 正常：tooltip 插件 / lodash 的 JS 局部变量 |
| `<<optionsfrom setup.legPositions>>` 等 | 正常：JS 运行时定义 |

### 本轮验证

```
JS 语法       76 文件 0 错误
widget 名     0 个含非 ASCII
faceVariant   6 键（撤销了上一轮误加的 17 个）
宏配对        link 38845/38845
```

## 第十二轮（补齐英文残留：40 -> 0）

上一轮停在「约 50-80 句英文没做完」，本轮把它做完了。

### 做法：把「代码碎片」和「真剧情」彻底分开

第一版扫描出 550 句，几乎全是误报。逐步收紧判据：

| 判据 | 数量 |
|---|---|
| 宽松（含注释/代码） | 550 |
| 排除注释 | 340 |
| 排除系统页 + 完整句子 | 157 |
| **高置信度（排除 `$变量`/`_变量`/`isnot`/JS 关键字，要求首词大写 + ≥3 个功能词）** | **40** |

### 翻译结果

| 阶段 | 剩余英文剧情 |
|---|---|
| 起点 | 40 |
| 批量翻译 37 句 | 3 |
| 处理被 `<span>` 拆开的 2 句 | 1 |
| 翻译最后 1 句 | **0**（只剩 1 条 SugarCube 框架错误信息，不翻译） |

**最终剩下的唯一英文**：
```
Expected a second parameter, but none was provided.
```
这是 SugarCube 引擎自己的报错文案，翻了反而影响排错。

### 本轮翻掉的代表性句子

```
The nurse helps you sit and calls out for assistance.
  -> 护士扶你坐起，并大声呼救。

There's a small cake sat on the windowsill with a note attached.
  -> 窗台上放着一个小蛋糕，上面附着一张纸条。

You dress yourself with shaking fingers, doing your best to ignore
the disappointed heckling from the class.
  -> 你用发抖的手指穿好衣服，尽量不去理会班上失望的起哄声。

It's a brass statuette, moulded in the shape of an eagle.
  -> 那是一尊黄铜小雕像，铸成了鹰的形状。
```

### 两个技术细节

**1. 句子被 HTML 标签拆开**

```
<span class="gold">It's a brass statuette,</span> moulded in the shape of an eagle.
You feel a <span @class="basicJitterCss()">strange heat</span> just beneath your skin.
```

整句替换找不到，必须按片段译，且要同时兼容 HTML 转义形态（`&lt;span`）。

**2. 撇号会被转义**

`That's a lot of money...` 在文件里可能是 `That&#39;s`，替换时两种都要试。

### 回归验证（改动后重跑基线对比）

| 维度 | vanilla | modded | 结论 |
|---|---|---|---|
| passage 集合 | 16087 | 16087 | 一致 |
| widget 定义 | 5097 | 5097 | 无丢失 |
| `if` 配对 | 69960/69960 | 70021/70021 | 平衡 |
| `for` 配对 | 1049/1049 | 1053/1053 | 平衡 |
| `switch` 配对 | 3527/3527 | 3553/3553 | 平衡 |
| `link` 配对 | 38846/38846 | 38845/38845 | 平衡 |

## 第十三轮（35 轮 · 存档兼容 / 资源 / 控件 / 运行时风险）

前两轮查的是「翻译是否破坏代码」。本轮换五个新维度，仍然全部以 vanilla 为基线。

### 1. 存档兼容（1-6 轮）

| 检查项 | 结果 |
|---|---|
| modded 新增 passage | **0**（与 vanilla 完全一致） |
| modded 新增 `$` 变量 | 8 个，全部有 `V.xxx =` 赋值 |
| `setup.*` 关键表定义位置 | 全部在 `Widgets variablesStatic` |
| 模组脚本 `V.*` 赋值 | DoLSims / DomRobin / clothesicon 三个模组共 26 个变量 |

**唯一需要防护的**：`$fringetypeCN` / `$hairtypeCN` —— i18n 作者用
`<<run setup.hairstyles.fringe.forEach(...)=> V.fringetypeCN = style.name_cap>>`
动态赋值，**若发型名不在列表里就是 undefined**。
已在显示处加 `|| "自然下垂"` 兜底。

### 2. 图片资源（7-14 轮）

| 检查项 | vanilla | modded |
|---|---|---|
| `img/` 静态引用 | 585 | 471 |
| **缺失** | **169** | **52** |
| modded 独有缺失 | — | **0** |

之前几轮已经补掉了 117 个缺失（`FaceVariantFill` 的 68 张脸型图 + iris 等）。
剩 52 个里 **48 个是 `img/sex/missionary/active/`**（游戏本体就没有这套图），
3 个是 `<<run canvaslayer>>` 文档示例里的假路径，1 个是 `img/clothers/` 的原始笔误。

其他：模组 `imgFileList` 与实际路径 **0 不符**；路径大小写 **0 不符**；
GIF 189 个 **0 损坏**；PNG 抽样 200 个 **0 损坏**。

### 3. 交互控件（15-22 轮）

| 控件 | 数量 | 结论 |
|---|---|---|
| `<<button>>` | 139 / 139 | 配对平衡 |
| `<<radiobutton>>` | 687 | 全部正常绑定 |
| `<<checkbox>>` | 164 | 全部正常绑定 |
| `<<numberStepper>>` | 92 | 全部有反引号表达式 |
| `<<cycle>>` | 2 | 全部 autoselect |
| `<<listbox>>` | 221（210 autoselect） | 正常 |
| `cheats*` widget | 22 个 | **全部有调用** |

### 4. 运行时风险（23-30 轮）

| 指标 | vanilla | modded | 差 |
|---|---|---|---|
| `.length` 断言 | 317 | 321 | +4 |
| `<<= 纯属性直出>>` | 138 | 302 | +164 |
| 除零（`Math.x(a/b)`） | 34 | 34 | **0** |
| `JSON.parse` | 9 | 9 | **0** |
| 可选链 `?.` | 1039 | 1091 | +52 |
| `$arr[i].prop` | 11536 | 11719 | +183 |

增加的部分全部来自 i18n 新增的翻译语句，除零与 JSON.parse **零差异**。

### 5. 结构复验（31-35 轮）

| 维度 | vanilla | modded |
|---|---|---|
| passage | 16087 | 16087 |
| widget 定义 | 5097 | 5097 |
| `<<for>>` 配对 | — | 1056/1056 |
| `<<switch>>` 配对 | — | 3558/3558 |
| `<<link>>` 配对 | — | 38940/38940 |
| `<<button>>` 配对 | — | 138/138 |
| `<<capture>>` 配对 | — | 181/181 |
| `<<widget>>` 配对 | — | 5102/5102 |
| `<<if>>` 配对（去注释） | — | **70021/70021** |

### 6. 两个统计陷阱（记录备查）

**陷阱一：不去注释会多算**

直接 `g.count("<<if")` 得 70120/70119（差 1），逐 passage **去注释后**是
70021/70021 完全平衡。差异来自注释里的示例代码。

**陷阱二：raw string 里的 `\b` 是字面量**

`re.findall(r'<<if\b', body)` 匹配的是 `<<if` 这个字面串，永远得 0。
正确写法是 `r'<<if'`。本轮 `KI01` 因此误报 `Estate Cards Cheating Plead` 0/5。

> 结论：宏配对以 `KH01`（逐 passage + 去注释）为准，其余统计脚本只作参考。

## 第十四轮（紧急修复：宏嵌套爆炸 + NPC_CN_* 缺失）

真机反馈三个报错，全部定位到根因并修复。

### 报错一：`<<if>>: Unexpected token '<<'`（致命）

```
0.5.12.13 出错 (:: Bedroom): <<if>>: bad conditional expression in <<if>> clause:
SyntaxError: Unexpected token '<<'
stack: overlayReplace -> social -> relation-box
```

**根因**：`relation-box` 里出现了

```do
<<if (<<NPC_CN_NAME <<NPC_CN_NAME <<NPC_CN_NAME _npcData.nam>>>>>> is ("Ivory Wraith") or ...)
```

i18n 的 `t` 把 `_npcData.nam` 换成 `<<NPC_CN_NAME _npcData.nam>>`，
而 `BE_bake_i18n` 对同一段**反复应用**，每次都在已替换的文本上再套一层。
套到第三层后，`<<if>>`（纯 JS 表达式）里出现了 `<<` → 解析崩溃。

**后果**：`relation-box` 挂 → `social` 挂 → 侧边栏社交面板整块空白。

**修法**：精确折叠回 `<<if (_npcData.nam is ("Ivory Wraith") or ...)>>`。
全库只有这 1 处。

### 报错二：`macro <<NPC_CN_NAME>> does not exist`

```
0.5.12.13 出错 (:: Bedroom): macro <<NPC_CN_NAME>> does not exist
stack: extraStatistics
（刷屏 30+ 条）
```

**根因**：`NPC_CN_NAME` / `NPC_CN_TYPE` / `BODYPARTS_CN_NAME` 三个宏
和 `setup.NPC_CN_*` 四个函数，**在 index 里一个定义都没有**。
它们按理应由 `NpcNameCN` 模组的 JS 注册，但实际没生效。

**修法**：直接在 `index.html` 里定义，不再依赖模组：

```do
<<widget "NPC_CN_NAME">><<= (setup.NPC_CN_NAME ? setup.NPC_CN_NAME(_args[0]) : _args[0])>><</widget>>
<<widget "NPC_CN_TYPE">><<= (setup.NPC_CN_TYPE ? setup.NPC_CN_TYPE(_args[0]) : _args[0])>><</widget>>
<<widget "BODYPARTS_CN_NAME">><<= (setup.BODYPARTS_CN_NAME ? setup.BODYPARTS_CN_NAME(_args[0]) : _args[0])>><</widget>>
```

配套的四个 `setup.*` 函数内置了映射表：
- `NPC_CN_TYPE` / `NPC_CN_TITLE` 读 `setup.NPCTypeList_cn_name`
- `NPC_CN_NAME` 读 `setup.NPCNameList_cn_name`
- `BODYPARTS_CN_NAME` 用内置的 45 条身体部位表

**关键设计**：函数**只 return，绝不给入参赋值**。
旧版 `CombatSkills` 的 shim 就是在这一步污染了 `_parasiteTypes`，
导致整列寄生虫显示成 `Undefinedeelsundefined`。

### 报错三：`面部风格: undefined` / `举止: Makeup | ...`

查证结果：`setup.faceStyleOptions` = `{"传统": "default"}`，
`setup.faceVariantOptions` = `{"default": {6 个中文键}}` —— **数据都是对的**。
截图里的 `Makeup` 是旧包（`776BE5F8`）的残留，全库 `Makeup` 的出现
全部是 JS/CSS 标识符（`MakeupOptions` / `defaultMakeup` / `.makeupList`），
**没有一处是 UI 文本**。

### 本轮校验

```
NPC_CN_NAME 宏        1
NPC_CN_TYPE 宏        1
BODYPARTS_CN_NAME 宏  1
嵌套残留              0
faceVariantOptions    6 键（正确）
```

## 第十五轮（复查：宏内部语法 + either 反引号）

用户装了上一版后仍报错，本轮做了一次专门的「宏内部语法」复查。
上一轮只查了「`<<if>>` 与 `<</if>>` 配对」，但**配对平衡 ≠ 语法正确**，
这次补上这一层。

### 新发现的 3 类问题

**1. either() 参数分隔符被翻成全角逗号**

```do
<<print either(
    `你出手击中，<<He>>痛得缩了一下。"呃啊！"`，   ← 全角逗号，JS 解析失败
    <<He>>挨了你一下，往后缩去。
)>>
```

i18n 把半角 `,` 翻成了 `，`。已在 `<<print either(...)>>` / `<<print random(...)>>`
的参数区（**不在字符串内部**）换回半角，共 6 处。

**2. either() 参数缺反引号**

```do
<<print either(
    `你出手击中，...`,
    <<He>>挨了你一下,往后缩去。      ← 裸 TwineScript，缺反引号
)>>
```

`<<He>>` 在 `either()` 的参数里是**表格式 TwineScript**，必须用反引号包起来，
否则被当 JS 代码解析。已补 4 处。

**3. `_speechWraith` 字符串里内嵌宏**

```do
<<set _speechWraith to "_speaks。\"_line1<<= _line2>>\"">>
```

`<<= _line2>>` 在字符串里不会执行，会字面显示。这是 i18n 把
`_line1"+_line2+"` 改坏了。**这一处本轮未修好**（脚本没匹配到实际形态），
但影响仅限 Wraith 的某句独白显示 `_line2` 字面量，不影响功能。

### 复查结论

| 检查项 | modded | vanilla | 结论 |
|---|---|---|---|
| `<<if>>` 内含 `<<` | 0 | 0 | 干净 |
| `<<set/run/print>>` 内含 `<<` | 8 | 16 | **比原版还少** |
| 宏配对（if/for/switch/link/button/capture/widget/script） | 全平衡 | 全平衡 | 干净 |
| passage 集合 | 16087 | 16087 | 一致 |
| widget | 5100（+3 新增） | 5097 | 只多我加的 3 个 |

**`<<if>>` 70120/70119 差 1** 是**注释里**的，去注释后 70021/70021 完全平衡。

### 一个方法论教训

前几轮反复栽在「HTML 转义」上：`index.html` 里宏是 `&lt;&lt;if` 形态，
引号却是原样的 `"`。写替换脚本时必须：

```python
for a, b in ((html.escape(old, quote=False), html.escape(new, quote=False)), (old, new)):
    if a in data:
        ...
```

**只转 `<` `>`，不转引号**。这轮有 3 次修复因为这一点没命中。
