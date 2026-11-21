# Degrees of Lewdity 模组化 APK —— 全面审查与修复（专用提示词模板 v1.1）

> **⚖ 最高准则（凌驾全篇）—— 修复都要建立在「尽量不破坏原有功能及其功能意图」的基础上。**
> 凡是靠「拿掉作者做进去的功能」去换日志安静的改法，一律降级为备选，并逐字写明牺牲了什么；
> 实在没有保意图的路可走，再另做打算 —— 但那时必须单列成「需要拍板」，不许自己悄悄决定。
> 判据与分级见 **§0.2**。

> **📌 任务性质与内容边界（先读这段，再动手）**
> 本任务是**本地单机游戏的模组维护与代码审查**，对象是已存在的第三方开源项目
> （Degrees of Lewdity 及其社区模组）的代码与已发布文本。工作内容是修 bug、修转义、
> 补翻译、写回归测试、维护仓库 —— **不是在创作内容**。
>
> 遇到成人向文本时，一律按「代码审查」处理：只做**字符串层面**的替换、翻译与转义修复，
> **不扩写、不演绎、不生成新的露骨内容**。判断某段文字该不该改，看的是
> 「它是不是被翻译/转义破坏了」，不是「它写得好不好」。
>
> 若某一段因内容策略被拒绝处理：**记录下来、跳过该段、继续跑其余判据**，并在报告里
> 单列「因策略未处理」清单 —— 不要整轮停下，也不要尝试规避策略。

> **模板里所有【】都是硬性要求，不是建议。**
> 唯一例外是 **§0.1 力度分级** —— 它决定这一轮要走哪些节。

> ⚠⚠ **本模板的判据都带「实测版本」。DoL-Lyra 一升级，这些结论就可能失效。**
> 动手前先看你要用的那条判据标的是哪个版本；跨版本沿用前，先用 CDP 复验一遍。

> 💡 **本模板的所有判据都是「被打脸之后」修出来的。** §5 事故台账里每一条都标注了
> 「我一开始以为是什么 / 实际是什么」，照着那个思路走能省很多轮。

---

## 速查卡 —— 遇到现象先查这里

> 正文很长，**不要从头读**。先在这张表里找你的现象，找到就直接跳对应章节。

### A. 装不上 / 装上了打不开

| 现象 | 最可能的根因 | 去哪 |
|---|---|---|
| 安装包解析失败 /「无效安装包」 | `resources.arsc` 被压缩了。**Android 要求 targetSdk ≥ 30 时 arsc 必须 STORED** | **§1.4** |
| HarmonyOS「与操作系统不兼容」 | 签名是 `SHA384withRSA`，鸿蒙只认 `SHA256withRSA` | **§1.4** |
| 打开后纯白屏 / 转圈不进 | `index.html` 的 passage 数是 0 或个位数 —— 通常是**双转义事故** | **§5.1** |
| 能进标题但点「开始」卡住 | 某个 `<<script>>` 抛异常，`setup` 未初始化 | §2.1 |
| 装了新包但问题没变 | **手机上装的还是旧包** | §6.3 |

### B. 进得去，但红字刷屏

| 现象 | 最可能的根因 | 去哪 |
|---|---|---|
| `macro <<xxx>> does not exist` | 宏名被翻译破坏；或**组件把 `<<宏>>` 塞进了 `<<if>>` 表达式** | **§5.5** |
| `<<if>>: bad conditional expression ... Unexpected token '<<'` | `<<if>>` 里嵌了宏调用 | **§5.5** |
| `ReferenceError: xxx is not defined` | 函数名被改错（**最常见：手写修复表少一个字母**） | **§5.4** |
| `Cannot read properties of undefined (reading '0')` 在商店 | 物品对象缺字段（如 mod 服装缺 `slot`） | **§5.6** |
| `[clothesIndex]: slot or valid object not provided` | 同上，`slot` 是 `undefined` | **§5.6** |
| `reading 'iconFile'` / `'accIcon'` / `'detailIcon'` / `'reduce'` | 上游 `_itemData` 是 `undefined` | **§5.6** |
| `Corrupted variables have been detected` | **存档数据损坏，不是包的问题** | §5.8 |
| `do_patch() cannot find findString` | TweeReplacer 锚点不匹配（**模组版本问题，不是缺模组**） | **§3.10** |
| `regexFlag: undefined` | 补丁里写了 `"regexFlag": ""`（空字符串） | **§5.16（含第12轮订正）** |
| `sets $x to` / `calls <<x>>` **出现在正文** | 宏被破坏；**但先确认它是不是在注释里** | **§5.17** |
| `Malformed arrow function parameter list` / `Missing initializer in const` | 宏表达式里用 `_x` 当箭头参数 / const 名 | **§5.25** |
| `cannot find a closing tag`，但静态看配对正常 | passage 正文有**裸 `<`**，浏览器吞了 `</if>` | **§5.24** |
| 运行时 passage 里冒出 `[[继续|…]]` 乱码 | TweeReplacer 正则以未转义 `[[` 开头（字符类） | **§5.23** |
| `do_patch() cannot find`，静态锚点却存在 | maplebirch 等模组抢先改写了 passage | **§5.28** |
| `<<npcrelationship>>提供了错误的参数` | 传了中文名（它按英文 `nam` 查） | **§5.29** |

### C. 显示不对（英文残留 / 变量没展开）

| 现象 | 最可能的根因 | 去哪 |
|---|---|---|
| 战斗里 `broad男人` / `left手` / `right手` | `<<combatperson>>` 只用了英文 `$description` | **§5.7** |
| `You _You坐在了...` | `<<set _You to "">>` 被破坏成裸 `You` | §5.9 |
| `up your _lower.name. It 并缠绕...` | 变量被拆开 / 宏没闭合 | §5.9 |
| 整句英文（`The squid drops off you...`） | i18n 漏翻 | §3.7 |
| NPC 名是英文 | `description_CN` 被直接赋了英文 `title` | **§5.10** |
| `Lewd 颤抖 ripple through your body...` | 半翻（翻译中断在句子中间） | §3.7 |
| 按钮还是英文（`Hang up coat` / `Confess your crimes`） | `<<link [[文本\|目标]]>>` 里的文本漏翻 | **§5.18** |
| 某模板调用失效（如 `?admires`） | **`Template.add` 的名字被翻译了** | **§5.19** |
| 咖啡/食物名部分变英文 | `setup.CafeFoodList_cn_name` 被赋值两次，后者覆盖前者 | **§5.20** |
| 正文里莫名多一个 `>` | 三重尖括号 `>>>` | **§5.21** |
| 成就描述/提示、JS 里的句子在**运行时**是英文（静态也没中文） | ModI18N 运行时 JS 替换被我们的静态改动挤歪 | **§5.26** |
| 某个剧情分支/选项永远不出现（英文版有） | 显示值兼作逻辑值，汉化改了值 | **§5.27** |

### D. 改完没生效 / 改一次坏一次

| 现象 | 最可能的根因 | 去哪 |
|---|---|---|
| 手工改好了，下次构建又变回原样 | **`build_all` 第 1 步会从源重新生成 index** | **§4.1** |
| index 里改了某个 `setup.xxx`，进游戏还是英文 | **模组在运行时无条件覆写**（模组最后跑） | **§4.2** |
| 改 A 坏了 B | 全局字符串替换误伤了数据值 | **§5.3** |
| 补丁打在了对的地方，但没生效 | **打在了错的 widget 里**（没查调用链） | **§5.6** |
| 修好了但下轮又复发 | 没做成幂等脚本 / 没加断言 | **§4.1 / §3.6** |

### E. 验证怎么算过

| 问题 | 答案 | 去哪 |
|---|---|---|
| 「日志没红字」算过吗 | **不算**。那只证明没崩，证明不了功能生效 | **§6** |
| 怎么才算过 | 静态回归（60 项）+ CDP 运行时探针 + 关键流程 | **§6** |
| 怎么判断某个函数真的挂载了 | CDP 里 `String(setup.xxx)` 打印源码 + 实调返回值 | **§2.1** |
| CDP 加载 100MB 一直超时怎么办 | **别硬等**，改用 Node 单元测试（从 index 抠表达式 + 翻成 JS 跑） | **§2.4** |
| 怎么判断「这个是不是我改坏的」 | **diff 黄金基线**，不要凭印象 | **§2.2** |

---

## §0 适用范围与前置

### §0.1 力度分级（决定这一轮走哪些节）

| 档位 | 触发场景 | 必走节 |
|---|---|---|
| **L1 快查** | 只改了一两处翻译 | §2.2 + §6.1 |
| **L2 常规** | 修一个具体 bug | §1 + §2 + §4 + §6 |
| **L3 全审** | 用户要求「全面审查」「至少 N 轮」 | **全篇，且每轮都要跑 §6.1 回归** |

### §0.2 修复的保意图三级

| 级别 | 定义 | 举例 |
|---|---|---|
| **① 保意图** | 只改错的地方，功能行为与作者意图一致 | 把 `applyClothingShopFiltre` 改回 `Filters` |
| **② 兜底** | 原逻辑不动，只加 fallback | `_item.slot \|\| 反查 \|\| "upper"` |
| **③ 牺牲** | 必须放弃某个功能才不崩 | **必须单列「需要拍板」，不许自己决定** |

**判据**：改完之后，问自己「作者如果看到这个改动，会不会认为我删了他的功能」。
- 不会 → ①/②，直接做
- 会 → ③，停下来写「需要拍板」

### §0.3 什么不该修

以下这些在**黄金基线里同样存在**，不是我们的责任，**改了反而可能引入新问题**：

| 项 | 基线值 | 说明 |
|---|---|---|
| 未配对的宏 | 67（原版 68） | 原版就有的排版问题 |
| `<<link>>` 指向不存在的 passage | 26 | 原版死链桩 |
| `<<include>>` 缺失目标 | 6（Fishing LocationName 系列） | 原版 |
| `Tutorial` 的 `unknown hair colour: undefined` | 74 | 角色创建前，正常 |
| `Corrupted variables` | — | **存档问题**，不是包的问题 |
| 重复 widget（Wraith 系） | 16 个，**内容完全相同** | 我修 Widgets Repair 时的副产物，无害 |

### §0.4 翻译工作必须外包给低成本模型（省 token）

