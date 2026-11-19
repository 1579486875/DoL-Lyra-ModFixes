"""A08：回滚到 0A316E37 + 修 Z03 的 html.escape 双转义 bug。"""
import hashlib
import os
import re
import shutil

WORK = r"E:\TAML\_dol\work"
OUT = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
ARCHIVE = r"E:\TAML\_dol\archive"
GOOD = os.path.join(ARCHIVE, "DoL-Lyra-0.5.12.13-CHS-modded_20261120-061313_修复arsc可安装.apk")
HTML = os.path.join(WORK, "index_modded6.html")

# 1) 回滚 out 到能装的版本
if os.path.exists(GOOD):
    bak = os.path.join(ARCHIVE, "DoL-Lyra-0.5.12.13-CHS-modded_20261120-071238_BAD_双转义.apk")
    if os.path.exists(OUT) and not os.path.exists(bak):
        shutil.copy2(OUT, bak)
    shutil.copy2(GOOD, OUT)
    h = hashlib.sha256(open(OUT, "rb").read()).hexdigest().upper()
    print(f"✅ 已回滚 out -> {h[:16]}  ({os.path.getsize(OUT)/1048576:.2f} MB)")

# 2) 修 index_modded6.html 的双转义
raw = open(HTML, "rb").read().decode("utf-8", "replace")
n_raw = len(re.findall(r"<tw-passagedata", raw))
n_esc = len(re.findall(r"&lt;tw-passagedata", raw))
print(f"\nindex 当前: 明文 passage {n_raw}, 转义 passage {n_esc}")

if n_raw == 0 and n_esc > 0:
    print("  ⚠️ index 被双重转义，正在修复...")
    # 只反转义 passage 标签外层（还原成原始「半转义」形态）
    # 原始形态：<tw-passagedata ...> 明文，内部 HTML 转义
    # 现在形态：&lt;tw-passagedata ...&gt; 全转义
    fixed = raw
    # 把 &lt; 和 &gt; 都还原 —— 但这样内部 HTML 也会还原成明文
    # 原始 index 的内部本来就是转义的，所以要先整体 unescape 再按原始方式 escape
    # 最简单：整体 unescape 一次 = 还原成"全明文 HTML"
    full = __import__("html").unescape(raw)
    n2 = len(re.findall(r"<tw-passagedata", full))
    print(f"  整体 unescape 后 passage: {n2}")

    # 原始 index 的形态是：passage 标签明文 + 内部 HTML 转义
    # 需要重新构建：对每个 passage 的内容做 escape，标签保持明文
    import html as H

    def rebuild(src):
        out = []
        pos = 0
        for m in re.finditer(r'(<tw-passagedata[^>]*>)(.*?)(</tw-passagedata>)', src, re.S):
            out.append(src[pos:m.start()])
            out.append(m.group(1))
            out.append(H.escape(m.group(2), quote=False))
            out.append(m.group(3))
            pos = m.end()
        out.append(src[pos:])
        return "".join(out)

    # 整体 unescape 后，passage 内容是明文，重新 escape 内容
    rebuilt = rebuild(full)
    # passage 外的部分（head/script/storydata 等）在原始 index 里是转义的
    # 检查一下 rebuilt 里 passage 外是否还是明文
    # 保守做法：passage 外用 H.escape，passage 内也 escape —— 等于全 escape，不对
    # 正确做法：原 index 的形态是「整个文件除了 tw-storydata 结构外都转义」
    # 先看一个原始好的 index 样本
    print("  用 0A316E37 的 index 作模板比对...")
    import zipfile
    gz = zipfile.ZipFile(GOOD)
    good_raw = gz.read("assets/www/index.html").decode("utf-8", "replace")
    g_n = len(re.findall(r"<tw-passagedata", good_raw))
    g_e = len(re.findall(r"&lt;tw-passagedata", good_raw))
    print(f"  好包 index: 明文 {g_n}, 转义 {g_e}")
    print(f"  好包开头: {good_raw[:80]!r}")
    print(f"  坏包开头: {raw[:80]!r}")

    # 直接判定：好包 passage 是明文，所以只需把坏包整体 unescape 一次并保留内部转义
    # 观察好包一个 passage 的内容形态
    m = re.search(r'<tw-passagedata[^>]*>(.{0,200})', good_raw, re.S)
    if m:
        print(f"  好包 passage 内容样本: {m.group(1)[:200]!r}")

print("\n" + "=" * 90)
print("下一步：把好包的 index 作为基线，重放本轮修复")
print("=" * 90)
if os.path.exists(GOOD):
    gz = zipfile.ZipFile(GOOD)
    good_raw = gz.read("assets/www/index.html").decode("utf-8", "replace")
    open(HTML, "wb").write(good_raw.encode("utf-8"))
    print(f"✅ 已用 0A316E37 的 index 覆盖 index_modded6.html")
    print(f"   明文 passage: {len(re.findall(r'<tw-passagedata', good_raw))}")
