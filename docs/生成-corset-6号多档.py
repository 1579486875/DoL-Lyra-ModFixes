# -*- coding: utf-8 -*-
"""为 corset 生成真正「6 号胸」的图。

关键认识：束腰是左右两块，大胸时会被撑向两侧。
所以 6 号不能只是把 4 号横向拉宽，必须：
  1) 每块加宽（模拟被撑开）
  2) 两块各自向外平移（模拟胸部占位变大）
  3) 纵向略微拉长（大胸时束腰覆盖范围更大）

同时输出多档参数，便于挑选。
"""
import os

from PIL import Image

SRC = r"E:\TAML\_dol\work\诊断-三类服装\corset\4.png"
OUT = r"E:\TAML\_dol\work\诊断-三类服装\corset-6号"
os.makedirs(OUT, exist_ok=True)

img = Image.open(SRC).convert("RGBA")
W, H = img.size
px = img.load()


def find_blobs(im, thr=16):
    w, h = im.size
    p = im.load()
    cols = [x for x in range(w) for y in range(h) if p[x, y][3] > thr]
    if not cols:
        return []
    cols = sorted(set(cols))
    blobs, start, prev = [], cols[0], cols[0]
    for x in cols[1:]:
        if x - prev > 8:
            blobs.append((start, prev))
            start = x
        prev = x
    blobs.append((start, prev))
    return blobs


def blob_bbox(im, x0, x1, thr=16):
    w, h = im.size
    p = im.load()
    ys = [y for y in range(h) for x in range(x0, x1 + 1) if p[x, y][3] > thr]
    return (min(ys), max(ys)) if ys else (0, 0)


blobs = find_blobs(img)
print("4.png 连通块:", blobs)
if len(blobs) != 2:
    raise SystemExit("⚠ 不是两块，停止")

# 参数组：(横向缩放, 向外平移, 纵向缩放)
VARIANTS = [
    ("A_保守", 1.20, 4, 1.00),
    ("B_中等", 1.28, 7, 1.06),
    ("C_激进", 1.36, 10, 1.12),
    ("D_最宽", 1.45, 13, 1.18),
]

for name, fx, shift, fy in VARIANTS:
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for i, (x0, x1) in enumerate(blobs):
        y0, y1 = blob_bbox(img, x0, x1)
        region = img.crop((x0, y0, x1 + 1, y1 + 1))
        nw = max(1, int(region.width * fx))
        nh = max(1, int(region.height * fy))
        region2 = region.resize((nw, nh), Image.LANCZOS)

        cx = (x0 + x1) // 2
        cx = cx - shift if i == 0 else cx + shift
        # 纵向以底边为基准（束腰下缘固定，向上撑开）
        paste_x = cx - nw // 2
        paste_y = y1 - nh + 1
        out.paste(region2, (paste_x, paste_y), region2)

    p = os.path.join(OUT, "%s.png" % name)
    out.save(p, "PNG", optimize=True)
    print("  %-8s 缩放%.2f 平移%+d 纵向%.2f -> %d 字节" % (name, fx, shift, fy, os.path.getsize(p)))

print("\n输出:", OUT)