**【硬性要求】凡是翻译类任务**（新增词条、补漏翻、批量校对、生成 `_cn_name` / `_DESC` 表、
把英文残留补成中文等），**不要用主审查模型（opus-5-5 等高价位模型）逐条翻译**。
改用**智能体团队协作（subagent / agent teams）**，把翻译批次交给
**`deepseek-v4-flash`**（或同级的低成本模型）执行。

分工：

| 角色 | 负责 |
|---|---|
| 主模型 | 拆批、给术语表与上下文、验收译文、合并回写、跑 §3.4 校验 |
| 子代理（`deepseek-v4-flash`） | 按批次翻译，返回结构化结果（原文 → 译文），不碰文件 |

【判据】一次翻译任务里，**主模型的 token 消耗不得随词条数线性增长** ——
如果翻 500 条和翻 50 条花掉的主模型 token 差不多，说明分工对了；如果翻 500 条
主模型 token 翻 10 倍，说明还在自己逐条翻。

【注意】
- 外包**不等于免检**：译文仍要过 §3.4 的判据（表只赋值一次、`Template.add` 名字不能含中文、
  `_desc_CN` 与 `_desc` 长度相等……）。
- 术语表必须由主模型先定好并随批次下发，否则子代理会造出不一致的译名（§5.3 的教训）。
- 子代理只产出**文本**，落盘、转义、插入由主模型统一做 —— 避免子代理手改 index 造成双转义（§5.1）。

### §0.5 不复杂的工作应当并行委派（同样为省 token、也提速）

**【要求】除翻译外，凡是机械性、可独立验证的工作，也应当交给子代理 / 智能体团队并行做**，
主模型只保留判断与验收。不要把高价模型的算力花在“体力活”上。

| 适合委派 | 为什么 |
|---|---|
| 批量统计（某宏出现几次、某表多少条、某字段几处） | 纯匹配，结果可复核 |
| 日志过滤与归类（几千行按错误类型分组、去重、计数） | 体力活，不需要推理 |
| 文件清单 / 哈希 / 大小 / 时间戳对比 | 机械比对 |
| 重复性代码生成（批量 `mk()` 表项、`_cn_name` 条目、样板 patch） | 模板化产出 |
| 大范围搜索定位（grep 候选行号、列出所有命中文件） | 只需返回位置 |
| 文档草稿整理（把散落的结论排成 markdown、表格对齐） | 格式化 |

| 必须主模型自己做 | 为什么 |
|---|---|
| 根因判断、调用链推理（§2.3） | 错一步全错 |
| 补丁锚点设计（`findString` / 正则边界） | 要结合上下文与转义形态 |
| 保意图决策（§0.2 的 ①/②/③） | 需要判断力，涉及是否牺牲功能 |
| 验收与「是否真的生效」（§6） | 不能外包给会幻觉的模型 |
| 跨轮一致性与防复发判据（§3.6） | 需要全局记忆 |

**【硬约束】**
- **独立**：每份子任务必须能独立完成，不依赖其他子任务的中间结果；
- **可验证**：主模型拿到结果后，能用**一条命令或一个判据**复核（复核不了的任务不许外派）；
- **不碰文件**：子代理只读、只返回结论；所有写盘由主模型统一执行；
- **留痕**：报告里要能追溯「谁做的、依据是什么」，不能出现来源不明的结论。

---

## §1 环境与工具链

### §1.1 目录约定

```
E:\TAML\_dol\
  out\        DoL-Lyra-<版本>-CHS-modded.apk    ← 交付物
  archive\    历史归档（每次构建自动存一份，文件名带说明）
  work\       构建工作区
    index_modded6.html   ← 构建中间产物（转义形态）
    build.py             ← 8 步总管
    build_all.py         ← 修复链（80+ 步）
    REGRESS_ALL.py       ← 60 项回归
    *.py / *.js          ← 各轮修复脚本 / 探针
  repo\       GitHub 仓库（docs\ 放报告）
```

### §1.2 构建管线（**关键理解**）

`build.py` 是 8 步总管：

```
1) inject6.py          从源重新生成 index_modded6.html  ★★★ 会覆盖手工修改
2) build_all.py        修复链（80+ 步）
3) 打包 (zipfile)
4) 签名 (uber-apk-signer, SHA256withRSA)
5) validate.py         22 项校验
6) rebuild2_fast.py    重打包（强制 arsc STORED）
7) 守门员
7.5) REGRESS_ALL.py    60 项回归  ← 已接入
8) exec_verify.py      真实执行验证（5 个 script 块）
```

**`build_all.py` 的收尾顺序（必须遵守）**：

```
... → R10 → R17 → T10 → T16 → T25 → TF01_nest_guard.py（永远最后）
```

**为什么 `TF01` 必须最后**：它检查并修复 widget 嵌套，会移动内容。
**为什么翻译类要放在 `TF01` 之前**：`TF01` 可能重排文本，翻译得在它之前完成。

### §1.3 `index.html` 的真实形态（**必读**）

```
<tw-passagedata name="Start" tags="" ...>   ← passage 标签 = 明文
&lt;&lt;if $x&gt;&gt;                            ← passage 正文 = HTML 转义
```

- **标签明文 + 正文转义**。所以：
  - 数 passage 用 **raw**：`re.findall(r'<tw-passagedata[^>]*name="', raw)`
  - 找正文内容先 **unescape**：`g = html.unescape(raw)`
- **绝对不要对整份文件做 `html.escape()`** —— 会把标签也转义，passage 数变 0，白屏。见 §5.1。
- **写入时**：只对**要插入的片段**做 `html.escape(frag, quote=False)`，拼进 `data`（raw）。
- **定位 `<<widget "xxx">>` 在 raw 里**：要用 `html.escape('<<widget "xxx">>', quote=False)`。

### §1.4 Android 安装硬要求

| 要求 | 判据 |
|---|---|
| `resources.arsc` **STORED** | `zip.getinfo("resources.arsc").compress_type == 0` |
| 签名 **SHA256withRSA** | `keytool -printcert -jarfile X.apk` 里有 `SHA256withRSA`，且**没有** `SHA384withRSA` |
| ZIP 完整 | `zipfile.ZipFile(apk).testzip() is None` |

**实测**：鸿蒙（HarmonyOS 7.0 / API 26）**拒绝 SHA384withRSA**。
重建 keystore 时要用 `-sigalg SHA256withRSA`，别名 `dol`，密码 `<签名口令：见本机 work\keystore.local，不入库>`。

**打包保护**：`rebuild2_fast.py` 里有 passage 数安全阀（< 10000 直接中止），并强制 arsc 用 `ZIP_STORED`。

### §1.5 CDP 测试环境

- **Edge headless + Node 原生 `fetch`/`WebSocket`**，零 npm 依赖。
- **`file://` 不行** —— ModLoader 用 `fetch` 读资源，跨域会失败。**必须起 HTTP 服务**：
  ```powershell
  python -m http.server 8801   # 在 E:\TAML\_dol\work 下
  ```
- 调用：`node cdp_probe.js <url> @probe.js <超时秒>`
- **100MB 的 index 加载要 60~90 秒**。`cdp_probe.js` 内部有硬上限，给 480 也可能只用 61 秒就判超时。
- 探针里 `Macro` **不是全局**，要用 `SugarCube.macros`。
- 探针里 `Story` 也不是全局，要用 `SugarCube.Story`。

### §1.6 黄金基线

```
archive\DoL-Lyra-0.5.12.13-CHS-modded_20261120-061313_修复arsc可安装.apk
```

**基线指标（任何一轮都必须对齐）**：

```
passage  16088（基线）/ 16089（当前，多出的 Widgets Repair 是修复用）
widget   5104
SHA256   0A316E37...（用户实机验证可安装）
```

---

## §2 诊断方法论

### §2.1 五层顺序（**不要跳层**）

```
① CDP 打印 toString()   →  看运行时真实源码长什么样
② 搜模组 ZIP           →  看是不是模组改的
③ 搜 index（unescape 后）→  看静态定义
④ 对比基线 APK         →  判断「是不是我改坏的」
⑤ 追调用链             →  找真正执行的那条路径
```

**为什么必须先 ①**：模组会在运行时覆写 `setup.*`，也会用 TweeReplacer 改写 passage。
只读 index 会得出「明明是好的啊」的错误结论。

**实测（§5.11）**：`Npc Name CN` 的 `forceSetup()` 无条件
`st.BODYPARTS_CN_NAME = partCN` —— index 侧修了 8 个版本都没用，因为模组最后跑。

### §2.2 基线对比（判断「是不是我改坏的」）

```python
GOOD = r"E:\TAML\_dol\archive\..._修复arsc可安装.apk"
gb = html.unescape(zipfile.ZipFile(GOOD).read("assets/www/index.html").decode("utf-8","replace"))
# 对比同类片段的实际写法
```

**任何「这个是不是本来就有」的疑问，先 diff 基线，不要凭印象。**

### §2.3 追调用链（**打补丁之前必做**）

**实测（§5.6）**：`Forest Shop` passage 内容是 `<<forestShop-main>>`，
而不是直接调 `clothingShopv2`。实际链是：

```
Forest Shop → forestShop-main → AllShop → clothingShopv2 → generateshoppage
```

**我第一次把修复放在 `clothingShopv2` 里，完全无效** —— 因为另有路径直接进 `generateshoppage`。

**查法**：
```python
# 1. 看入口 passage 调什么
print(PASSAGES.get("Forest Shop"))
# 2. 顺着 widget 一层层往下找
m = re.search(r'<<widget "forestShop-main">>(.*?)<</widget>>', g, re.S)
# 3. 看报错的 stack 里有哪些 widget
#    日志里 stack: [{"type":"widget","name":"generateshoppage"}] ← 只这一层
```

### §2.4 CDP 超时的替代方案：Node 单元测试

**问题**：100MB index 加载慢，`cdp_probe.js` 频繁超时。

**替代路（推荐）**：把要验证的表达式从 index 里抠出来，在 Node 里跑。

