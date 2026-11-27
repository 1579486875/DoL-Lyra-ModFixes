# -*- coding: utf-8 -*-
"""更新 AGENTS.md 的 DoL 项目约定：新命名规则 + index 权威源规则。"""
import io
import os
import shutil

P = r"E:\TAML\AGENTS.md"
raw = open(P, "rb").read()
bom = raw.startswith(b"\xef\xbb\xbf")
text = raw.decode("utf-8-sig")

OLD = """- 交付包：`E:\\TAML\\_dol\\out\\DoL-Lyra-0.5.12.13-CHS-modded.apk`"""

NEW = """- **交付包命名（2026-11-27 用户指定）**：`育都孤儿-GNH个人整合版-YYYY.MM.DD.apk`，日期按发布当天改。
  同时保留旧名 `DoL-Lyra-0.5.12.13-CHS-modded.apk` 的一份副本（765 处脚本引用旧名，别一次性全改）。
- **★★★ index 的权威源是 `work\\index_modded6.html`，不是 `out\\` 的 APK**：
  `重打包-以最新为底.py` 会用 `work\\index_modded6.html` **覆盖** APK 里的 index。
  所以**任何对 index 的修改都必须写进 work 源**，只改 `out\\` 的 APK 一定会在下次重打包时丢失。
  - 事故 1（第 43 轮）：MapleBirchCE 的 `_zs` 钳位只改 out → 第 48 轮丢失
  - 事故 2（第 50 轮）：坐标系 + 钳位只改 out → 第 51 轮丢失，用户报「解锁图标拖动限制又回来了」
- **打包前必跑 `python work\\体检-补丁齐全.py`**（检查 work 源；也可传 APK 路径检查产物）。
  它逐项核对：系统联动补全的 11 个补丁、MapleBirchCE 拖动、BasicNeeds 洗澡、descCN 拆分、
  Escape Attempt、两个图片修复模组。退出码 0 才算可以打包。
- **交付前同时检查 `out\\` 里文件是否真的存在**：发生过一次主 apk 凭空消失（疑似杀毒/占用），
  靠 `archive\\` 的归档恢复。**每次部署必须同时往 `archive\\` 存一份**，这是唯一的兜底。"""

if OLD not in text:
    print("❌ 未找到锚点，当前 DoL 段：")
    i = text.find("## 《Degrees of Lewdity》项目上下文")
    print(text[i:i + 500] if i >= 0 else "(找不到该节)")
    raise SystemExit(1)

text2 = text.replace(OLD, NEW, 1)
assert text2 != text

# 备份
bak = P + ".bak"
shutil.copy2(P, bak)

data = (b"\xef\xbb\xbf" if bom else b"") + text2.encode("utf-8")
open(P, "wb").write(data)

print("✅ 已更新", P)
print("   原 BOM:", bom)
print("   备份:", bak)
print("   大小: %d -> %d 字节" % (len(raw), len(data)))

# 校验：新增的三条规则关键词都在
for k in ("育都孤儿-GNH个人整合版", "index 的权威源", "体检-补丁齐全.py"):
    print("   %-26s %s" % (k, "OK" if k in text2 else "MISSING"))
