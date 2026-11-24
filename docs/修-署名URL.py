# -*- coding: utf-8 -*-
"""修正：GitHub URL 恢复裸号 + 美化修正的 LICENSE 内容改正。"""
import os
import re

SIGN = "大赢经直插白皮赢道（1579486875）"

# ============ 1. 恢复被改坏的 GitHub URL ============
FILES = [
    r"E:\TAML\_dol\repos\DoL-Lyra-ModFixes\声明与许可.md",
    r"E:\TAML\_dol\work\联动模组\系统联动补全\LICENSE.md",
    r"E:\TAML\_dol\work\_mods\44_美化修正\LICENSE.md",
    r"E:\TAML\_dol\work\加-整合包声明.py",
]

BAD = "github.com/" + SIGN
GOOD = "github.com/1579486875"

for p in FILES:
    if not os.path.exists(p):
        continue
    t = open(p, encoding="utf-8").read()
    if BAD in t:
        t = t.replace(BAD, GOOD)
        open(p, "w", encoding="utf-8").write(t)
        print("✅ 修复 URL:", os.path.basename(p))

# ============ 2. 美化修正的 LICENSE 内容改正 ============
BEAUTY_LIC = r"E:\TAML\_dol\work\_mods\44_美化修正\LICENSE.md"

CONTENT = """# 美化修正 · 声明与许可

## 本模组的许可

本模组（`美化修正` / Beauty Fixer）由 **{sign}** 原创，采用
**CC BY-NC-SA 4.0**（知识共享 署名—非商业性使用—相同方式共享 4.0 国际）。

- 许可全文：<https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode>

**你可以**：自由使用、修改、分发，**条件是**：
1. 署名原作者；
2. **不得用于商业目的**；
3. 修改后的作品必须使用**同样的许可**发布。

## 本模组做什么

`美化修正` 是一个**图片覆盖工具**，用于调整美化资源与游戏服装的对齐问题。

它提供：
- 一个侧栏入口（`StoryCaption` 里的「美化修正」按钮）
- 一个可视化编辑器，可以对 `img/clothes/`、`img/face/`、`img/hair/` 下的素材做
  位移、缩放、局部变形
- 修改结果存在浏览器本地（IndexedDB），**不改动游戏原始文件**

## 上游致谢

| 组件 | 作者 | 许可 |
|---|---|---|
| **Degrees of Lewdity** | **Vrelnir** | CC BY-NC-SA 4.0 |
| SugarCube 2 | Thomas Michael Edwards | BSD 3-Clause |
| ModLoader | Lyoko-Jeremie | 见原仓库 |
| TweeReplacer | — | 见原模组 |

**Degrees of Lewdity** 版权归 **Vrelnir** 所有。
- 博客：<https://vrelnir.blogspot.com>
- 源码：<https://gitgud.io/Vrelnir/degrees-of-lewdity>

## 免责

本模组按"现状"提供，不附带任何担保。使用本模组产生的任何后果由使用者自行承担。

本模组**仅限 18 岁以上成年人使用**。

## 联系

问题反馈：<https://github.com/1579486875/DoL-Lyra-ModFixes/issues>
""".replace("{sign}", SIGN)

open(BEAUTY_LIC, "w", encoding="utf-8").write(CONTENT)
print("✅ 重写 美化修正/LICENSE.md")

# ============ 3. 校验 ============
print("\n=== 校验 ===")
for p in FILES:
    if not os.path.exists(p):
        continue
    t = open(p, encoding="utf-8").read()
    bad = t.count("github.com/" + SIGN)
    good = t.count(SIGN)
    print("%-30s 完整署名 %d 处 | 坏URL %d 处" % (os.path.basename(p), good, bad))

print()
t = open(BEAUTY_LIC, encoding="utf-8").read()
print("美化修正 LICENSE 首行:", t.split("\n")[0])
print("含「系统联动补全」:", "系统联动补全" in t)