```javascript
// 1. 读 index，unescape
const raw = fs.readFileSync("index_apk.html", "utf8");
const g = raw.replace(/&lt;/g,"<").replace(/&gt;/g,">").replace(/&quot;/g,'"')
             .replace(/&#39;/g,"'").replace(/&amp;/g,"&");

// 2. 抠出表达式
const m = g.match(/<<set \$_realSlot to \(([\s\S]{0,600}?)\)>>/);
let expr = m[1];

// 3. SugarCube 语法 → JS
let js = expr.replace(/\$([A-Za-z_][A-Za-z0-9_]*)/g, "_$1")
             .replace(/\bisnot\b/g, "!==")
             .replace(/\bis\b/g, "===");

// 4. 用模拟数据跑
const fn = new Function("setup", "_item", "_clothingShopSlot", "return (" + js + ");");
console.log(fn(mockSetup, mockItem, "all"));
```

**实测**：`T02_slot_unit_test2.js` 这样跑了 12 个用例，全部通过，耗时 < 1 秒。

---

## §3 审查维度清单（12 类）

> 每轮至少扫 **D/F/G**；L3 全审要全扫。

### §3.1 A 类 —— 安装前提（4 项）

```python
i = z.getinfo("resources.arsc")
assert i.compress_type == 0                      # STORED
assert z.testzip() is None                        # ZIP 完整
assert "SHA256withRSA" in keytool_output          # 签名
assert "SHA384withRSA" not in keytool_output      # 无旧算法
```

### §3.2 B 类 —— 内容完整性（5 项）

```python
# 精确计数（宽正则会多算 1 处，因为某个 JS 字符串里有 pid=\"1\"）
def pn(t):
    return re.findall(r'<tw-passagedata\s+(?![^>]*\\")[^>]*name="([^"]*)"', t)

assert len(pn(raw)) >= len(pn(base_raw))          # passage 数
assert len(wn(raw)) >= len(wn(base_raw))          # widget 数
assert not (set(base_passages) - set(passages))   # 无缺失
assert not (set(base_widgets) - set(widgets))     # 无缺失
assert not {k for k,v in Counter(passages).items() if v>1}   # 无重复
```

### §3.3 C 类 —— 代码卫生（5 项）

| 项 | 判据 | 陷阱 |
|---|---|---|
| 代码位置含中文 | `<<if/set/run/...>>` 的**表达式部分**（挖掉字符串后）无中文 | 必须挖字符串，否则 `"你好"` 会误报 |
| 模板字符串粘连 | 只在 `<<script>>`/`<<run>>` 里查 `\.xxx中文` | **普通文本里的反引号不是 JS 模板**，见 §5.2 |
| CSS 选择器含中文 | `[.#]xxx中文xxx {` | — |
| SugarCube 关键字被翻译 | `且`/`或`/`不是`/`大于等于` 独立出现在表达式里 | — |
| **宏调用出现在 `<<if>>` 里** | `<<if ... <<宏>> ...>>` | **社交界面崩溃的根因**，见 §5.5 |

**正确实现（逐行扫，先挖字符串再找 `>>`）**：

