# -*- coding: utf-8 -*-
"""根据 GitHub 实查结果，修正三个模组的归属声明。"""
import os

SIGN = "大赢经直插白皮赢道（1579486875）"

# ============================================================
# 1. 修正 美化修正 的 LICENSE（其实是 ANLINSTUDIO 的）
# ============================================================
BEAUTY = r"E:\TAML\_dol\work\_mods\44_美化修正\LICENSE.md"

BEAUTY_NEW = """# 美化修正 · 声明与许可

> **本模组由 ANLINSTUDIO 开发，本包仅作打包分发，未作任何修改。**

## 原作者

- **ANLINSTUDIO**
- GitHub：<https://github.com/ANLINSTUDIO>
- 项目主页：<https://github.com/ANLINSTUDIO/Degrees-of-Lewdity-BeautyFixer>
- 交流渠道：DoL 中文 Discord 频道（见原作者 README）

## 许可

原作者 **未在仓库中声明具体的开源许可名称**（GitHub `license` 字段为空）。

但其 README 明确写道：

> 本模组与 Degrees of Lewdity 及其 Mod Loader 生态保持一致，**仅限非商业用途**。

**据此，本包遵循以下原则：**

1. **仅作非商业用途**；
2. **完整保留原作者署名**，未作任何修改；
3. **如原作者提出异议，将立即移除**。

## 本模组做什么

`美化修正`（BeautyFixer）是一个**图片覆盖工具**，用于调整美化资源与游戏服装的对齐问题。

原作者描述：

> 本模组为游戏内添加图像编辑器，直接修正服装 / 五官 / 头发的图像。
> 避免游戏版本或模组服装与美化不兼容。那就自给自足！
> 无需拥有过强的美术基础，简单的移动、补齐像素，谁都能上手。

功能：
- 图层面板化编辑（原图 + 自绘笔迹层 + 复制块 + 导入图层）
- 像素级对准：网格吸附、1px 微调、25%–400% 缩放、多选成组变换
- 像素重烤（Pixel Rebake）
- 镜像/同步绘制、切线分割、取色盖章、服装组编辑
- 修改只存玩家笔迹与位置参数（不存原图像素，永不污染）
- 可导出/导入修正码

## 上游致谢

| 组件 | 作者 | 许可 |
|---|---|---|
| **Degrees of Lewdity** | **Vrelnir** | CC BY-NC-SA 4.0 |
| **BeautyFixer** | **ANLINSTUDIO** | 仅限非商业 |
| SugarCube 2 | Thomas Michael Edwards | BSD 3-Clause |
| ModLoader | Lyoko-Jeremie | 见原仓库 |
| TweeReplacer | Lyoko-Jeremie | 见原仓库 |

## 免责

本模组按"现状"提供，不附带任何担保。**仅限 18 岁以上成年人使用**。

## 问题反馈

- **模组本身的问题**：请向原作者 ANLINSTUDIO 反馈（GitHub Issues 或 Discord）
- **本包的打包问题**：<https://github.com/1579486875/DoL-Lyra-ModFixes/issues>
"""

open(BEAUTY, "w", encoding="utf-8").write(BEAUTY_NEW)
print("✅ 重写 美化修正/LICENSE.md（归属改为 ANLINSTUDIO）")

# ============================================================
# 2. 修正 系统联动补全 的 LICENSE（这个确实是我们写的）
# ============================================================
LINK = r"E:\TAML\_dol\work\联动模组\系统联动补全\LICENSE.md"

LINK_NEW = """# 系统联动补全 · 声明与许可

## 本模组的许可

本模组（`系统联动补全` / System Interactions）由 **{sign}** 原创，采用
**CC BY-NC-SA 4.0**（知识共享 署名—非商业性使用—相同方式共享 4.0 国际）。

- 许可全文：<https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode>

**你可以**：自由使用、修改、分发，**条件是**：
1. 署名原作者；
2. **不得用于商业目的**；
3. 修改后的作品必须使用**同样的许可**发布。

## 本模组做什么

把原本互不相干的系统接起来，共 **6 组联动**：

| 联动 | 触发 | 效果 |
|---|---|---|
| **失禁 → 羞耻/名声** | 膀胱从 ≥9000 跳到 0 | 按场合分 4 档（在家 / 无人 / 公共不在意 / 公共羞耻）加压力、创伤、名声 |
| **服装破损 → 走光** | 衣服完好度 <70% | 半透 +20 压力；走光 +60 压力 +1 名声（同一次破损名声只计一次） |
| **需求 → 战斗** | 开战瞬间口渴/尿意 ≥8000 | 尿急 +300 压力，口渴 +200 压力 |
| **拍照 → 暴露名声** | 手机拍照计数增长 | 暴露自拍 +5 名声 +100 压力 +60 性奋；公共拍照 +1 名声 |
| **在自家 → 放松** | 自家 + 暴露状态 | 削减 8% 压力（最多 200） |
| **怀孕 → 尿意不适** | 怀孕中 + 尿意 ≥7000 | +30 压力 |

**设计原则**：
- 只读取游戏已有状态，只追加副作用（`$stress` / `$trauma` / `$fame` / `$arousal`）
- **不修改**游戏的任何原有逻辑、渲染、战斗公式或存档结构
- 每组联动有独立开关，可单独关闭
- 删除模组即完全回退

## 上游致谢

| 组件 | 作者 | 许可 |
|---|---|---|
| **Degrees of Lewdity** | **Vrelnir** | CC BY-NC-SA 4.0 |
| SugarCube 2 | Thomas Michael Edwards | BSD 3-Clause |
| ModLoader | Lyoko-Jeremie | 见原仓库 |
| maplebirch | MaplebirchLeaf | MIT |
| BasicNeeds | YanYeQi | 无显式声明 |

**Degrees of Lewdity** 版权归 **Vrelnir** 所有。
- 博客：<https://vrelnir.blogspot.com>
- 源码：<https://gitgud.io/Vrelnir/degrees-of-lewdity>

## 免责

本模组按"现状"提供，不附带任何担保。**仅限 18 岁以上成年人使用**。

## 联系

问题反馈：<https://github.com/1579486875/DoL-Lyra-ModFixes/issues>
""".replace("{sign}", SIGN)

open(LINK, "w", encoding="utf-8").write(LINK_NEW)
print("✅ 重写 系统联动补全/LICENSE.md（标注为自研 + 列出 6 组联动）")

print("\n=== 校验 ===")
for p in (BEAUTY, LINK):
    t = open(p, encoding="utf-8").read()
    print("%-22s %d 字节 | 含署名 %d 处" % (
        os.path.basename(os.path.dirname(p)), len(t.encode()), t.count(SIGN)))
