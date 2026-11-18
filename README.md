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
| 模组数 | 54（其中 13 个为本次新建补丁模组） |
| APK | 182,351,306 字节（173.90 MB），SHA256 `8057C3CD3247C76631C0B7EF97FB25E0FA7D517D3E732568BDF5558AAA36ED66`，已重签名（keystore `dol.jks`，alias `dol`） |

## 修复清单（27 项）

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