```python
def scan_macro_in_if(text):
    cnt = 0
    for line in text.split("\n"):
        if "<<if" not in line and "<<elseif" not in line:
            continue
        for m in re.finditer(r"<<(?:if|elseif)\b", line):
            rest = line[m.end():]
            # ★ 先挖字符串成等长空格，再找 >>
            masked = re.sub(r'"[^"]*"', lambda x: " "*len(x.group(0)), rest)
            masked = re.sub(r"'[^']*'", lambda x: " "*len(x.group(0)), masked)
            masked = re.sub(r"`[^`]*`", lambda x: " "*len(x.group(0)), masked)
            e = masked.find(">>")
            body = masked if e < 0 else masked[:e]
            if re.search(r"<<[A-Za-z]", body):
                cnt += 1
    return cnt
```

**为什么必须先挖字符串**（血泪）：
- 不挖 → `<<if x ? "潮红的面颊" : "<<genitals>>">>` 会被误报
- 用 `rest.find(">>")` → 被字符串里的 `>>` 截断，引号不闭合 → 又误报
- 用 `[^<>]{0,500}` → **匹配不到含 `<` 的内容** → 报「0 处」，实际有 2 处

### §3.4 D 类 —— 翻译表（10 项）

> **翻译本身请外包**（见 §0.4）：主模型只负责拆批、定术语表与验收，逐条翻译交给
> `deepseek-v4-flash` 子代理执行，别用高价模型自己一句一句翻。

| 表 | 位置 | 预期 | 判据 |
|---|---|---|---|
| `setup.NPCTypeList_cn_name` | index | **只赋值 1 次**、≥240 条 | 曾出现两次赋值，63 vs 248 |
| `EXTRA` 表 | `var EXTRA = {` 在 `var NAMES = ["NPC_CN_TYPE"` 之前 | ≥155 键 | — |
| `setup.CAFE_FOOD_CN` | `mk()` 包装 | 含 `"lemonade"` `"cheesecake"` | — |
| `setup.DirectionCN` | 同上 | 含 `"back": "后"` | — |
| `setup.brothelshowType_CN` | 同上 | 含 `"sex": "性爱表演"` | — |
| `setup.update_cloth_cn` | `mk(null, fn)` 形态，**表是 null 走 extra 回调** | 含 `"hat"` `"scarf"` | 设计如此，不是坏了 |
| `_DESC` 表 | index | 75 键，含 `broad`/`bulky`/`robust` | — |
| `_desc_CN` 数组 | 与 `_desc` **逐项对应、长度相等** | 23 项 × 4 组 | 长度不等就会错位 |
| **`Template.add` 的名字** | index | **不能含中文** | 见 §5.19 |
| **`setup.CafeFoodList_cn_name`** | index | **只 1 次赋值、≥25 词** | 见 §5.20 |

### §3.5 E 类 —— 模组（5 项）

| 项 | 判据 | 实测值 |
|---|---|---|
| 模组数量 | ≥57（第12轮撤下 Quoted Link Fix） | 57 条（56 ZIP + 1 modpack） |
| 每个 mod ZIP 完整 | 逐个 `testzip()` | 0 损坏 |
| `Npc Name CN` 的 `BODYPARTS` | **≥70 键** | 76 |
| TweeReplacer 补丁的 `regexFlag` | **不能是空字符串**（但删之前先确认正则本身对，§5.16 订正） | 0 处空 |
| TweeReplacer `findRegex` | **不得以未转义 `[` 开头**（字符类陷阱） | 0 |
| 模组 `.twee` 宏表达式 | 经引擎 parse 可编译（`T03 --twee-dir`） | 0 失败 |
| 服装对象的 `slot` 字段 | 每个 `setup.clothes[栏位]` 的 item 都要有 | 由 R17 兜底 |

### §3.6 F 类 —— 历史修复防复发（32 项）

**必须把每一个修过的字符串都写成断言**。

```python
HIST = {
    "_下体。": 0, "C.npc.罗宾": 0, "applyClothingShop过滤": 0,
    "tanning启用d": 0, "次序:": 0, "_精液，": 0, "我的arousal": 0,
    "lean,精瘦": None,  # ... 逐项
    "<<br>>": 0, "flesh_text": 0, "printNobody": 0, "<<</if>>": 0,
    "按enter键": 0, "一个Wink": 0, "束缚play": 0,
    "applyClothingShopFilter(_items)": 0, "lifts up": 0,
    "You_You": 0, " glory hole": 0,
}
GOOD_ONLY = {
    "applyClothingShopFilters": 4, "<<print _You>>": 3,
    "黑暗的触须": 1, "你的眼睛发痒": 1,
}
```

**原则**：修过的 bug 必须变成「该字符串出现次数 = 0」的断言，否则下一轮构建会悄悄复发。

### §3.7 G 类 —— 英文残留

| 检查 | 判据 | 实测 |
|---|---|---|
| `<<print "英文句子">>` | 纯英文 + ≥3 词 | 0 |
| `<<either(...)>>` 全英文选项 | 整句（有句末标点）优先 | 8 → 已修 |
| **`Template.add("x", () => either(...))`** | 玩家可见的闲聊/物品名 | 20 → 已修 |
| **`<<link [[文本\|目标]]>>`** | ≥3 个英文词，**排除 `$var` / `setup.` / `<<宏>>`** | 29 → 已修 |
| `<<option>>` / `<<checkbox>>` / `<<radiobutton>>` | 纯英文 | 0（全是变量引用） |
| `<<button>>` | 纯英文，**排除 `<span class='fa-icon'>`** | 0（全是图标） |
| 战斗描述 | `<<combatperson>>` 用哪个 description | 已修 |
| 商店物品名 | `_itemData.cn_name_cap` 是否存在 | 运行时注入 |
| 模组 `.twee` 英文正文 | 排除 `::` / `<<` / `<!--` 开头 | 38 行，**全是 JS** |
| 模组 JS 硬编码 UI | `text:` / `label:` / `innerHTML =` | 47 条，多为框架串 |

**`is_text()` 判据（排除误报的关键）**：

```python
def is_text(s):
    s = s.strip()
    if not s or re.search(r"[\u4e00-\u9fff]", s):        return False
    if re.search(r"[$`(){}\[\]]|=>|::|\.\w+\.|setup\.|"
                 r"\bvar\b|\bfunction\b|\breturn\b|\bnull\b|\bundefined\b", s):
        return False
    if s.startswith("<<") or s.startswith("<"):           return False
    if len(re.findall(r"[A-Za-z]{2,}", s)) < 3:           return False
    return True
```

### §3.8 H 类 —— 运行时错误（CDP）

- `cdp_flow.js`：开局 → 创建 → 卧室 → 镜子 → 衣柜 → 走廊 → 孤儿院 → 户外，**10 步 0 错误**
- `cdp_passages2.js`：40+ passage 遍历，**只有 `Tutorial` 允许有噪音**
- `probe_full.js`：5 个 `setup` 函数实调返回中文

### §3.9 I 类 —— 存档兼容

- `Corrupted variables` 是**存档问题，不是包的问题**。不要为它改包。
- 但要检查：是否某个修复把**变量名**改了（会导致旧存档失效）。
- 处置话术：告诉用户「先备份存档，再点重设」。

### §3.10 J 类 —— TweeReplacer 补丁锚点

- 报错格式：`do_patch() cannot find findString: <锚点> in [<passage>]`
- **不是「缺模组」**，是「模组增强功能不生效」。
- 排查：
  1. 读报错原文的 `findString`/`findRegex`
  2. 去对应 passage 搜这段代码
  3. **搜到** = 字段/顺序问题；**搜不到** = 模组版本与游戏版本不匹配
- **实测案例**：
  - `[DoLSims] findRegex: <<widget "fallentransform">>...` → **真实 widget 名是 `fallenTransform`（驼峰）**，日志显示全小写是 `TweeReplacer` 打印处理
  - `[DoLSims]` 补丁里 `"regexFlag": ""` → **空字符串导致正则构造失败**
  - ~~`[DomRobin] findString: <<if $robinpaid isnot 1...>>` → 锚点在，是旧包问题~~
    **第12轮订正**：静态 index 里锚点确实在，但 **maplebirch 的 zone 补丁先执行**，运行时已改成
    `… and !maplebirch.get("Finance").orphanage.robinFree>>`。见 §5.28。
- **⚠ 第4步之后必做**：用运行时导出（§2.5）确认锚点在**运行时文本**里是否存在 —— 静态 index 不是 TweeReplacer 看到的内容。
- **⚠ 正则补丁**：在 Node 里对目标 passage 跑一遍 `matchAll`，看命中片段（`AQ05_tr_audit.js`）。命中片段 ≤3 字符基本就是写错了（§5.23）。

### §3.11 K 类 —— 模组覆盖 index

- 模组的 `forceSetup()` / `st.XXX = ...` 在**最后执行**，会覆盖 index 里的同名定义。
- **判据**：CDP 打印 `String(setup.xxx)`，如果和 index 里的源码不一样 → 被模组覆盖了。
- **修法**：改**模组自己的表**，不要改 index。

### §3.12 L 类 —— 资源缺失

- `Failed to load image img/clothes/<slot>/<name>/...`
- **这条其实是个诊断线索**：它告诉了你该物品真正的 `slot`（如 `clothes/upper/` → `upper`）。
- 在 §5.6 的修复里，就是靠这条推断出 `dragonbreath` 的 slot 应该是 `upper`。

---

## §4 修复铁律

### §4.1 铁律一：修复必须做成幂等脚本并接入 `build_all`

**根因**：`build_all` 第 1 步从源重建 index。手工改的一律蒸发。

**标准脚本模板**：

```python
"""XX01：一句话说明（幂等）。"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

# ---- 1. 安全阀 ----
if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[XX01] index 形态异常")
    sys.exit(1)

# ---- 2. 幂等标记 ----
MARK = "[XX01]"
g = H.unescape(data)
if MARK in g:
    print("[XX01] 已存在，跳过  passage=%d" % len(re.findall(r'<tw-passagedata[^>]*name=', data)))
    sys.exit(0)

# ---- 3. 修复（同时试转义/未转义两种形态）----
# ★ 两边必须同形态：(escape(old), escape(new))。写成 (escape(old), new) 会把裸 < 写进 passage（§5.24）。
# ★ 不要命中一种就 break：同一句话可能既在 passage 正文（转义）又在 JS 里（原样），第12轮 F12 因此漏改。
# ★ 只想改 passage 时，先用 passage_span() 限定范围（见 AD10 / AI01），不要全文件替换。
total = 0
for old, new in FIXES:
    for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
        if a in data:
            c = data.count(a)
            data = data.replace(a, b)
            total += c

# ---- 4. 打标记 ----
data = data.replace(
    H.escape('<<widget "generateshoppage">>', quote=False),
    H.escape('<!-- [XX01] 说明 -->' + '<<widget "generateshoppage">>', quote=False), 1)

open(HTML, "wb").write(data.encode("utf-8"))

# ---- 5. 校验并返回退出码 ----
g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
ok = all(v == 0 for v in BAD.values())
print("[XX01] 修 %d 处  passage=%d  %s" % (total, n, "OK" if ok else "FAIL"))
sys.exit(0 if ok else 1)
```

**接入 `build_all.py`**：

```python
(r"E:\TAML\_dol\work\XX01_xxx.py", "一句话说明"),
```

### §4.2 铁律二：模组覆盖优先于 index

见 §3.11。**判据顺序**：先 CDP `String(setup.xxx)`，再看是不是模组改的。

**实测（§5.11）**：`Npc Name CN` 的 `BODYPARTS` 表只有 30 键，必须扩到 76 键
（改模组 ZIP 里的 JS，不是改 index）。

**改模组 ZIP 的标准流程**：

```python
# 1. 解出所有 mod ZIP
m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", g, re.S)
parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m.group(1))

# 2. 找到目标模组
for s in parts:
    raw = base64.b64decode(re.sub(r"\s+", "", s))
    if raw[:2] != b"PK":
        continue
    zz = zipfile.ZipFile(io.BytesIO(raw))
    bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
    if bj.get("name") != "TARGET":
        continue
    # 3. 改文件
    # 4. 重打包
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
        for info in zz.infolist():
            d = zz.read(info.filename)
            if info.filename == "target.js":
                d = new_content.encode("utf-8")
            zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
            zi.compress_type = info.compress_type
            zi.external_attr = info.external_attr
            zo.writestr(zi, d)
    # 5. 重编码回 modDataValueZipList
    nb64 = base64.b64encode(buf.getvalue()).decode("ascii")
    pat = re.compile(r'"' + re.escape(s[:80]) + r'[A-Za-z0-9+/=\s]*"')
    new_block = pat.sub(lambda _: '"' + nb64 + '"', new_block, count=1)
```

### §4.3 铁律三：全局字符串替换是最后手段

**血的教训（§5.3）**：把 `"lust": "色欲"` 放进全局映射，全局替换 `"lust"` →
**165 处 `$NPCList[].lust` 被误改**。

**正确做法**：只在**目标块内**替换；`?sin` 的 7 个词（`lust`/`pride`/`wrath`/`envy`/
`gluttony`/`greed`/`sloth`）**永不翻译**（它们是数据值）。

**但如果目标是「独特的长串」**（整句英文、多词物品名），全局替换是安全的 —— 因为不会撞车。
判断标准：**这个串在 index 里出现次数 ≤ 5 且都是同一个含义**。

### §4.4 铁律四：改前先看基线

见 §2.2。**不要凭记忆**。

### §4.5 铁律五：改前先在 CDP 里打印真实源码

`String(setup.xxx)` / `SugarCube.macros.xxx` 的 `toString()`。**只读 index 会误判**。

### §4.6 铁律六：插入后立刻做结构校验

- JS 片段：`{`/`}` 数量相等、`(`/`)` 数量相等
- SugarCube 片段：`<<`/`>>` 配对
- **插入位置必须在正确的 widget 内**（§5.6 的教训）
- **用 Node 单元测试验证逻辑**（§2.4）

### §4.7 铁律七：注释语法

- **`/* ... */` 是 JS 注释，放进 passage 正文会原样显示给玩家**。
- passage 里用 `<!-- ... -->`。

### §4.8 铁律八：每轮都要跑回归

见 §6.1。**不跑回归就宣布完成 = 无效**。

---

## §5 事故台账（每一条都是真踩过的）

> 格式统一为：**现象 → 我一开始以为 → 实际根因 → 判据 → 修法 → 教训**

### §5.1 双转义事故 —— 0 passage / 白屏

**现象**：装上新包，打开纯白，`passage: 0`。

**我一开始以为**：源文件损坏。

**实际根因**：某个脚本对整个 `index.html` 做了 `html.escape()`。正文本来是转义的，
再转一次变 `&amp;lt;&amp;lt;if`，SugarCube 认不出来。

**判据**：`re.findall(r'<tw-passagedata[^>]*name="', raw)` 数量 < 10000。

**修法**：
1. 重写脚本，只对**要插入的片段**做 escape
2. 在脚本 + `rebuild2_fast.py` + `ZZ02` 三处加 passage 数安全阀

**教训**：**任何会写 index 的脚本，第一行就要有 passage 数安全阀。**

### §5.2 反引号判据误报 993 处

**现象**：断言 `no_tpl_glue` 报 993 处。

**我一开始以为**：991 处模板字符串被翻译破坏了。

**实际根因**：SugarCube 普通 passage 文本里的 `` `...` `` 是**内联文本**，不是 JS 模板字符串。
其中 `$var` 只匹配 `[A-Za-z0-9_.]`，所以 `$x.cn_name_cap中文` 是**完全正常**的写法。

**判据修正**：
- **只有 `<<script>>` / `<<run>>` 里的反引号**才是 JS 模板，需要 `${}`
- 逐步收紧：993 → 12 → 4 → **0（全是误报）**
- 最终改为「只查已知 3 个模式」

**教训**：**SugarCube 的语法和 JS 不一样。判据前先确认「这段代码在哪个上下文里执行」。**

### §5.3 `"lust"` 被误译 165 处

**现象**：`REGRESS` 报 `lust=165`（正常应 ≥150 带引号 / ≥3000 含属性访问）。

**我一开始以为**：翻译成功了。

**实际根因**：把 `"lust": "色欲"` 放进全局映射，`data.replace('"lust"', '"色欲"')` 命中
`$NPCList[].lust` 的数据字面量。

**判据**：`g.count('"lust"')` 应 ≥150，`g.count("lust")` 应 ≥3000。

**修法**：只在 `Template.add` 块内替换；`?sin` 的 7 个词永不翻译。

**教训**：**短单词（≤6 字符）如果不是「独特长串」，绝不全局替换。**

### §5.4 `applyClothingShopFilter` 少一个 `s`

**现象**：进服装店 `ReferenceError: applyClothingShopFilter is not defined`，整店崩。

**我一开始以为**：函数没定义。

**实际根因**：手写修复表时把 `applyClothingShopFilters`（真名，带 s）写成了 `applyClothingShopFilter`。

**判据**：`g.count("applyClothingShopFilters") == 4` 且 `g.count("applyClothingShopFilter(_items)") == 0`。

**教训**：**手写字符串修复表极易出错**。每条都要「改完之后立刻用 CDP/单元测试实测调用」。

### §5.5 `<<if>>` 里嵌宏 —— 社交界面崩溃

**现象**：
```
<<social>>: error within widget code
  (<<relation-box>>: errors within widget code
    (<<if>>: bad conditional expression: SyntaxError: Unexpected token '<<'))
```

**我一开始以为**：`relation-box` 的 `<<if>>` 写法有问题（查了两轮都说「0 处」）。

**实际根因**：早期脚本把 `_npcData.nam` 全局替换成 `<<NPC_CN_NAME _npcData.nam>>>>>>`，
结果在 `<<if>>` 表达式里也替换了：
```do
<<if (<<NPC_CN_NAME _npcData.nam>>>>>> is ("Ivory Wraith") ...>>
```

**两点错**：
1. **宏不能出现在 `<<if>>` 表达式里** —— 必须用函数调用 `setup.NPC_CN_NAME(...)`
2. **比较场景必须用英文原名** —— `_npcData.nam is "Ivory Wraith"`

**修法**：
```do
<!-- 比较：用英文原名 -->
<<if (_npcData.nam is "Ivory Wraith") or ($wraith.mimic is _npcData.nam and $wraith.revealed)>>

<!-- 显示：用函数调用 -->
<<print setup.NPC_CN_NAME(_npcData.nam)>>

<!-- widget 参数：直接传表达式 -->
<<npcrelationship setup.NPC_CN_NAME(_npcData.nam)>>
```

**判据**：`<<if>>` / `<<elseif>>` 的表达式（挖掉字符串后）里不含 `<<宏名`。

**自查脚本的三次翻车**（这段特别重要）：
1. ❌ `r"<<if\b([^<>]{0,500}?)>>"` —— `[^<>]` **匹配不到含 `<` 的内容** → 报「0 处」
2. ❌ `rest.find(">>")` —— 被字符串里的 `>>` 截断 → 引号不闭合 → 报「1 处」误报
3. ✅ 先挖字符串成等长空格，再找 `>>`

**教训**：**审计脚本报「0 处」时，先怀疑判据能不能匹配到目标。**

### §5.6 Forest Shop 崩溃 —— mod 服装缺 `slot`

**现象**：
```
[clothesIndex]: slot or valid object not provided
<<set>>: bad evaluation: TypeError: Cannot read properties of undefined (reading '0')
<<if>>: bad conditional expression: ... (reading 'iconFile')
<<printmoney>>: unable to parse ... getClothingCost(_item, $_realSlot)
```

**我一开始以为**：`clothingShopv2` 的 slot 逻辑坏了（第一次修在 `clothingShopv2` 加补全 → **无效**）。

**实际根因链**：
1. 原版 `generateshoppage` 用 `_item.slot` 判断真实栏位
2. **模组用 JS push 的服装常常漏了 `slot` 字段**
   （`dragonbreath`/`Queen of heart`/`Alice's dream`/`acorn`/`Suit for Adventurer`）
3. `$_realSlot = undefined` → `setup.clothes[undefined]` → `_itemData = undefined` → 整链 NPE

**为什么第一次修无效**：`Forest Shop` → `forestShop-main` → `AllShop` → `clothingShopv2` → `generateshoppage`，
**但另有路径直接进 `generateshoppage`**（日志 stack 里只有 `generateshoppage` 一层）。

**修法（最小侵入，在真正使用的那一行加兜底）**：
```do
<<set $_realSlot to ($clothingShopSlot is "all"
  ? (_item.slot
     || Object.keys(setup.clothes).find(_k => _k !== "all"
        && Array.isArray(setup.clothes[_k])
        && setup.clothes[_k].some(_x => _x && _x.index === _item.index))
     || "upper")
  : $clothingShopSlot)>>
```

**辅助线索**：日志里的 `Failed to load image img/clothes/upper/xxx` 直接告诉你真实 slot 是 `upper`。

**教训**：
1. **打补丁之前必须查调用链**（§2.3）
2. **补丁要打在「真正使用那个字段的那一行」**，不是入口
3. **CDP 超时就用 Node 单元测试**（§2.4）—— 12 个用例 1 秒跑完

### §5.7 `<<combatperson>>` 只用英文 `$description`

**现象**：战斗里 `broad男人`、`left手`、`right手`。

**我一开始以为**：`description_CN` 表缺词。

**实际根因**：
- `<<person>>` 用的是 `$description_CN || $description`
- **`<<combatperson>>` 只用了 `$description`**（4 处：直接输出、拼 role、拼"男人"、拼"女人"）

**修法**：全部改成 `($description_CN || $description)`。

**判据**：`combatperson` widget 里不应有裸 `$description`
（**除条件判断 `$description isnot "pale figure"` 外** —— 判断要用英文原名）。

**教训**：**同一个游戏里「显示 NPC 的 widget」可能有好几个，要全部检查。**

### §5.8 `Corrupted variables have been detected`

**这是存档问题，不是包的问题**。常见于：
- 旧存档里存了已不存在的变量
- 模组增删导致变量结构不一致

**处置**：告诉用户「先备份存档，再点重设」。**不要为它改包**。

**教训**：**看到这条先去问「你用的是不是旧存档」，不要一头扎进 index。**

### §5.9 `You _You` 与变量拆开

**现象 1**：`You _You坐在了...`

**根因**：`<<else>>\n\tYou\n<</if>>` —— 本该是 `<<set _You to "">>`，被翻译破坏成裸 `You`。

**修法**：改回 `<<set _You to "">>`，显示处用 `<<print _You>>`。

**现象 2**：`up your _lower.name. It 并缠绕在她的普通内裤上。`

**根因**：变量被拆成 `_lower.name` + `. It`，宏没闭合。

**修法**：恢复成完整表达式。

### §5.10 `description_CN` 被赋了英文 `title`

**现象**：NPC 名显示 `broad`（中文「宽硕的」在数组里明明有）。

**实际根因**：命名 NPC 走的是另一条路径：
```do
<<set $description to $NPCName[...].title>>       ← 英文
<<set $description_CN to $NPCName[...].title>>    ← 还是英文！没翻译
```

**修法**：
```do
<<set $description_CN to setup.NPC_CN_TITLE($NPCName[...].title) || $NPCName[...].title>>
```

**判据**：`description_CN to $xxx.title>>` 出现次数 = 0。

### §5.11 模组运行时覆写（`Npc Name CN` 案例）

**现象**：index 里 `BODYPARTS_CN_NAME` 修了 8 个版本，进游戏还是英文。

**实际根因**：模组 `npcNameCN.js` 的 `forceSetup()` 无条件
`st.BODYPARTS_CN_NAME = partCN`，`partCN(v) = tr(BODYPARTS, v)`，
而 `BODYPARTS` 只有 30 键（缺 `penis`/`vagina`/`anus`/`breasts`/`tongue`/`buttocks`）。

**修法**：改模组 ZIP 里的表（30 → 76 键），不是改 index。

**教训**：**多版本修不好的问题，先怀疑「我的修改被覆盖了」。**

### §5.12 审计脚本自身的错（第 N 次）

**这是最容易浪费轮次的一类**。完整清单：

| 错误 | 症状 | 修正 |
|---|---|---|
| `[^<>]` 匹配不到含 `<` 的内容 | 报「0 处」，实际有 | 用 `.*?` 或按行取 |
| `rest.find(">>")` 被字符串里的 `>>` 截断 | 引号不闭合 → 误报 | **先挖字符串成等长空格，再找 `>>`** |
| `<<br` 会匹配 `<<breasts` | 误报 | 用 `<<br\s*>>` |
| `>>>` 判据 | JS 位运算 `>>>` 误报 8152 处 | **只查已知形态**（`\<\<xxx>>\<\</if>>>` 这类） |
| `format()` 遇到 `{...}` | `IndexError` | 用 `%` 或 f-string 前先转义 |
| f-string 里有 `${...}` | `NameError` | 用 `%` 格式化 |
| PowerShell 吞反引号 / `$` | 脚本被改坏 | **用文件，不用 `-c @"..."@`** |
| `re.sub` 替换串含 `\` | 报错 | 用 lambda |
| 逐字符扫描 100MB | 卡死 | 按行扫描 |
| `shutil.copy2(src, src)` | `PermissionError` | 不要复制到自己 |
| 未闭合 `<<set ...{` 跨行 | 误报 742 处 | **跨行数组定义是合法的**，判据要按 `>>` 配对 |

**总纲：审计脚本报「不通过」时，先怀疑脚本，再怀疑数据。**

### §5.13 `_item.slot` vs `realSlot`

原版注释里提到计划给 `clothing.all` 的 clone 加 `realSlot` 属性，但**实际代码是
`setup.clothes[slot].forEach(c => clothes.push(c)); setup.clothes.all = clothes;`
—— 直接 push 原对象引用，没有 clone，也没有 `realSlot`**。

**教训：注释 ≠ 实现。以代码为准。**

### §5.14 `mk()` 包装函数的表是 `null`

`setup.update_cloth_cn` 是 `mk(null, function(s){...})` 形态 —— **表是 `null`，走 `extra` 回调**。
这是**设计如此**，不是坏了。改它的数据要改回调里的映射，不是改"表"。

### §5.15 `NPCTypeList_cn_name` 被赋值两次

**现象**：表格只有 63 项（应有 248）。

**实际根因**：`<<set>>` 出现两次，**后一次（605 字符）覆盖了前一次（2273 字符）**。

**修法**：合并两份，只保留一次赋值。
**判据**：`setup.NPCTypeList_cn_name to "` 出现次数 = **1**。

### §5.16 TweeReplacer 的空 `regexFlag`

**现象**：`[DoLSims] findRegex: <<widget "fallentransform">>...` 找不到。

**我一开始以为**：widget 名大小写不对（真实是 `fallenTransform` 驼峰）。

**实际根因**：补丁定义里有 `"regexFlag": ""`（空字符串）。
`TweeReplacer` 读到空字符串时日志打印 `regexFlag:undefined`，
`new RegExp(pattern, "")` 在某些实现下抛错 → 整条补丁失效。

**修法**：删掉这个空字段。

**教训**：**日志里的 `findRegex` 显示全小写，是打印处理，不代表匹配用的就是小写。**

> ⚠⚠ **第12轮订正（实测 TweeReplacer 1.7.0 源码第 19181 行）**：
> `all:true` 时 `regexFlag = p.regexFlag ?? 'g'`。空字符串 `""` **不会**回落成 `'g'`，
> 于是 `replaceAll(new RegExp(x, ""))` 抛 `TypeError`（非全局正则不能 replaceAll）—— 这才是「补丁失效」的真因。
> **删掉空 regexFlag 之前，必须先确认那条正则本身是对的**：第7轮删掉 Quoted Link Fix 的空 regexFlag 后，
> 它那条以未转义 `[[` 开头的正则（字符类！）开始真正生效，`all:true` 把 4 个 passage 里所有 `x]` 换成链接，
> 改坏了 `<<if>>` 代码和链接。**「报错让补丁失效」有时是在替你挡灾。** 见 §5.23。

### §5.17 `sets` / `calls` —— 先确认是不是在注释里

**现象**：扫到 `sets $estate_cards_end to` / `calls <<endevent>>` 等 27 处。

**我一开始以为**：宏名被翻译破坏了。

**实际根因**：**全在 `<!-- ... -->` 或 `/* ... */` 注释块里**，是原作者的伪代码笔记，**无害**。

**判据**：
```python
# 先判断这一行是否在注释块内
# 简单办法：看它前面最近的 <!-- 和 --> 谁更近
```

**教训**：**扫出「异常」之后，第一件事是确认它是不是在注释里。**

### §5.18 `<<link>>` 文本的引号形态

**现象**：写了个替换脚本，只改了 1 处（`DEBUG: Instagrow`），其余 29 条没动。

**我一开始以为**：文本是 `"Investigate the staircase"`（带引号）。

**实际形态**：`<<link [[Investigate the staircase|目标]]>>` —— **文本在 `[[...|` 里，无引号**。

**修法**：
```python
# 主形态
("[[" + en + "|", "[[" + cn + "|")
# 兼容转义
("[[" + en.replace("'", "\\'") + "|", "[[" + cn + "|")
# 也处理 <<link "文本">> 形态
('<<link "' + en + '"', '<<link "' + cn + '"')
```

**教训**：**写替换脚本前，先 `print` 一条真实样本，看清它的确切形态。**

### §5.19 `Template.add` 的名字被翻译

**现象**：`Template.add("欣赏着", () => either(...))` —— 原本是 `"admires"`。

**实际根因**：某个全局替换把 `"admires"` 当文本翻了。**模板名是标识符，翻了就调不到。**

**修法**：恢复 `"admires"`。

**判据**：`Template.add` 的名字**不能含中文**。

**注意**：基线共 13 个模板名：
`stroke` / `alongside` / `orgasmMoans` / `vulva` / `Vulva` / `animal` / `animals` /
`garden` / `admires` / `gwylanItem` / `sin` / `chatter1` / `chatter2`

### §5.20 `CafeFoodList_cn_name` 丢 9 词

**现象**：咖啡店部分食物名变英文。

**实际根因**：`<<set setup.CafeFoodList_cn_name to "..."` 出现**两次**：
- 第一次（163 字符 / 11 词）：`coffee,咖啡|fruity ale,果味艾尔酒|autumn ale,秋日艾尔酒|...`
- 第二次（162 字符 / 16 词）：`coffee,咖啡|tea,茶|hot chocolate,热巧克力|...`

**后者完全覆盖前者** → 丢了 9 个词（`fruity ale`/`shandy`/`autumn ale`/`winter ale`/
`fruit salad`/`pancakes`/`deluxe cream bun`/`crepes`/`gingerbread`）。

**修法**：**合并两份**（取并集，后面的优先），变成 25 词。

**判据**：赋值次数 = 1 且 ≥25 词。

**教训**：**同一个翻译表被赋值两次是这类游戏的通病（`NPCTypeList` 也犯过）。**
**扫描口径：所有 `<<set setup.XXX_cn_name to "..."`，出现 ≥2 次就要查。**

### §5.21 三重尖括号 `>>>`

**现象**：正文里莫名多一个 `>`。

**实际根因**：`<<if ...>><</if>>>` —— 末尾多一个 `>`。

**修法**：删掉多余的。

**判据**：只查**已知形态**（`>>><</` / `">>>"` 紧跟标签），
**不要用全局 `>>>` 统计**（JS 位运算 `x >>> 0` 会有 8000+ 处）。

### §5.22 `<<button>>` 与 `<<option>>` 的误报

**现象**：
- `<<button>>` 报 13 条英文 → 全是 `<span class='fa-icon fa-left'></span>`
- `<<option>>` 报 399 条 → 全是 `$demo.type` / `_outfitEditorFilter.type.normal` 这类变量引用

**修法**：`is_text()` 里排除 `$`/`<`/`<<`/`=>` 等代码符号。

---

> **§5.23 ~ §5.30 是第12轮（2026-11-20）新增。共同主题：静态检查全绿，运行时却是坏的。**
> 这一轮发现的 9 类问题里有 6 类**只在运行时可见** —— 详见 §2.5 与 §6.4。

### §5.23 Quoted Link Fix：把「不是死链」当死链修，修法还是字符类

**现象**：运行时 `Bully Toilets Fight Finish` 里出现
`$worn[slo[[继续|School Boy's Toilet[[继续|School Girl's Toilets]]].gender` 这种乱码。

**我一开始以为**：`[[继续|"School Boy's Toilets"]]` 带引号是死链（静态扫链接目标时 passage 不存在）。

**实际根因（两层）**：
1. **不是死链**：引擎 `Wikifier.helpers.evalPassageId` 对「不存在的目标」会当表达式求值，
   `"School Boy's Toilets"` → 字符串 `School Boy's Toilets` → 合法 passage。原版作者是故意这么写的。
2. 修复模组的 `findRegex` 写成 `[[(?:Next|继续)\|"…"]]` —— **开头未转义的 `[[` 是字符类**，
   能匹配任意一个字符后跟 `]`。原先空 `regexFlag` 让它抛错失效（§5.16 订正），第7轮删掉后 `all:true` 生效，
   4 个 passage 里所有 `t]` `s]` `"]` 都被换成了链接。

**修法**：撤下整个 Quoted Link Fix（恢复 vanilla 行为）。
**判据**：`E.no_quoted_link_fix` + `E.tr_regex_no_charclass_trap`（任何模组的 findRegex 不得以未转义 `[` 开头）。
**教训**：**「链接目标不存在」先查 evalPassageId**；**正则补丁先在 Node 里对目标 passage 跑一遍，看命中片段长什么样**（`AQ05_tr_audit.js`）。

### §5.24 passage 正文里的裸 `<` —— 浏览器吃掉 `</if>`

**现象**：社区 issue #582「荒原钓鱼遇袭 `cannot find a closing tag for macro <<if>>`」，我们的包也有。
静态 unescape 后看，`<</if>>` 好好的。

**实际根因**：`ZZ01_final_guard.py` 修 `<<</if>>` 时写成
`for a, b in ((H.escape(old), new), (old, new))` —— **转义形态的旧串被替换成了未转义的新串**，
裸 `<</if>>` 进了 `<tw-passagedata>`。浏览器 HTML 解析把 `</if>` 当成无主结束标签丢弃，
SugarCube 读 `textContent` 得到 `<>`。

**判据**：`C.no_raw_angle_in_passage` —— **查原始字节**：`<tw-passagedata>` 正文里不得出现任何 `<` `>`。
**教训**：**`html.unescape` 之后再查，永远看不见这类问题。** 替换对必须写成
`(H.escape(old), H.escape(new))`，两边同形态。

### §5.25 宏表达式里 `_x` 当箭头参数 / const 名

**现象**：服装店每件商品都报 `SyntaxError: Malformed arrow function parameter list`。

**实际根因**：引擎的 `Scripting.parse` 把表达式里**所有** `_name` 词元改写成 `State.temporary.name`，
`find(_k => _k !== "all")` 变成 `find(State.temporary.k => …)`；`for (const _sk of …)` 变成 `const State.temporary.sk`。
第10轮我自己写的 R10/R17 就是这样 —— 而当时的单元测试 `T02` 只做了 `$→_` 文本替换，`_k => …` 在 Node 里照样能跑。

**判据**：`C.sc_compile`（`T03_sc_compile_all.js`：**从 index 里抠出引擎自己的 `Scripting.parse`**，
对全部 19 万个宏表达式先 parse 再 `new Function` 编译）+ `C.no_tempvar_as_param`。
**教训**：**测 SugarCube 表达式，必须用引擎自己的 parse**，不要自己写 `is→===` 的近似转换。

### §5.26 ModI18N 运行时 JS 替换的位移失配

**现象**：成就描述 299 条只有 47 条是中文、提示 152 条只有 2 条中文；
同一批成就名被换成了我们的自译（官方「第一桶金」→「零钱」）。**静态看 `setup.feats` 根本没有描述的中文**，
于是第11轮我以为「描述/提示官方没翻」。

**实际根因**：ModI18N 在**运行时**按 `(文件名, pos)` 替换 JS，窗口只有 `pos-10 ~ pos+len+30`。
我们的静态翻译脚本（AC06 / AB06~AB13 / P05~T10）改了同一 JS 文件前部的文字长度，后面的官方条目全部错位失配。
黄金基线里这些描述在运行时是 299/299 中文。

**修法**：`AP01_bake_js_i18n.py` 在构建最早期（BE_bake 之后、任何改 JS 的脚本之前）
按 ModI18N 完全相同的算法把官方 JS 译文烘焙进 index；我们的自译只处理官方没覆盖的残余。
**判据**：`RT_GATE` G5（运行时成就 title/desc/hint 中文覆盖不低于基线）。
**教训**：**「静态没有中文」≠「玩家看到的是英文」。判断翻译覆盖率只认运行时（§2.1 第①层）。**
**改 JS 文本之前先问：ModI18N 有没有这个文件的条目？有的话你会把它后面的条目全部挤歪。**

### §5.27 显示值兼作逻辑值（社区 issue #583 一类）

**现象**：逃离地下农场时没有「亲吻半人马」选项。

**实际根因**：`<<livestock_horse>>` 的 `_text_output` 既用来显示、又被存进 `$remyEscapeSteed` 做判断；
汉化把显示值改成「半人马」，判断 `is "centaur"` 永远为假。同类：`_sydtext is "Sydney"` / `_text_output is "meat"` /
`_type is "harpy"` / `password[2] is "the blood moon"` / `$remyEscapeSteed is "stallion"`。

**修法（①保意图）**：判断改为中英都认（`is "centaur" or is "半人马"`），**不改显示文字**，新旧存档都兼容。
**扫描法**（`AH11_translated_logic.py`）：找 vanilla 里 `<<set X to "英文">>` 被汉化改成中文的变量，
再找当前包里拿 X（及其二跳赋值）与英文字面量比较的地方。

### §5.28 maplebirch 抢先改写 → 其它模组的锚点失配

**现象**：运行时日志 `[DomRobin] cannot find findString: <<if $robinpaid isnot 1>>` 等 4 条，静态 index 里锚点明明存在。

**实际根因**：maplebirch 5.6.2 的 zone 补丁先于 TweeReplacer 执行，把 `$money gte 300` 换成
`maplebirch.get("Finance").canPay(300, "cafe")`、给 robinpaid 条件追加 `and !…orphanage.robinFree`、
给 `fallenTransform` 外面包一层 `<<if not (…)>>`。DomRobin 只认旧 API（`VanillaPlus.finance`）。

**修法**：`AR02_maplebirch_compat.py` —— 锚点改成「不含 `>>` 的前缀」或在正则里加新 API 分支；
DoLSims 那条用 `$1` 保留 maplebirch 的外层开标签（否则它的 `<</if>>` 落单）。
**判据**：`RT_GATE` G2（ModLoader 日志里没有 TweeReplacer / zone 错误）。
**教训**：**静态 index 不是 TweeReplacer 看到的内容。** 锚点诊断要用运行时导出的 passage（§2.5）。
**另**：第11轮记的「Toilet Addon 4 条已知不可修」已过期 —— 那 4 个 passage 由枯木逢春等模组在运行时提供，补丁实际全部成功。

### §5.29 `<<npcrelationship>>` 传了中文名

**现象**：关系面板每个 NPC 的描述行都可能报「`<<npcrelationship>>`提供了错误的参数」；
maplebirch 日志 `[zone] 补丁 Widgets #2: unmatched`。

**实际根因**：第10轮修 relation-box 宏嵌套时，把参数换成了 `setup.NPC_CN_NAME(_npcData.nam)`，
而 `<<npcrelationship>>` 内部用 `V.NPCName.findIndex(i => i.nam === _args[0])` 查**英文原名**；
显示处又换成了 `<<print setup.NPC_CN_NAME(…)>>`，maplebirch 的 zone 正则只认 `\t<<NPC_CN_NAME _npcData.nam>>`。

**修法**：参数恢复 vanilla 的 `_npcData.nam`；显示处恢复 `<<NPC_CN_NAME _npcData.nam>>` 宏形态。
**教训**：**修 A 时把 B 的输入也改了。改任何 widget 的参数前，先打印该 widget 怎么用参数。**

### §5.30 模组自带 twee 的跨行字符串

**现象**：「对银海螺说话」(Silver Conch Talk) 永远没有对话内容。

**实际根因**：Wraith'sReflection 的 `<<set _chat.push("……\n<br><br>\n……")>>` —— 双引号字符串跨行，
`<<set>>` 交给 eval 时是 `SyntaxError`，`_chat` 永远是空数组。**模组源码自带的 bug**，与汉化无关。

**修法**：只在这几处字符串字面量内部把「换行+缩进」折叠成一个空格（文本、`<br>` 原样保留）。
**判据**：`E.mod_twee_compile`（T03 `--twee-dir` 扫全部模组 twee）。

> **§5.31 ~ §5.36 是第12/13轮补充。**

### §5.31 i18n 烘焙「替换第一处出现」造成的错位翻译

**现象**：运行时 166 段官方有译文却是英文；同时出现 `<<He>>含着 <<his>> hand up…`、`一个天使ic`、`unlockAvery鞠躬` 这类半英半中/标识符被译。

**实际根因**：旧 `BE_bake_i18n` 在 `pos` 精确比较失败后退回 `body.replace(f, t, 1)`。官方 i18n 有约 3.1 万条 `pos` 比原文偏 -1/-2
（ModI18N 自己按 ±2 容错），这些条目全走了兜底；原文在 passage 里重复出现时就替换到了别处，连带把同 passage 的长条目打断。

**修法**：`BE2_bake_i18n.py` 完全按 ModI18N 运行时算法（`tryReplaceStringFuzzyWithHintIndexComp`）定位：升序、±2、窗口 -10/+30、不重叠；失配只跳过该条。
**判据**：在 vanilla 上 190165 条全部命中、0 失配；运行时英文残留 182 段 → 20 段（`AU01_runtime_english.py`）。
**教训**：**烘焙/替换必须复刻消费方的定位算法**，不要自己发明「找不到就替换第一处」。

### §5.32 不看位置的全量替换把变量路径改坏

**现象**：社交面板显示「贝利>>」；`<<if _npcData.nam is "Ivory Wraith">>` 等被套上宏。

**实际根因**：`UB01_full_bake`（「先烤入再查漏补缺」）对每个 passage 把官方条目的 `f` **全部出现处**都换成 `t`。
官方有条目 `f="_npcData.nam"` → `t="<<NPC_CN_NAME _npcData.nam>>"`（译文包含原文），于是代码里的变量也被换、已换过的再套一层。

**修法**：`is_safe()` 加两条：`f` 是变量/属性路径（`_x.y` / `T.a.b`）不替换；`t` 包含 `f`（包裹式翻译）不替换。
**判据**：F 组 `_npcData.nam>>>>` / `<<NPC_CN_NAME <<` 为 0；RT_GATE G8（渲染文本无 `<<` `>>`）。

### §5.33 翻译表被二次赋值（§5.20 的同类，第13轮全量扫）

**现象**：角色名与正文不一致（Jordan 正文「约旦」520 处，名字处显示「乔丹」；River 瑞沃/里弗、Wren 伦恩/雷恩……）；
头衔表 businessperson / crimson hound 等变回英文。

**实际根因**：早期 `AD_direct_patch` 注入的临时表（`NPCNameList_cn_name` 412 字符、`NPCTitleList_cn_name` 605 字符）
排在官方表后面，覆盖了官方表（414 / 1072 字符）。§5.20 只给 `CafeFoodList` 和 `NPCTypeList` 写了断言，其它表漏查。

**修法**：`AW02_merge_dup_tables.py`：以官方表为准，临时表里官方没有的键追加；只保留一处赋值。
**判据**：`D.all_cn_tables_single`（**所有** `setup.*_cn_name` 只赋值一次）+ `D.npcname_official`。
**教训**：**§5.20 的扫描口径要做成断言覆盖全部表**，不要只写当时出事的那两张。

### §5.34 自建补丁模组遮蔽了官方映射表

**现象**：钓鱼开场「herring咬住了钩上的黑莓」——15 种鱼名全是英文，官方表里明明都有。

**实际根因**：`Npc Name CN` 1.3.0 起「强制接管」`setup.NPC_CN_TYPE/NAME/TITLE`，只查自己内置的小表（60 类 / 39 名），
官方 `NPCTypeList_cn_name`（248 类）被完全绕过。194 个类型键只靠 index 里的 EXTRA 兜底，没兜到的显示英文。

**修法**：`AW03` 把模组升到 1.4.0：「官方表 → 内置表 → 原样」，官方表按内容缓存；官方表的已知错译单独覆盖（`fish`→鱼，官方写成「海星」；`baitfish` 官方缺，取 foodstuff 的「饵鱼」）。同步更新模组 `version` 与 `description`。
**判据**：`E.npcnamecn_official_first`；RT_GATE G7（运行时 `NPC_CN_TYPE("herring")` = 鲱鱼，鱼名 0 个未翻）；Node 单测 `T06` 14/14。
**教训**：**「强制接管」类补丁必须把被接管方的数据源接过来**，否则就是用小表替换大表。

### §5.35 X05 全文件解实体 + 错误的「双重转义」断言

见第12轮报告第一节第 5 条。**判据口径**：`&amp;lt;` / `&amp;gt;` 逐 passage 与 vanilla 相等（`C.no_double_escape` 已改），
不是「全文件为 0」——原版源码里本来就有合法的 `&lt;`。

### §5.36 签名口令随脚本副本进了公开仓库（GitGuardian 告警）

**现象**：GitGuardian 报 `Keystore Password exposed`（仓库 `DoL-Lyra-ModFixes`）。

**实际根因**：`build.py` 等脚本里写死了 `--ksPass` / `--ksKeyPass` 的口令，脚本副本被复制进 `repo\docs\`；模板正文也写了口令。
`.jks` 文件本身从未入库（`git log --all` 核实），所以光有口令签不了包。

**修法**：`build.py` 改读环境变量 `DOL_KS_PASS`，否则读本机 `work\keystore.local`（不入库、不复制进 repo）；
仓库与模板里的明文全部替换成占位符（`AX01_secret_scan.py --redact`）。用户选择不改写 git 历史、不更换密钥（更换会导致无法覆盖安装、存档丢失）。
**判据**：**每次往 repo 提交前跑 `python AX01_secret_scan.py E:\TAML\_dol\repo`，非 0 不许提交。**
**教训**：脚本里不写任何口令 / token；复制脚本进公开仓库前必须过密钥扫描。

---

### §2.5（补）运行时导出 —— 第12轮起的标准诊断入口

`cdp_suite.js` 的 `dump` 步骤把**运行时**全部 passage / widget / init / script 原文导出成 jsonl
（`Story.lookupWith` + `getAllWidget` + `getAllInit` + `getAllScript`；注意 `lookupWith` **不含 widget**）。
`AK01_runtime_to_html.py` 把它拼回伪 index，于是 T03 / `scan_lib.struct_regressions` 等静态工具都能直接查运行时内容。
`AK03_runtime_diff.py` 对比「静态 → 运行时」被哪些机制改写过。

---

## §6 验收标准

### §6.1 静态回归（`REGRESS_ALL.py`，60 项）

| 组 | 内容 | 项数 |
|---|---|---|
| A | 安装前提 | 4 |
| B | 内容完整性 | 5 |
| C | 代码卫生（含 `no_macro_in_if`） | 5 |
| D | 翻译表（含 `no_cn_template_name` / `cafefood_merged`） | 10 |
| E | 模组 | 4 |
| F | 历史修复防复发 | 32 |

**跑法**：`python REGRESS_ALL.py`，**退出码 0 才算过**。
**第12轮起 `build.py` 改为「先验后发」**：签名后依次跑 REGRESS_ALL → validate → exec_verify → RT_GATE，
**任何一项失败都不归档、不覆盖 out/**（旧流程先覆盖 out/ 再跑回归，失败只告警 —— 坏包照样被部署）。
第12轮新增断言：`C.sc_compile` / `C.no_tempvar_as_param` / `C.struct_vs_vanilla`（**对照 vanilla，不是汉化基线**）/
`C.no_raw_angle_in_passage` / `E.mod_twee_compile` / `E.tr_regex_no_charclass_trap` / `E.no_quoted_link_fix` /
F 组 10 条（#579/#583 同类、`<<case "nobody">>`、Wraith 台词转义、npcrelationship 中文参数）。

### §6.4 运行时验证门 `RT_GATE.py`（第12轮新增，构建必过）

| 项 | 判据 |
|---|---|
| G1 | 页面就绪 |
| G2 | ModLoader 日志无 TweeReplacer / zone 补丁错误 |
| G3 | **运行时**全部 passage+widget 宏表达式经引擎 parse 后可编译 |
| G4 | **运行时**宏结构不比 vanilla 多出错误 |
| G5 | 运行时成就 title/desc/hint 中文覆盖不低于黄金基线 |
| G6 | 新档开局（Start2 → 孤儿院 → 卧室）、社交面板、服装店、森林商店、钓鱼、#582/#583/#584 现场等零红字 |
| G7 | （第13轮）运行时查名函数走官方映射表：`NPC_CN_TYPE("herring")`=鲱鱼 等，鱼名 0 个未翻 |
| G8 | （第13轮）测试步骤渲染出的文字里没有 `<<` / `>>` 残留（「贝利>>」这类） |
| G9 | （第13轮）RT_GATE 解出 APK 的 `assets/www` 交给 `cdp_suite` 提供（`DOL_WWW`），测试流程中请求的静态资源无 404（原版也没有的 `modList.json` / `style.css` / `usettings.js` 除外） |

**`cdp_suite.js` 会数页面里 `.error` 元素** —— SugarCube 的宏错误是渲染进页面的，不抛异常；
旧 `cdp_flow.js` 只收 `exceptionThrown` / `console.error`，所以「10 步 0 错误」看不见红字。
**直接 `Engine.play` 某个中途 passage 前要先 `play("Start2")`**，否则 `$shopDefaults` 等新档变量不存在，会冒出探针自己造成的红字。

### §6.2 CDP / 单元测试

| 测试 | 期望 | 备注 |
|---|---|---|
| `cdp_flow.js` | 10 步全 0 错误 | 100MB 加载 ~250 秒 |
| `cdp_passages2.js` | 40+ passage，只有 `Tutorial` 有噪音 | — |
| `probe_full.js` | 5 个 `setup` 函数实调返回中文 | — |
| `T02_slot_unit_test2.js` | 12/12 通过 | **不需要 CDP，1 秒跑完** |

### §6.3 交付前三查

1. **SHA256** 与构建输出一致
2. **arsc STORED** + **testzip 通过**
3. **passage 16088（基线）/ 16089（当前）/ widget 5104**

**另外**：告诉用户「装新包前核对 SHA256」，因为**很多问题其实是旧包导致的**。

---

## §7 轮次与交付

### §7.1 每轮固定动作

```
1. 跑 REGRESS_ALL.py（确认起点干净）
2. 扫一个维度（§3 里挑一类）
3. 发现 → 定位（§2.1 五层）→ 修（幂等脚本 + 接入 build_all）
4. 重建
5. 再跑 REGRESS_ALL.py
6. CDP / 单元测试抽查
7. 写报告 → 推 GitHub
```

> **每轮开工前先过一遍 §0.4 / §0.5**：这一轮有哪些活属于翻译、批量统计、日志归类、
> 重复代码生成？能外派的先派出去并行跑，主模型只做判断与验收，别自己一条条干。

### §7.2 报告要求

每轮至少产出：
- 修了什么（现象 / 根因 / 修法 / 判据）
- 没修什么，为什么
- **扫过但确认干净的维度**（这很重要，证明覆盖面）
- 新出现的风险

### §7.3 GitHub

- 仓库：`1579486875/DoL-Lyra-ModFixes`（**公开仓库**）
- 本地：`E:\TAML\_dol\repo`
- `docs\` 放报告 + 关键脚本
- **提交前必跑** `python E:\TAML\_dol\work\AX01_secret_scan.py E:\TAML\_dol\repo`（非 0 不许提交，见 §5.36）；
  提交身份沿用历史提交的 `GNH <1579486875@qq.com>`（用 `git -c user.name=… -c user.email=…`，不改全局配置）

### §7.4 关于「更新模组描述和工坊简介」

DoL-Lyra 是 **APK 分发**，不是 Steam 工坊。对应的「描述」是：
- `repo\README.md` 的版本说明
- `repo\docs\` 里的报告
- 打包时归档文件名里的说明（`build.py` 的第二个参数）

**每次有功能变化，这三处都要同步。**

---

## 附录 A 常见日志文本 → 根因对照表

| 日志文本 | 根因 | 去哪 |
|---|---|---|
| `macro <<xxx>> does not exist` | 宏名被翻译破坏 / `<<if>>` 里嵌宏 | §5.5 |
| `Unexpected token '<<'` | 同上 | §5.5 |
| `ReferenceError: xxx is not defined` | 函数名改错（多为少字母） | §5.4 |
| `slot or valid object not provided` | 物品缺 `slot` 字段 | §5.6 |
| `reading '0'`（在商店） | 同上，或数组越界 | §5.6 |
| `reading 'iconFile'` / `'accIcon'` / `'detailIcon'` | `_itemData` 是 undefined | §5.6 |
| `reading 'reduce'` | 同上 | §5.6 |
| `reading 'desc'` | 过滤菜单数据源为空 | — |
| `Corrupted variables` | **存档损坏，不是包的问题** | §5.8 |
| `Failed to load image` | 资源缺失；**也是 slot 的线索** | §5.6 |
| `do_patch() cannot find findString` | TweeReplacer 锚点不匹配 | §3.10 |
| `regexFlag: undefined` | 补丁里 `"regexFlag": ""` | §5.16 |
| `ApplyPatches` / `PatchOperation` 报错 | XML 补丁顺序 / 异常被吞 | — |

## 附录 B 脚本命名规范

| 前缀 | 含义 |
|---|---|
| `A*`~`P*` | 历次审查轮次的脚本（按时间） |
| `R*`/`Q*`/`T*` | 第 10 轮（R=诊断，Q=relation-box，T=模板/英文） |
| `ZZ01_final_guard` | 最终守门（11 类检查）—— 第12轮修了它自己的「转义旧串换成未转义新串」 |
| `TF01_nest_guard` | **必须永远最后** |
| `REGRESS_ALL` | 回归套件（第12轮约 85 项） |
| `RT_GATE` | **运行时验证门**（第12轮新增，构建必过） |
| `scan_lib.py` / `modzip_lib.py` | 宏边界切分 / 结构对照 vanilla / 改模组 ZIP 的公共库（第12轮新增） |
| `T03_sc_compile_all.js` | 用引擎自己的 `Scripting.parse` 编译全部宏表达式（`--twee-dir` 可扫模组 twee） |
| `cdp_suite.js` + `plan_*.json` | 一次加载、多步检查、**数页面红字**、可导出运行时 passage |
| `AP01_bake_js_i18n` | 官方 JS 译文烘焙（必须在任何改 JS 文本的脚本之前） |
| `probe_*.js` | CDP 探针 |
| `cdp_*.js` | CDP 测试器 |
| `T*_unit_test*.js` | Node 单元测试（不需要 CDP） |

## 附录 C 关键常量速查

```
基线 passage     16088   （当前 16089 = 基线 + 我新建的 Widgets Repair）
基线 widget      5104
模组条目         57（第12轮撤下 Quoted Link Fix：56 个 ZIP 模组 + 1 个枯木逢春 modpack）
NPCTypeList      248 条（只赋值 1 次）
EXTRA 表         ≥155 键
Npc Name CN      76 键（BODYPARTS）
CafeFoodList     25 词（只赋值 1 次）
Template.add     13 个名字，不含中文
ModI18N          1.0.1a（与社区 Eltirosto 发布版逐字节一致）；JS 条目 7853，在 vanilla 上 7853/7853 全部可命中
运行时 passage   约 17992（含 widget/init/script；静态 16089）
运行时成就中文   基线 title 298/299 · desc 299/299 · hint 152/152
arsc             STORED
签名             SHA256withRSA
```

## 附录 D 一句话清单（打印出来贴在屏幕上）

1. **改前 diff 基线**，不要凭印象
2. **改前先 CDP 打印真实源码**，不要只读 index
3. **打补丁前查调用链**，补丁打在「真正使用的那一行」
4. **修复必须幂等 + 接入 build_all**
5. **短单词不全局替换**；独特长串可以
6. **做完立刻验证**（单元测试 / CDP）
7. **每轮跑回归**，不跑等于没做
8. **审计脚本报错先怀疑脚本**
9. **扫出异常先确认是不是在注释里**
10. **注释用 `<!-- -->`，不用 `/* */`**
11. **玩家看到的是运行时**：翻译覆盖率、补丁是否命中、结构是否正确，一律以运行时导出为准（§2.5）
12. **结构判据对照 vanilla 英文原版**，不对照汉化基线 ——「与基线相同」只说明问题来自汉化包，不说明无害
13. **测 SugarCube 表达式用引擎自己的 `Scripting.parse`**（T03），`_x` 不能当箭头参数
14. **查原始字节**：passage 正文不得有裸 `<` `>`；替换对两边同为转义形态
15. **「死链」先查 `evalPassageId`**；正则补丁先在 Node 里看命中片段
16. **构建先验后发**：REGRESS / validate / exec_verify / RT_GATE 任何一项失败都不部署
17. **烘焙/替换复刻消费方算法**；不看位置的全量替换必须排除变量路径和「译文包含原文」的条目
18. **所有翻译表只赋值一次**；「强制接管」类补丁要接管对方的数据源
19. **脚本里不写口令**；往 repo 提交前跑 `AX01_secret_scan.py`
