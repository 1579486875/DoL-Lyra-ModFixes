# -*- coding: utf-8 -*-
"""FIX-R7A：修用户实测的四类问题（幂等）。

A. setup.breastsizes 英文数组 -> 中文（拼接 "large胸部" 的直接根因）
B. wearProp 的 setup.propDefaults 兜底（props/undefined/xxx.png）
C. NPCTitleList_cn_name 补 slenderman / lissomeman / glowing tentacle
D. StoryInit 加运行时兜底：把 passage 文本里的 <<br>> 还原成 <br>

只改动目标片段；passage 数必须保持 16088。
"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
E = lambda s: H.escape(s, quote=False)

raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
if npass != 16088:
    print("❌ passage 数异常", npass)
    sys.exit(1)

g = H.unescape(raw)
changed = []

# ---------- A. breastsizes 中文 ----------
OLD_A = '<<set setup.breastsizes to ["", "budding", "tiny", "small", "pert", "modest", "full", "large", "ample", "massive", "huge", "gigantic", "enormous"]>>'
NEW_A = '<<set setup.breastsizes to ["", "含苞", "娇小", "小巧", "挺立", "适中", "丰满", "浑圆", "傲人", "硕大", "巨硕", "惊人", "宏伟"]>>'
if OLD_A in g:
    g = g.replace(OLD_A, NEW_A)
    changed.append("A: breastsizes -> 中文")
elif NEW_A in g:
    changed.append("A: 已修")
else:
    print("⚠ A 未命中（结构可能已变）")

# ---------- B. wearProp 兜底 ----------
OLD_B = "T.prop = Object.assign({}, setup.propDefaults, propErties, {"
NEW_B = ('T.prop = Object.assign({}, (setup.propDefaults || { folder: "general", '
         'armPosition: "right_hold", animation: "idle", zIndex: "handheld" }), propErties, {')
if OLD_B in g:
    g = g.replace(OLD_B, NEW_B)
    changed.append("B: propDefaults 兜底")
elif "setup.propDefaults || {" in g:
    changed.append("B: 已修")
else:
    print("⚠ B 未命中")

# ---------- C. NPCTitleList 补名 ----------
m = re.search(r'<<set setup\.NPCTitleList_cn_name to "([^"]*)"', g)
if m:
    tbl = m.group(1)
    adds = []
    for k, v in [("slenderman", "瘦长鬼影"), ("lissomeman", "柔影"), ("glowing tentacle", "发光触手")]:
        if (k + ",") not in tbl:
            adds.append("%s,%s" % (k, v))
    if adds:
        newtbl = tbl + "|" + "|".join(adds)
        g = g.replace(m.group(0), '<<set setup.NPCTitleList_cn_name to "%s"' % newtbl, 1)
        changed.append("C: 补名 " + ",".join(adds))
    else:
        changed.append("C: 已修")
else:
    print("⚠ C 未命中考题表")

# ---------- D. <<br>> 运行时兜底 ----------
MARK = "<!-- R7A_BR_GUARD -->"
GUARD = MARK + """<<script>>
(function () {
  try {
    var fix = function (p) {
      if (p && typeof p.text === "string" && p.text.indexOf("<<br>>") !== -1) {
        p.text = p.text.replace(/<<br>>/g, "<br>");
      }
    };
    var S = (typeof SugarCube !== "undefined" && SugarCube.Story) ? SugarCube.Story : null;
    if (S && S.passages) { S.passages.forEach(fix); }
    if (S && S.lookup) { S.lookup().forEach(fix); }
  } catch (e) { console.warn("[R7A] br guard:", e); }
})();
<</script>>"""
if MARK not in g:
    # 插到 StoryInit 的 <<variablesStatic>> 之后（StoryInit 每页都会跑）
    m2 = re.search(r'<<variablesStatic>>', g)
    if not m2:
        print("⚠ D 找不到 variablesStatic")
    else:
        g = g[:m2.end()] + "\n" + GUARD + g[m2.end():]
        changed.append("D: <<br>> 兜底注入 StoryInit")
else:
    changed.append("D: 已修")

# ---------- 写回 ----------
new_raw = E(g) if False else g  # g 是 unescape 后的整体，直接 encode 会破坏 HTML 结构
# 正确做法：只把改动写回 raw —— 用 raw.replace(escape(old), escape(new)) 逐项做
raw2 = raw
mapAB = [(E(OLD_A), E(NEW_A)), (E(OLD_B), E(NEW_B))]
for a, b in mapAB:
    if a in raw2:
        raw2 = raw2.replace(a, b)
if m:
    old_tbl_raw = E(m.group(0))
    # 从 g 里取新表
    m3 = re.search(r'<<set setup\.NPCTitleList_cn_name to "([^"]*)"', g)
    if m3:
        new_tbl_raw = E('<<set setup.NPCTitleList_cn_name to "%s"' % m3.group(1))
        raw2 = raw2.replace(old_tbl_raw, new_tbl_raw, 1)
if MARK not in H.unescape(raw2):
    m4 = re.search(re.escape(E("<<variablesStatic>>")), raw2)
    if m4:
        raw2 = raw2[:m4.end()] + "\n" + E(GUARD) + raw2[m4.end():]

npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
print("changed:", changed)
print("passage:", npass, "->", npass2)
if npass2 != npass:
    print("❌ passage 数变化，拒绝写入")
    sys.exit(1)

open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写入", HTML, len(raw2))
