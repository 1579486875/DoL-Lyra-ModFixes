"""把所有 <<script>> 提取出来，用 node --check 逐个验证语法。

用户报 setup.description_CN / NPC_CN_TOOLNAME is not a function
=> <<script>> 整体未执行 => 有语法错误
"""
import html
import os
import re
import subprocess
import tempfile
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
TMP = os.path.join(tempfile.gettempdir(), "dsh_sc.js")

z = zipfile.ZipFile(APK)
raw = z.read("assets/www/index.html").decode("utf-8", "replace")
g = html.unescape(raw)

scripts = []
for m in re.finditer(r"<<script>>(.*?)<</script>>", g, re.S):
    scripts.append((m.start(), m.group(1)))

print(f"共 {len(scripts)} 个 <<script>> 块\n")

bad = 0
for pos, src in scripts:
    if not src.strip():
        continue
    open(TMP, "w", encoding="utf-8").write(src)
    r = subprocess.run(["node", "--check", TMP], capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        bad += 1
        print("=" * 88)
        print(f"❌ 语法错误 @{pos}  (长度 {len(src)})")
        print("=" * 88)
        for line in (r.stderr or "").strip().split("\n")[:8]:
            print("  " + line)
        # 定位到源码
        print(f"\n  前 600 字符:\n{src[:600]}")
        print(f"\n  后 600 字符:\n{src[-600:]}")
        print()

print(f"\n=== 结果：{len(scripts)} 块，语法错误 {bad} 块 ===")

# 额外：检查关键函数到底在不在
print("\n" + "=" * 88)
print("关键函数定义检查")
print("=" * 88)
for fn in ["description_CN", "NPC_CN_TOOLNAME", "NPC_CN_TYPE", "NPC_CN_NAME",
           "NPC_CN_TITLE", "BODYPARTS_CN_NAME", "CAFE_FOOD_CN", "DirectionCN",
           "brothelshowType_CN", "update_cloth_cn"]:
    pat = f"st.{fn} ="
    print(f"  setup.{fn}: {'✅ 有定义' if pat in g else '❌ 无定义'}")
