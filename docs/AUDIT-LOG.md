# 逐轮审查日志

按 RimWorld《全面审查与修复-通用模板》执行。力度定档 **L3**（涉及全量模组 + 运行时钩子）。

保意图分级贯穿全程：
- ✅ **保意图**：修复后原功能行为不变，只挡异常输入
- ⚠ **部分让步**：上游变了（如游戏本体改了条件），只能适配新值
- ⛔ **破坏意图**：靠删功能换日志安静 —— 一律不做

---

## 第一轮（早期 1–46 轮，摘要）

摸底 → 定位 → 修复，覆盖：

| 检查项 | 结果 |
|---|---|
| 文件清单 vs 实际 | 0 缺失 |
| 图片引用（静态字面量） | 与 vanilla 完全一致 |
| addon 引用（41 处） | 0 问题 |
| TweeReplacer 锚点 | 初测 427 点 |
| ReplacePatcher | 11 条报缺，复核后 4 条是已删 Inuno、7 条是中文锚点（i18n 有）→ 实际 0 |
| JS 全局符号（273 个） | 0 真冲突（`window.Math` 是 polyfill，`EdenCheats`/`MirrorHypnoVariableRefresh` 是注释与 typeof 检测） |
| passage / widget 跨模组重名 | 0 / 0 |
| 跨模组图片路径冲突（1978 条） | 0 |
| 模组图片覆盖游戏资源 | 14 张，全是 ModI18N 的 banner |

**本轮修掉**：DomRobin Bailey 锚点、handheld idle 104 张、BasicNeeds 饥饿初始化 + 进食联动、effectsman 空值、4 浴室如厕 + 大便清小便、BabyHawk widget 冲突、Cargopants 重复。

**Deadwood 破解**：`.modpack` 是固定密钥 XOR → PBKDF2(210000, SHA-256) → AES-GCM。密钥串 `dol-mod-protection-tools:deadwood-reblooms:maplebirch-auth-loader.js` 明文写在 loader 里。解密出 3.95 MB 源码，房产浴室 passage 由此定位。

---

## 第二轮（47–55 轮）

| 轮 | 检查 | 结果 |
|---|---|---|
| 47 | 资源扩展名盘点 | 32881 PNG / 189 GIF，另有 10 个开发残留（`.xcf`/`.pdn`/`.bat`） |
| 48 | 依赖环检测（DFS） | **0 循环**；"缺失"的 `ModLoader`/`GameVersion` 是框架虚拟名 |
| 49 | passage 名合法性 | `FertilityExpansion` 带前导空格是脚本没 trim 的误报（SugarCube 会 strip） |
| 50 | `<<link>>` 断链（38236 个） | 38 条：7 条已补桩、30 条变量插值、**1 条真 bug** |

**本轮修掉**：8 处引号链接（`"School Boy's Toilets"`）。

**关键教训**：第一版用 `findString: '[[Next|"..."]'` 模拟报 6 条未命中 —— 因为 **i18n 把 `Next` 译成了 `继续`**。改 `findRegex` 同时匹配两种写法后 8/8 命中。

---

## 第三轮（56–76 轮）

| 轮 | 检查 | 结果 |
|---|---|---|
| 56 | GIF 完整性（189 个） | 全部解码成功，0 失败 |
| 57-58 | 游戏衣服定义 vs 图片目录 | 用 `slot` 配对时串行（feet 配到眼镜），方法不可靠 |
| 59-61 | 图标宏引用（1162 个） | 前两版不知道路径规则；第三版定位到 **3 个真缺失** |
| 66 | `img/sex` 姿势目录 | `closeRed` 只有 3 子目录但代码只引用这 3 个，不算缺 |
| 69 | `T.*` 跨画面误用 | 0 |
| 70 | 模板 passage 可达性 | `Fishing LocationName` 是死代码（无 `initFishingLocationName`、无 include、链接指向不存在页），从不被访问 |
| 73 | `img/ui` 引用（69 条） | 5 条全是目录/前缀误报 |
| 74 | `img/misc` 引用（155 条） | 16 条全是动态拼接前缀 |
| 75 | body/face/hair/transformations/clothes | 静态引用全部命中 |
| 76 | `setup.*` 全表（43 个赋值点） | 唯一缺失仍是 `missionary/active` 48 张 |

**本轮修掉**：3 个图标路径（`avery-study_hallway` → `avery-study_hallway`、`bronze-key` → `key-bronze`、`stream` → `stream-base.gif`）。

---

## 第四轮（77–90 轮）—— 追 `characterSettings` 崩

真机报 `<<characterSettings>>: cannot find a closing tag for macro <<if>>`。

