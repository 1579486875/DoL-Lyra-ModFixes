# 第 15 轮补充 —— Remy Love 汉化结论：模组与中文版不兼容，已移除

**日期**：2026-11-22 21:40
**产出**：`out\DoL-Lyra-0.5.12.13-CHS-modded.apk`
**SHA256**：`D9F6843F5B71324A0B0C88C09CE6296DA4892426FD20DF3C424C5773FDD1B004`（与 t22 字节级一致）
**模组数**：65（Remy Love 已移除）

---

## 一、汉化完成情况

`game/base-combat/actions-text.twee` 的玩家可见文本已**全部汉化**：

| 项 | 数值 |
|---|---|
| 原文文本行 | 1,123 |
| 去重唯一句子 | **795** |
| 已译 | **795（100%）** |
| 缺 / 多 | **0 / 0** |
| 单独 twee 编译 | **失败 0**（1,612 宏） |

产物：`_remy_actions_text_zh.twee`（185 KB，全中文动作描述）。

---

## 二、加入后暴露的兼容性问题

把汉化后的 Remy Love 打进包后，RT_GATE 报两类错误：

### 2.1 G2：38 条补丁全部失配

```
[Remy Love Mod] findString:[<<elseif random(1,10) is 10 and $NPCList[_n].penis isnot "che...
[Remy Love Mod] findString:[T.importantNpcOrder = ["Robin", "Whitney", "Eden", "Kylar"...
[Remy Love Mod] findString:[text: "罗宾依赖着你，你需要坚强起来。额外增加每天的创伤恢复"...
[Remy Love Mod] findString:[<<set _npc = ["None","Robin","Whitney","Kylar","Sydney","Ede...
```

**根因**：Remy Love 的所有 TweeReplacer `findString` 都是针对**英文原版**写的，而我们的 index 是**中文汉化版**，字符串对不上，38 条补丁**全部失配**。

### 2.2 G4：宏结构被破坏

```
('Canteen', ['cannot find a closing tag for macro <<if>> @441'])
('Livestock Lactate', ['orphan closing tag <</if>> @2548'])
```

Remy Love 的部分补丁在失配后仍执行了部分替换，导致 `Canteen` 与 `Livestock Lactate` 的 `<<if>>` 结构错位。

---

## 三、处置

**移除 Remy Love**，恢复到不含它的状态。

移除后 index 与 t22 **字节级一致**（SHA256 `D9F6843F…`），t22 的 G1–G9 全过结论直接适用。

**汉化成果保留**：

| 文件 | 用途 |
|---|---|
| `_remy_texts.json` / `_remy_batch_*.json` | 795 条原文 |
| `_remy_zh_*.json` | 795 条译文 |
| `_remy_actions_text_zh.twee` | 完整汉化 twee |

等 Remy Love 出**中文兼容版**（或作者更新 `findString`）时，可直接复用这份译文。

---

## 四、结论

- **汉化本身是成功的**：795 条 100% 覆盖、twee 编译零失败。
- **模组本身与中文版不兼容**：38 条补丁全失配 + 破坏 2 个 passage 的宏结构。
- **不是汉化造成的问题** —— 未汉化的原版加进去同样会失配（`findString` 对的是英文）。

*报告：汐蓝（DeepSeek）*
