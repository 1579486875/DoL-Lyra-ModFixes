# 第 26 轮报告 —— TaskDanger 修复 + 遗留项裁定

**日期**：2026-11-23 17:56
**产出**：`out\DoL-Lyra-0.5.12.13-CHS-modded.apk`
**SHA256**：`35C5B55BDD041D5E97A2D945077815FE6ECBD4BFFC3546CF5C77CECABA54B91A`
**模组数**：65

---

## 一、TaskDanger 报错：真问题，已修

### 根因

**SmartPhone Alpha 模组混用了两套变量体系**：

| 体系 | 初始化 | 读取 |
|---|---|---|
| JS：`V.Phone` | `V.Phone = V.Phone || {}`（smartphone-patch.js）✅ | `V.Phone.TaskDanger` |
| SugarCube：`$Phone` | **从未初始化** ❌ | `<<if $Phone.TaskDanger is 1>>` |

模组的 ReplacePatcher 补丁把 `<<if $Phone.TaskDanger is 1>>` 注入到多个 passage（`Widgets Journal`、`Events Street`、多处 `<<effects>>` 后），而 **`$Phone` 这个 SugarCube 变量从未初始化** —— 读 `$Phone.TaskDanger` 就抛：

```
TypeError: Cannot read properties of undefined (reading 'TaskDanger')
```

**报错链里的 `attitudes → othersFeelings → sexDefaults` 只是 SugarCube 的嵌套 widget 错误上报路径，真正炸的是被注入到这些页面的 `$Phone` 读取。**

### 修复（两层）

**① 全局初始化**（新游戏，`Widgets variablesStatic`）：

```twee
<<if $Phone is undefined>><<set $Phone to {}>><</if>>
<<if $Phone.TaskDanger is undefined>><<set $Phone.TaskDanger to 0>><</if>>
<<if $Phone.Task is undefined>><<set $Phone.Task to 0>><</if>>
<<if $Phone.TaskRun is undefined>><<set $Phone.TaskRun to 0>><</if>>
```

**② 读取守卫**（旧存档兼容，改 SmartPhone 的 boot.json 补丁）：

```twee
<<if $Phone.TaskDanger is 1>>  →  <<if ($Phone and $Phone.TaskDanger is 1)>>
($Phone.Owned and ...)          →  ($Phone and $Phone.Owned and ...)
currentValue : $Phone.photography  →  currentValue : ($Phone ? $Phone.photography : 0)
```

**复查**：`$Phone.TaskTemp` / `$Phone.TaskRun` 的裸读都在已守卫的 `<<if ($Phone and $Phone.TaskDanger is 1)>>` 内部，安全。

---

## 二、Toilet Addon「PASSAGE_MISSING」：误报，功能正常

静态审计报 4 个 passage 缺失，但**运行时验证**：

| 场景 | 存在 | 解手选项 |
|---|---|---|
| Inn Bathroom | ✅ | 小便+大便 |
| Inn Bath | ✅ | 小便+大便 |
| Flats Own Shower | ✅ | 小便+大便 |
| Deadwood Reblooms Property Bathroom | ✅ | 小便+大便（Story 文本内，房产条件满足时显示） |

**结论**：这 4 个 passage 由模组**动态创建**（TweeReplacer 语义），静态 index 里当然没有。运行时 G2 = 0 且功能齐全，**不用修**。

（之前一次探针显示 Deadwood 0 解手，是因为探针没满足「拥有房产」条件，走了「返回房产中介」分支——不是补丁失效。）

---

## 三、DomRobin「FIND_MISSING」：误报，功能正常

`Robin Hug Cry` 是**链式补丁**（第一步把 `gte 5` 改成 `gte 2`，第二步再匹配 `gte 2` 删除），静态逐条比对必报一条失配，但运行时 G2 = 0，补丁按顺序执行，功能正常。

---

## 四、验证

| 项 | 结果 |
|---|---|
| `REGRESS_ALL` | **98 / 98** |
| `validate` | **22 / 22** |
| `RT_GATE` G1–G9 | **全过**（就绪 84 秒，G2 = 0，G9 = 0） |

---

## 五、遗留项最终清单

| 项 | 性质 | 处置 |
|---|---|---|
| `img/sex/*/active/` 缺图 | 原版未打包可选图层 | 无法修（无素材来源），不影响逻辑 |
| Toilet Addon 4 个 PASSAGE_MISSING | 模组动态创建 passage | 不用修 |
| DomRobin 链式补丁失配 | 链式补丁正常现象 | 不用修 |
| `Fishing Moor Hiker Molestation Finish` no usable links | 探针副作用 | 不用修 |

**至此，除原版缺图层外，其余已知问题全部修复或裁定为非缺陷。**

*报告：汐蓝（DeepSeek）*
