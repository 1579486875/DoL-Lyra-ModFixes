# -*- coding: utf-8 -*-
r"""补丁体检：检查 work\index_modded6.html（打包权威源）里所有已知补丁是否齐全。

背景（两次事故）：
  第 43 轮修了 MapleBirchCE 的 _zs 钳位 -> 只改 out 的 APK，没落地 work
      -> 第 48 轮「以最新为底」重打包时 index 被 work 覆盖，修复丢失
  第 50 轮修了坐标系 + 钳位 -> 同样只改 out
      -> 第 51 轮又被覆盖，用户报「解锁图标拖动限制又回来了」

根因：重打包-以最新为底.py 会用 work\index_modded6.html 替换 APK 里的 index。
      所以【任何修改 index 的操作，必须写进 work 源】。

用法：
  python 体检-补丁齐全.py           # 检查 work 源
  python 体检-补丁齐全.py <apk>      # 检查指定 APK

退出码 0 = 全部齐全；1 = 有缺失。
"""
import base64
import io
import json
import re
import sys
import zipfile


def load_index(target):
    if target.lower().endswith(".apk"):
        z = zipfile.ZipFile(target)
        return z.read("assets/www/index.html").decode("utf-8", "replace")
    return open(target, encoding="utf-8", errors="replace").read()


