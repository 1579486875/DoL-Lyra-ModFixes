"""R16：修 Forest Shop —— 在 generateshoppage 里对 _item.slot 做兜底解析。

真正的调用链：Forest Shop → forestShop-main → AllShop → clothingShopv2 → generateshoppage
_items 由上层传入，我上一轮在 clothingShopv2 里补 slot 覆盖不到这里。

根因：
  原版按 `_item.slot` 判断真实栏位，但模组用 JS push 的服装常常漏了 slot 字段
  （dragonbreath / Queen of heart / Alice's dream / acorn / Suit for Adventurer …），
  于是 $_realSlot = undefined → setup.clothes[undefined] → 整条链 NPE。

修复（最小改动，只加兜底，不改原语义）：
  先试 _item.slot；没有就遍历 setup.clothes 各栏位，按 index 反查；
  再没有就用 "upper"（这些报错服装的图路径都在 clothes/upper/ 下）。
"""
import html as H
import re
import shutil

HTML = r"E:\TAML\_dol\work\index_modded6.html"
shutil.copy2(HTML, HTML + ".bak_R16")

data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    raise SystemExit("❌ index 形态异常")

MARK = "[R16]"
g = H.unescape(data)
if MARK in g:
    print("（已注入过，跳过）")
    raise SystemExit(0)

OLD_RAW = '<<set $_realSlot to ($clothingShopSlot is "all" ? _item.slot : $clothingShopSlot)>>'
NEW_RAW = (
    '<!-- [R16] slot 兜底：模组服装常漏 slot 字段，按 index 反查 -->'
    '<<set $_realSlot to ($clothingShopSlot is "all" '
    '? (_item.slot || Object.keys(setup.clothes).find(_k => _k !== "all" '
    '&& Array.isArray(setup.clothes[_k]) '
    '&& setup.clothes[_k].some(_x => _x && _x.index === _item.index)) || "upper") '
    ': $clothingShopSlot)>>'
)

# 只替换 generateshoppage 里的那一处（全局该字符串应当只有 1 处）
cnt_total = g.count(OLD_RAW)
print(f"全局出现次数: {cnt_total}")

# 定位 generateshoppage 范围
wm = re.search(r'<<widget "generateshoppage">>', g)
if not wm:
    raise SystemExit("❌ 找不到 generateshoppage")
we = g.find("<</widget>>", wm.start())
seg = g[wm.start():we]
cnt_seg = seg.count(OLD_RAW)
print(f"generateshoppage 内出现: {cnt_seg}")

if cnt_seg != 1:
    raise SystemExit(f"❌ generateshoppage 内应恰好 1 处，实际 {cnt_seg}")

# 转义后替换（只替换第一处 = 该 widget 内那处）
old_esc = H.escape(OLD_RAW, quote=False)
new_esc = H.escape(NEW_RAW, quote=False)
n = data.count(old_esc)
print(f"转义形态出现: {n}")

if n == 1:
    data = data.replace(old_esc, new_esc, 1)
elif n > 1:
    # 多处时只改 generateshoppage 内那处：按前缀定位
    wt = H.escape('<<widget "generateshoppage">>', quote=False)
    wi = data.find(wt)
    oi = data.find(old_esc, wi)
    if oi < 0:
        raise SystemExit("❌ 定位失败")
    data = data[:oi] + new_esc + data[oi + len(old_esc):]
    print("  （多处，仅改 generateshoppage 内第一处）")
else:
    raise SystemExit("❌ 转义形态找不到")

open(HTML, "wb").write(data.encode("utf-8"))
print("✅ 已注入")

# 校验
g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
print("\n" + "=" * 90)
print("校验")
print("=" * 90)
m = re.search(r'<<widget "generateshoppage">>(.{0,1400})', g2, re.S)
if m:
    print(m.group(1)[:1400])
print(f"\n  passage: {len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML,'rb').read().decode('utf-8','replace')))}")
