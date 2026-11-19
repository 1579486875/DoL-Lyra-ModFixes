# -*- coding: utf-8 -*-
import os
import shutil
import subprocess

REPO = r"E:\TAML\_dol\repo"
WORK = r"E:\TAML\_dol\work"

for f in ("AAA01_script_syntax.py", "AAB01_big_script.py", "AAC01_setup_scope.py",
          "AAD01_fix_setup_guard.py", "AAE01_fix_selfassign.py", "AAF01_verify.py",
          "AAG01_remaining.py", "AAH01_fix_all.py", "AAI01_wire_beast.py",
          "AAJ01_fix_table.py", "AAK01_verify_final.py",
          "build.py", "build_all.py", "validate.py", "regress.py"):
    src = os.path.join(WORK, f)
    dst = os.path.join(REPO, "docs", f)
    if os.path.exists(src):
        shutil.copy2(src, dst)

p = os.path.join(REPO, "README.md")
s = open(p, encoding="utf-8").read()

ADD = """
## 第二十七轮（紧急修复：`<<script>>` 守卫写错，5 个模块全部失效）

用户实测报了大量红字，全部指向同一个根因。

### 根因：`SugarCube.setup` 不存在

我写的守卫：

```javascript
if (!window.SugarCube || !SugarCube.setup) return;   // ← 恒为真
var st = SugarCube.setup;
```

**SugarCube 2 的 `setup` 是 `window.setup`，不是 `SugarCube.setup`。**

证据：vanilla 里 `SugarCube.setup` 只出现在**注释**里（`/*Can be found at 'SugarCube.setup'*/`），
而真正定义 setup 函数用的是**裸 `setup.xxx = function`**（`setup.guessColourInMap` 等 3 处）。

**后果**：5 个 `<<script>>` 块**全部在第一行就 return**，导致：

| 失效的 | 症状 |
|---|---|
| `setup.description_CN` | 孤儿院开场/医院/回家路上全部红字 |
| `setup.NPC_CN_TOOLNAME` | 教程战斗红字 |
| `setup.NPC_CN_TYPE` | **`lizard` / `eels` / `whale` 夹在中文里** |
| `setup.NPC_CN_NAME` | NPC 名不翻译 |
| `setup.CAFE_FOOD_CN` / `DirectionCN` / ... | 同类 |

**修法**：

```javascript
var st = (typeof setup !== "undefined" && setup) ? setup
       : (window.setup || (window.SugarCube && window.SugarCube.setup));
if (!st) return;
```

**顺带修掉**第二个 bug：替换时产生 `var st = st;` 自赋值（hoisting 后为 undefined），已删 3 处。

### 修掉的其它问题

| 问题 | 说明 |
|---|---|
| `<<= setup.colourName（<<= ... >>）?...>>` | 全角括号 `（` `）` + 双层嵌套 → Wardrobe 报 `Invalid or unexpected token`。已折叠为单层 + 半角括号 |
| `left手` | `left hand` 被翻一半 |
| `Ass and legs.` | 未翻 |
| `eels` / `whales` / `lizards` / `slimes` / `worms` | `NPCTypeList_cn_name` 缺复数形式，已补 5 项 |

### 查证后**不是** bug 的

| 现象 | 结论 |
|---|---|
| `Makeup`（52 次） | **全是 CSS 注释 / JSDoc 类型名**（`MakeupOptions` / `defaultMakeup()`），不是 UI 文本 |
| `<<= <<=` 2 处 | ①`a <<= 6` 是 zip.js 位运算 ②字符串内嵌 `<<= either(...)>>`，都合法 |
| `<<if (<<NPC_CN_NAME ...>> is ...)` | SugarCube 合法语法 |
| `rngWraith`/`wPersist`/`wHunt` | **定义都在**（各 1 个，与 vanilla 一致），报错来自旧包 |

### 关于「英语单词夹中文」

`lizard`/`eels`/`whale` 不是静态文本，而是 **`<<beasttype>>` 的输出**：

```do
<<widget "beasttype">>
  <<set _text_output to setup.NPC_CN_TYPE($NPCList[_na].type)>>
  <<print _text_output>>
<</widget>>
```

`setup.NPC_CN_TYPE` 一旦失效就回落到英文原值。**守卫修好后自动中文化。**

### 教训

**这是「改 A 打坏 B」的第八次，也是最隐蔽的一次**：
静态检查（`validate.py` 20/20、`regress.py` 几乎全过）全部通过，
因为**语法是对的**——错的是**语义**（`SugarCube.setup` 永远不存在）。

**以后写 `<<script>>` 必须遵守**：不要在 script 里用 `SugarCube.xxx` 判断，
SugarCube 注入的全局对象直接裸用（`setup` / `State` / `variables` / `T` / `C`）。
"""

if ADD.strip() not in s:
    s = s.rstrip() + "\n" + ADD
    open(p, "w", encoding="utf-8").write(s)
    print("README 已追加")

os.chdir(REPO)
subprocess.run(["git", "add", "-A"], check=False)
subprocess.run(["git", "-c", "user.name=GNH", "-c", "user.email=1579486875@qq.com",
                "commit", "-m",
                "hotfix: <<script>> 守卫误用 SugarCube.setup（恒为真）导致 5 个模块全部失效 + Wardrobe 全角括号"],
               check=False)
r = subprocess.run(["git", "push", "origin", "HEAD"], capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
print((r.stdout or "")[-300:])
print((r.stderr or "")[-300:])
