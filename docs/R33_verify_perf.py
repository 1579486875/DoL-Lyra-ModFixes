"""第 33 轮：验证 R24 翻译在 APK 里 + 性能基线。"""
import html
import os
import re
import time
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"

print("=" * 88)
print("1) R24 翻译验证")
print("=" * 88)
CN = [
    "它「啵」地一声抽了出来",
    "白天你可以自由探索这栋建筑",
    "别进入任何标有「员工专用」的门",
    "他们转过身来打量你",
    "你一直以不当的方式展示自己的身体",
    "你们都停下了片刻",
    "当阴霾将你吞没时",
    "还知道带着灯，挺机灵",
    "你睁开眼，看见黑狼正蜷缩在你身旁",
    "黑狼把一些东西放在了你的身旁",
    "一盏白灯在你头顶亮起",
    "你看不清舞台边缘之外的地方",
    "你们两人一起跌倒在地",
    "你的心脏仍在剧烈跳动",
    "你听到身后传来一声哨响",
    "你听到一声撕裂声",
    "那是你曾经见过的眼神",
    "贞操带的钥匙早已不知所踪",
    "一切都会好起来的",
]
EN = [
    "It exits with a pop, prompting Gwylan to slowly moan",
    "You're free to explore the building during the day",
    "Don't enter any doors marked for staff",
    "They turn to regard you",
    "You've been displaying your body in inappropriate ways",
    "You both stop for a moment",
    "Its wooden face is the last thing you see",
    "Smart thinking, with the light",
    "You open your eyes to see the Black Wolf curling up",
    "The Black Wolf drops some by your side",
    "A single white light turns on above you",
    "You can't see beyond the edge of the stage",
    "Paper flies everywhere as both of you tumble",
    "Your heart continues to beat rapidly",
    "You hear a whistle blow behind you",
    "You hear a tear",
    "It's a look you've seen before",
    "The key to the belt is long lost",
    "Everything will be fine",
]

z = zipfile.ZipFile(APK)
raw = z.read("assets/www/index.html").decode("utf-8", "replace")
g = html.unescape(raw)

cn_ok = sum(1 for c in CN if c in g)
en_rem = [(e, g.count(e)) for e in EN if e in g]
print(f"  中文注入: {cn_ok}/{len(CN)}")
print(f"  英文残留: {len(en_rem)}")
for e, n in en_rem:
    print(f"    ⚠️ {n}× {e!r}")

print("\n" + "=" * 88)
print("2) 性能基线")
print("=" * 88)
for label, p in (("modded", APK), ("vanilla", VAN)):
    st = os.stat(p)
    zz = zipfile.ZipFile(p)
    idx = zz.getinfo("assets/www/index.html")
    print(f"  {label}:")
    print(f"    APK   {st.st_size/1048576:.2f} MB")
    print(f"    index {idx.file_size/1048576:.2f} MB  (压缩后 {idx.compress_size/1048576:.2f} MB)")
    print(f"    压缩比 {idx.compress_size/idx.file_size*100:.1f}%")

# index 解析性能
print("\n" + "=" * 88)
print("3) 解析性能（Python 侧参考值）")
print("=" * 88)
t0 = time.time()
n = len(re.findall(r"<tw-passagedata", raw))
t1 = time.time()
print(f"  passage 扫描: {n:,} 个，{t1-t0:.2f}s")

t0 = time.time()
m = html.unescape(raw)
t1 = time.time()
print(f"  HTML unescape: {len(m)/1048576:.1f} MB -> {len(m)/1048576:.1f} MB，{t1-t0:.2f}s")

# widget / 宏密度
t0 = time.time()
w = len(re.findall(r'<<widget "', m))
mc = len(re.findall(r"<<", m))
t1 = time.time()
print(f"  widget {w:,} 个 / << 标记 {mc:,} 个，{t1-t0:.2f}s")

print("\n" + "=" * 88)
print("4) 体积变化（modded vs vanilla）")
print("=" * 88)
ms = os.path.getsize(APK)
vs = os.path.getsize(VAN)
print(f"  modded {ms/1048576:.2f} MB  vanilla {vs/1048576:.2f} MB")
print(f"  差值   +{(ms-vs)/1048576:.2f} MB  (+{(ms-vs)/vs*100:.1f}%)")

mz = zipfile.ZipFile(APK)
vz2 = zipfile.ZipFile(VAN)
mi = mz.getinfo("assets/www/index.html").file_size
vi = vz2.getinfo("assets/www/index.html").file_size
print(f"  index: modded {mi/1048576:.2f} MB  vanilla {vi/1048576:.2f} MB  差 +{(mi-vi)/1048576:.2f} MB")
