# Degrees of Lewdity 模组化 APK —— 全面审查与修复（专用提示词模板 v1.1）

> **⚖ 最高准则（凌驾全篇）—— 修复都要建立在「尽量不破坏原有功能及其功能意图」的基础上。**
> 凡是靠「拿掉作者做进去的功能」去换日志安静的改法，一律降级为备选，并逐字写明牺牲了什么；
> 实在没有保意图的路可走，再另做打算 —— 但那时必须单列成「需要拍板」，不许自己悄悄决定。
> 判据与分级见 **§0.2**。

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
| `regexFlag: undefined` | 补丁里写了 `"regexFlag": ""`（空字符串） | **§5.16** |
| `sets $x to` / `calls <<x>>` **出现在正文** | 宏被破坏；**但先确认它是不是在注释里** | **§5.17** |

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
| 模组数量 | ≥58 | 58 |
| 每个 mod ZIP 完整 | 逐个 `testzip()` | 0 损坏 |
| `Npc Name CN` 的 `BODYPARTS` | **≥70 键** | 76 |
| TweeReplacer 补丁的 `regexFlag` | **不能是空字符串** | 0 处空 |
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
  - `[DomRobin] findString: <<if $robinpaid isnot 1...>>` → 锚点在，是旧包问题

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
total = 0
for old, new in FIXES:
    for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
        if a in data:
            c = data.count(a)
            data = data.replace(a, b)
            total += c
            break

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
**已接进 `build.py` 第 7.5 步**，每次构建自动跑。

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

### §7.2 报告要求

每轮至少产出：
- 修了什么（现象 / 根因 / 修法 / 判据）
- 没修什么，为什么
- **扫过但确认干净的维度**（这很重要，证明覆盖面）
- 新出现的风险

### §7.3 GitHub

- 仓库：`1579486875/DoL-Lyra-ModFixes`
- 本地：`E:\TAML\_dol\repo`
- `docs\` 放报告 + 关键脚本

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
| `ZZ01_final_guard` | 最终守门（11 类检查） |
| `TF01_nest_guard` | **必须永远最后** |
| `REGRESS_ALL` | 60 项回归套件 |
| `probe_*.js` | CDP 探针 |
| `cdp_*.js` | CDP 测试器 |
| `T*_unit_test*.js` | Node 单元测试（不需要 CDP） |

## 附录 C 关键常量速查

```
基线 passage     16088   （当前 16089 = 基线 + 我新建的 Widgets Repair）
基线 widget      5104
模组数量         ≥58
NPCTypeList      248 条（只赋值 1 次）
EXTRA 表         ≥155 键
Npc Name CN      76 键（BODYPARTS）
CafeFoodList     25 词（只赋值 1 次）
Template.add     13 个名字，不含中文
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