def get_mod(html, name):
    """取出某个模组的 {文件名: 内容} 字典。"""
    mz = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", html, re.S)
    if not mz:
        return None
    for s in re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', mz.group(1)):
        try:
            d = base64.b64decode(re.sub(r"\s+", "", s))
        except Exception:
            continue
        if d[:2] != b"PK":
            continue
        try:
            zz = zipfile.ZipFile(io.BytesIO(d))
            bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
        except Exception:
            continue
        if (bj.get("name") or "") == name:
            out = {}
            for n in zz.namelist():
                if n.lower().endswith((".js", ".twee", ".tw")):
                    try:
                        out[n] = zz.read(n).decode("utf-8", "replace")
                    except Exception:
                        pass
            return out
    return None


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else r"E:\TAML\_dol\work\index_modded6.html"
    print("检查目标:", target)
    html = load_index(target)
    print("index 大小: %d 字符\n" % len(html))

    fail = 0

    def check(scope_label, text, needle, why):
        nonlocal fail
        ok = needle in text
        if not ok:
            fail += 1
        print("  %s %-34s %s" % ("OK  " if ok else "缺失", needle[:32], why))
        return ok

    # ========== 1. 系统联动补全 ==========
    print("=== [1] 系统联动补全 / core.js ===")
    mod = get_mod(html, "系统联动补全")
    if not mod:
        print("  ❌ 找不到模组")
        fail += 1
    else:
        core = mod.get("scripts/core.js", "")
        print("  core.js: %d 字符" % len(core))
        for k, why in [
            ("PHONE_SHOP_PATCH", "购物中心手机店入口"),
            ("TOILET_PATCH", "枯木逢春浴室厕所"),
            ("YENOTE_TEXT_PATCH", "小黄书发帖文本"),
            ("NPC_TITLE_FIX", "NPC 英文 title"),
            ("PROP_FOLDER_FIX", "prop 路径 undefined"),
            ("inOwnHome 修正版", "房产误判为在家（文案串台）"),
            ("PUBLIC_RE_V2", "公共场所判定补全"),
            ("CHEAT_FACE_FIX_V2", "作弊菜单脸型/举止"),
            ("POSSESSIVE_FIX", "所有格 's 残留"),
            ("ARTICLE_FIX", "英文冠词残留"),
            ("cleanTextNodes", "文本清洗函数"),
        ]:
            check("联动", core, k, why)

        # cleanTextNodes 是否被调用
        calls = [m for m in re.finditer(r"cleanTextNodes\(\)", core)
                 if not core[max(0, m.start() - 9):m.start() + 16].startswith("function cleanTextNodes")]
        if calls:
            print("  OK   cleanTextNodes 调用点            %d 处" % len(calls))
        else:
            print("  缺失 cleanTextNodes 调用点            文本清洗不会执行")
            fail += 1

        # 裸尖括号检查（会触发 REGRESS 的 C.no_raw_angle_in_passage）
        # 只针对 Twee 文件
        for fn, txt in mod.items():
            if fn.lower().endswith((".twee", ".tw")):
                if "<" in txt or ">" in txt:
                    # tw 文件里允许 HTML 标签，这里只报告箭头式写法
                    for mm in re.finditer(r"(?<!-)->", txt):
                        print("  ⚠  %s 里有裸箭头 -> （可能触发尖括号检查）@%d" % (fn, mm.start()))
                        fail += 1
                        break

    # ========== 2. MapleBirchCE 拖动 ==========
    print("\n=== [2] MapleBirchCE / maplebirchce.js（浮层拖动）===")
    mod = get_mod(html, "MapleBirchCE")
    if not mod:
        print("  ❌ 找不到模组")
        fail += 1
    else:
        js = mod.get("javascript/maplebirchce.js", "")
        print("  maplebirchce.js: %d 字符" % len(js))
        check("MB", js, "_mbceZoomScale", "zoomScale 辅助函数")

        n_zsv = js.count("_zsv")
        print("  %s _zsv（钳位变量）                 %d 处（应 >=14）" % ("OK  " if n_zsv >= 14 else "缺失", n_zsv))
        if n_zsv < 14:
            fail += 1

        n_bare = len(re.findall(r'window\.innerWidth\) \|\| 1280;', js))
        print("  %s 残留裸 innerWidth 钳位             %d 处（应为 0）" % ("OK  " if n_bare == 0 else "残留", n_bare))
        if n_bare:
            fail += 1

        n_drag = len(re.findall(r"drag\.l = r\.left;", js))
        print("  %s 残留 drag.l = r.left（会弹回）      %d 处（应为 0）" % ("OK  " if n_drag == 0 else "残留", n_drag))
        if n_drag:
            fail += 1

    # ========== 3. BasicNeeds 洗澡兜底 ==========
    print("\n=== [3] BasicNeeds / 洗澡返回目标 ===")
    mod = get_mod(html, "BasicNeeds")
    if not mod:
        print("  ❌ 找不到模组")
        fail += 1
    else:
        joined = "\n".join(mod.values())
        check("BN", joined, "bnBathTarget", "跨地点洗澡返回目标")
        # 裸 Engine.play('Bath') 应为 0
        bare = len(re.findall(r"Engine\.play\(\s*['\"]Bath['\"]\s*\)", joined))
        print("  %s 裸 Engine.play('Bath')            %d 处（应为 0，否则回孤儿院）" % ("OK  " if bare == 0 else "残留", bare))
        if bare:
            fail += 1

    # ========== 4. index 文本层补丁 ==========
    print("\n=== [4] index 全局文本 ===")
    check("IDX", html, "DESCCN_CONCAT_FIX", "ruggedman 等无分隔拼接词")
    # Escape Attempt（Twee 里应已改成中文）
    n_en = len(re.findall(r'&lt;&lt;note "Escape Attempt"', html))
    print("  %s Escape Attempt 残留                %d 处（应为 0）" % ("OK  " if n_en == 0 else "残留", n_en))
    if n_en:
        fail += 1

    # ========== 5. 修复性图片模组 ==========
    print("\n=== [5] 修复性图片模组 ===")
    for name, why in [("Handheld Idle Fix", "手持物 idle 图层"),
                      ("Face Variant Fill", "脸型缺失图层")]:
        # 注意：这两个模组只有图片，没有 .js/.twee，
        # get_mod 会返回空 dict（不是 None）—— 不能直接用 truthiness 判断。
        mod = get_mod(html, name)
        ok = mod is not None
        print("  %s %-24s %s" % ("OK  " if ok else "缺失", name, why))
        if not ok:
            fail += 1

    # ========== 汇总 ==========
    print("\n" + "=" * 60)
    if fail == 0:
        print("✅ 全部补丁齐全")
    else:
        print("❌ 有 %d 项缺失/残留，需重放对应脚本" % fail)
        print("\n重放顺序（参考）：")
        print("  1) python 打包-联动模组2.py         # 系统联动补全")
        print("  2) python 修-拖动-落到work.py       # MapleBirchCE 拖动")
        print("  3) python 修-descCN拼接2.py         # descCN 拆分")
        print("  4) python 修-EscapeAttempt.py       # 逃脱尝试")
        print("  5) python 重打包-以最新为底.py      # 用 work index 重打包")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
