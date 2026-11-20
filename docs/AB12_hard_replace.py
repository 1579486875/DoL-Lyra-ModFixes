"""AB12：直接硬替换最后 2 处（绕过 FIXES 循环）。"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[AB12] index 形态异常")
    sys.exit(1)

# 用最直接的字节级替换
OLD1 = "It continues to force you to play with yourself, but limits its control so you can do your task."
NEW1 = "它继续逼迫你玩弄自己，但限制了控制力，好让你完成任务。"
OLD2 = "It continues to force you to play with yourself."
NEW2 = "它继续逼迫你玩弄自己。"

n1 = data.count(OLD1)
n2 = data.count(OLD2)
print(f"找到: 长版 {n1} 处 / 短版 {n2} 处")

# ⚠️ 先替换长版（否则短版会误伤长版的前缀）
data = data.replace(OLD1, NEW1)
data = data.replace(OLD2, NEW2)

open(HTML, "wb").write(data.encode("utf-8"))
print(f"已替换 {n1 + n2} 处")

# 校验
g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
left = g.count("It continues to force you to play with yourself")
print(f"\n残留: {left}  {'OK' if left == 0 else 'FAIL'}")
print(f"passage: {len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML,'rb').read().decode('utf-8','replace')))}")

# 顺便确认替换后的内容正确
for m in list(re.finditer("它继续逼迫你玩弄自己", g))[:2]:
    print(f"  {g[max(0,m.start()-60):m.start()+80]!r}")

sys.exit(0 if left == 0 else 1)
