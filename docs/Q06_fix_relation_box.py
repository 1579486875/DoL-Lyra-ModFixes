"""Q06：修 relation-box 里 NPC_CN_NAME 的 13 处错误。

根因：某个早期脚本把 `_npcData.nam` 全局替换成 `<<NPC_CN_NAME _npcData.nam>>>>>>`，
      但 SugarCube 的 `<<if>>` 表达式里不能嵌宏，必须用 `setup.NPC_CN_NAME(...)` 函数调用，
      比较场景则必须用英文原名 `_npcData.nam`。
"""
import html as H
import re

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    raise SystemExit("❌ index 形态异常")

g = H.unescape(data)

# ---- 正确写法 ----
CMP = "_npcData.nam"                                    # 比较场景：英文原名
SHOW = "<<print setup.NPC_CN_NAME(_npcData.nam)>>"       # 显示场景
ARG = "setup.NPC_CN_NAME(_npcData.nam)"                  # widget 参数场景

# 逐条精确替换（按从长到短排序，避免误伤）
FIXES = [
    # ===== A. 比较场景（必须英文原名）=====
    # A1: <<if (<<NPC_CN_NAME _npcData.nam>>>>>> is ("Ivory Wraith") or ($wraith.mimic is <<NPC_CN_NAME _npcData.nam>>>>>> and $wraith.revealed))>>
    ('<<if (<<NPC_CN_NAME _npcData.nam>>>>>> is ("Ivory Wraith") or ($wraith.mimic is <<NPC_CN_NAME _npcData.nam>>>>>> and $wraith.revealed))>>',
     '<<if (_npcData.nam is "Ivory Wraith") or ($wraith.mimic is _npcData.nam and $wraith.revealed)>>'),
    # A2: <<if <<NPC_CN_NAME _npcData.nam>>>>>> is ("Ivory Wraith") and (...)
    ('<<if <<NPC_CN_NAME _npcData.nam>>>>>> is ("Ivory Wraith") and',
     '<<if _npcData.nam is "Ivory Wraith" and'),
    # A3: <<elseif $wraithIntro and $wraith.mimic is <<NPC_CN_NAME _npcData.nam>>>>>> and
    ('<<elseif $wraithIntro and $wraith.mimic is <<NPC_CN_NAME _npcData.nam>>>>>> and',
     '<<elseif $wraithIntro and $wraith.mimic is _npcData.nam and'),
    # ===== B. widget 参数场景（<<npcrelationship X>>）=====
    ('<<npcrelationship <<NPC_CN_NAME _npcData.nam>>>>>>>>',
     '<<npcrelationship setup.NPC_CN_NAME(_npcData.nam)>>'),
    # ===== C. 显示场景 =====
    # C1: 带问号的那个（4 个 > + ？）
    ('<<NPC_CN_NAME _npcData.nam>>>>>>>>？', SHOW + '？'),
    # C2: 通用（6 个 >）
    ('<<NPC_CN_NAME _npcData.nam>>>>>>', SHOW),
]

total = 0
print("=" * 90)
print("逐条修复")
print("=" * 90)
for old, new in FIXES:
    hit = 0
    for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
        if a in data:
            c = data.count(a)
            data = data.replace(a, b)
            hit += c
            break
    if hit:
        total += hit
        print(f"  OK {hit}x  {old[:75]!r}")

open(HTML, "wb").write(data.encode("utf-8"))
print(f"\n共修 {total} 处")

# ---- 校验 ----
g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
print("\n" + "=" * 90)
print("校验")
print("=" * 90)
m = re.search(r'<<widget "relation-box">>(.*?)<</widget>>', g2, re.S)
wb = m.group(1) if m else ""
bad = 0
for mm in re.finditer(r"<<if\b(.*?)>>", wb):
    body = mm.group(1)
    s = re.sub(r'"[^"]*"', lambda x: " " * len(x.group(0)), body)
    s = re.sub(r"'[^']*'", lambda x: " " * len(x.group(0)), s)
    s = re.sub(r"`[^`]*`", lambda x: " " * len(x.group(0)), s)
    if "<" in s:
        bad += 1
        print(f"  ❌ 仍有: {mm.group(0)[:200]!r}")
print(f"  relation-box 里 <<if>> 含 < : {bad}")

print(f"\n  残留 <<NPC_CN_NAME (宏调用形式): {len(re.findall(r'<<NPC_CN_NAME ', g2))}")
print(f"  setup.NPC_CN_NAME( 总数: {g2.count('setup.NPC_CN_NAME(')}")
print(f"  passage: {len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML,'rb').read().decode('utf-8','replace')))}")

# ---- 全局扫：所有 <<if>> 里含 << 的 ----
print("\n" + "=" * 90)
print("全局：所有 <<if>>/<<elseif>> 里含 < 的（排除字符串）")
print("=" * 90)
n_all = 0
for mm in re.finditer(r"<<(?:if|elseif)\b(.*?)>>", g2):
    body = mm.group(1)
    s = re.sub(r'"[^"]*"', lambda x: " " * len(x.group(0)), body)
    s = re.sub(r"'[^']*'", lambda x: " " * len(x.group(0)), s)
    s = re.sub(r"`[^`]*`", lambda x: " " * len(x.group(0)), s)
    if "<" in s:
        n_all += 1
        if n_all <= 10:
            print(f"  @{mm.start()}: {mm.group(0)[:220]!r}")
print(f"  共 {n_all} 处")
