# -*- coding: utf-8 -*-
"""PoC v2：按连通区域分别缩放，保持各块中心位置不变。

修正 v1 的问题：整体缩放会把左右两块的间距也改变，
正确做法是识别每个连通块，围绕各自质心缩放。
"""
import io
import os
import zipfile

import numpy as np
from PIL import Image

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
OUT = r"E:\TAML\_dol\work\试做-corset-2"
os.makedirs(OUT, exist_ok=True)

z = zipfile.ZipFile(APK)
names = {n.replace("\\", "/"): n for n in z.namelist()}


def load(rel):
    return Image.open(io.BytesIO(z.read(names["assets/www/img/" + rel]))).convert("RGBA")


def save(img, name):
    img.save(os.path.join(OUT, name))
    print("  ", name, img.size)


def connected_blocks(alpha, thresh=8):
    """简易连通域：按列分组（左右两块通常是分离的）。"""
    mask = alpha > thresh
    cols = np.nonzero(mask.any(axis=0))[0]
    if len(cols) == 0:
        return []
    # 按列间断分组
    groups = []
    start = cols[0]
    prev = cols[0]
    for c in cols[1:]:
        if c - prev > 12:      # 间隔 > 12 像素视为不同块
            groups.append((start, prev))
            start = c
        prev = c
    groups.append((start, prev))

    blocks = []
    for x0, x1 in groups:
        sub = mask[:, x0:x1 + 1]
        rows = np.nonzero(sub.any(axis=1))[0]
        if len(rows) == 0:
            continue
        blocks.append((x0, rows[0], x1 + 1, rows[-1] + 1))
    return blocks


def scale_block(img, box, factor):
    """围绕 box 中心缩放该区域，其他区域保持原样。"""
    arr = np.array(img)
    x0, y0, x1, y1 = box
    crop = img.crop(box)
    w, h = crop.size
    nw, nh = max(1, int(round(w * factor))), max(1, int(round(h * factor)))
    crop2 = crop.resize((nw, nh), Image.LANCZOS)
    # 粘贴时保持中心不变
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    px, py = cx - nw // 2, cy - nh // 2
    base = Image.new("RGBA", img.size, (0, 0, 0, 0))
    base.paste(img, (0, 0))
    # 先清空原区域
    clear = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
    base.paste(clear, (x0, y0))
    base.paste(crop2, (px, py), crop2)
    return base


print("=== 素材 ===")
corset1 = load("clothes/under-upper/corset/1.png")
corset4 = load("clothes/under-upper/corset/4.png")

a1 = np.array(corset1.split()[-1])
a4 = np.array(corset4.split()[-1])
b1 = connected_blocks(a1)
b4 = connected_blocks(a4)
print("  corset/1 连通块:", b1)
print("  corset/4 连通块:", b4)

# 轮廓宽度比：用胸部图估算
def breadth(img):
    a = np.array(img.split()[-1])
    mask = a > 8
    cols = np.nonzero(mask.any(axis=0))[0]
    return (cols[-1] - cols[0]) if len(cols) else 0


br0, br1 = load("body/breasts/breasts-0.png"), load("body/breasts/breasts-1.png")
br4, br5 = load("body/breasts/breasts-4.png"), load("body/breasts/breasts-5.png")
w0, w1 = breadth(br0), breadth(br1)
w4, w5 = breadth(br4), breadth(br5)
print("\n  胸宽 0=%d 1=%d 4=%d 5=%d" % (w0, w1, w4, w5))

f_1to0 = (w0 / w1) if w1 else 1.0
f_4to5 = (w5 / w4) if w4 else 1.0
f_1to0 = max(0.75, min(1.25, f_1to0))
f_4to5 = max(0.75, min(1.25, f_4to5))
print("  缩放系数 1->0: %.4f  4->5: %.4f" % (f_1to0, f_4to5))

print("\n=== 生成 0.png（各块单独缩放）===")
out0 = corset1
for box in b1:
    out0 = scale_block(out0, box, f_1to0)
save(out0, "corset_0.png")

print("=== 生成 5.png ===")
out5 = corset4
for box in b4:
    out5 = scale_block(out5, box, f_4to5)
save(out5, "corset_5.png")

save(corset1, "corset_1_原始.png")
save(corset4, "corset_4_原始.png")
print("\n完成 ->", OUT)
