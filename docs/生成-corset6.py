# -*- coding: utf-8 -*-
"""用 corset/4.png 生成 corset/6.png（方案 B）。

思路：
1. 找出 4.png 里所有不透明像素的连通块（左右两个束腰）
2. 每块分别横向拉伸 1.10 倍
3. 各自向外平移几像素（模拟胸部撑开）
4. 合成到新图
"""
import os

from PIL import Image

SRC = r"E:\TAML\_dol\work\诊断-三类服装\corset\4.png"
OUT_DIR = r"E:\TAML\_dol\work\诊断-三类服装\corset-新"
os.makedirs(OUT_DIR, exist_ok=True)


def find_blobs(img, alpha_thr=16):
    """用简单的行扫描找左右连通块（假定只有左右两块）。"""
    w, h = img.size
    px = img.load()
    cols = set()
    for y in range(h):
        for x in range(w):
            if px[x, y][3] > alpha_thr:
                cols.add(x)
    if not cols:
        return []
    # 把列号聚类（间隔 > 8 视为新块）
    xs = sorted(cols)
    blobs = []
    start = xs[0]
    prev = xs[0]
    for x in xs[1:]:
        if x - prev > 8:
            blobs.append((start, prev))
            start = x
        prev = x
    blobs.append((start, prev))
    return blobs


def main():
    img = Image.open(SRC).convert("RGBA")
    w, h = img.size
    blobs = find_blobs(img)
    print("找到 %d 个连通块: %s" % (len(blobs), blobs))

    if len(blobs) != 2:
        print("⚠ 块数不是 2，按整体处理")

    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    FACTOR = 1.10      # 横向拉伸
    SHIFT = 3          # 向外平移像素

    for i, (x0, x1) in enumerate(blobs):
        # 纵向范围
        px = img.load()
        ys = [y for y in range(h) for x in range(x0, x1 + 1) if px[x, y][3] > 16]
        if not ys:
            continue
        y0, y1 = min(ys), max(ys)

        # 裁出这一块
        region = img.crop((x0, y0, x1 + 1, y1 + 1))
        new_w = max(1, int(region.width * FACTOR))
        region2 = region.resize((new_w, region.height), Image.LANCZOS)

        # 计算粘贴位置：以原块中心为基准，向外偏移
        cx = (x0 + x1) // 2
        if i == 0:
            cx -= SHIFT    # 左块向左
        else:
            cx += SHIFT    # 右块向右
        paste_x = cx - new_w // 2
        out.paste(region2, (paste_x, y0), region2)
        print("  块%d: x=%d-%d y=%d-%d -> 宽 %d->%d, 贴到 x=%d" % (
            i, x0, x1, y0, y1, region.width, new_w, paste_x))

    dst = os.path.join(OUT_DIR, "6.png")
    out.save(dst, "PNG", optimize=True)
    print("\n✅ 输出:", dst, os.path.getsize(dst), "字节")


if __name__ == "__main__":
    main()