| 轮 | 动作 | 结论 |
|---|---|---|
| 77 | 定位 `characterSettings` → 在 `Widgets Settings`；查 patcher | DoLSims 有 6 条 patch 改这个 passage |
| 77b | 逐条查 replaceFile 的 if 配对 | `Alice_0.txt` **1 个 `<<if>>`、0 个 `<</if>>`** |
| 77c | 看 `Alice_1.txt` 全文 | 第 19 行的 `<</if>>` 是给 `Alice_0` 闭合用的 |
| 77d | 查 `#2` 的 findString 是否存在于原文 | **不存在**（用的是中文「生殖器」，原文是 `Genitals:`） |
| 78 | 修 `Alice_0.txt` 去掉 `<<if>>` | `Widgets Settings` if=125/125 |
| 79 | 补扫所有 replaceFile 的 if 增量 | 5 条净差非零，逐条看都是片段设计 |
| 81-83 | 全 16000 passage 宏配对（排除注释） | 11 条异常 |
| 84-85 | 查 i18n 条目 | **12 处翻译失衡** |
| 86-88 | 修 | 7 处 `<<link>>` + 1 处 `<<if>>` |
| 89-92 | 剩余 3 条 | 全是误报（findRegex 模拟差异 / 无 patch / 跨 widget 计数） |

**本轮修掉**：`Alice_0` 悬空 if、`I18n Macro Fix` 10 条。

---

## 第五轮（R01–R34，30+ 轮）

用户要求至少 30 轮。这轮**从零重跑**，不看之前的结论。

| 轮 | 检查项 | 结果 |
|---|---|---|
| R01 | 文件清单（52 模组 / 2569 引用） | **0 缺失** |
| R02 | 孤儿资源 | 482 条全是动态拼接，方法不适用 |
| R03 | 锚点（不应用 i18n） | 83 未命中 —— 因为锚点大都是中文 |
| R03b | 锚点（应用 i18n） | **2 未命中** |
| R04 | 追 `Robin Hug Cry` | 原文 `gte 5`，补丁 `gte 2` |
| R05 | 修 DomRobin | findString + replaceFile 同步改 `gte 5` |
| R06 | 复查 Bailey 锚点是否丢失 | **没丢** —— 原文有两处 `robinpaid`，第二处能匹配 |
| R07 | `Bailey's Office` 原文核对 | 确认两处 |
| R11 | JS 语法（114 文件）+ twee 宏配对（99 文件） | JS **0 错误**；twee 3 个已知项 |
| R12 | 模组描述一致性 | `Handheld Idle Fix` / `EffectsMan Null Guard` 缺 `nickName` |
| R13-14 | 补 9 个自建模组的 `nickName` + `description` | 完成 |
| R16-19 | `V.*` 对象变量初始化 | DoLSims 4 个对象变量无赋值语句 |
| R20 | `Widgets Settings` 整体栈匹配 | 0 未闭合 / 0 孤立 |
| R21 | 定位 `npcSettings*` / `characterSettings` | 都在 `Widgets Settings` |
| R22 | 按 widget 切块逐个栈匹配 | **全部平衡** —— 模拟复现不出真机问题 |
| R23 | 移除 `Alice_0` / `Alice_1` 补丁 | 彻底消除孤儿 `<</if>>` 风险 |
| R25 | `characterSettings` 里的 `Object.*` | 自身没有 |
| R26 | 全 passage 的 `Object.*` | 8 处，最可疑 `Object.entries(setup.faceVariantOptions[$facestyle])` |
| R27 | `setup.faceVariantOptions` 键 | 只有 `"default"`，而 `$facestyle` 早期可能是 undefined |
| R28 | `Settings Null Guard 1.0.0` | 3 条兜底 |
| R30 | `DoLSims_v7` 剩余 patch | 4 条，Alice 那两条已移除 |
| R31-32 | 重建 + 验证 | **find 未命中 0**，`Widgets Settings` 0 未闭合 / 0 孤立 |
| R33 | 回归 | JS 0 错误；宏配对 4 个（3 误报 + 1 片段设计） |

**本轮修掉**：`Robin Hug Cry` 锚点适配、`Alice_0`/`Alice_1` 补丁移除、`Settings Null Guard` 3 条、9 个模组描述补齐。

---

## 方法论备忘

1. **改 TweeReplacer 的 findString 前，必须确认 replaceFile 里未闭合的 `<<if>>` 是否靠原文后续的 `<</if>>` 闭合**。一旦配对的另一条补丁失配，就会造出悬空标签 —— 这类 bug 是「修好一半比不修更糟」。
2. **任何针对游戏文本的补丁都必须考虑 i18n**。DoL 的汉化会把 `Next` 译成 `继续`、把英文正文整段替换，按英文写的锚点在汉化环境里静默失配。
3. **宏配对检查必须排除三类注释**：`/* */`（SugarCube）、`/% %/`（Twee 注释）、`<!-- -->`（HTML）。否则 `Estate Cards Cheating Plead` 会误报。
4. **按 `::` 切 passage 时，同一文件里的多个 `<<widget>>` 会被算进同一段**，跨 widget 的 `<<if>>` 会互相配对而掩盖真实失衡。要按 `<<widget>>` 边界单独切。
5. **`img/` 下 482 条「孤儿」和 16 条 `img/misc` 缺失都是动态拼接**（`${}` 模板），静态判断不可靠。
6. **`*Red` 命名是同一类系统性问题**：`setup.tanImg` 的 `t`（晒痕）子表把目录名加了 `Red` 后缀，但 `doggyRed`/`missionaryRed` 从未创建，只有 `closeRed` 存在。
