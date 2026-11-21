# -*- coding: utf-8 -*-
"""CUR17: 把 r6 包里被"解实体"破坏的两个明文 JS 块换回黄金基线的原始块。

只替换 <script> 明文块（passage 正文不动）：
  #3  webpack BeforeSC2（4.6MB，无 id）
  #11 script-sugarcube（SugarCube 引擎）

用法: python CUR17_restore_engine.py
输出: E:\TAML\_dol\work\index_modded6.html
"""
import hashlib
import re
import sys
import zipfile

GOLDEN = r"E:\TAML\_dol\archive\DoL-Lyra-0.5.12.13-CHS-modded_20261120-061313_修复arsc可安装.apk"
BASE = r"E:\TAML\_dol\out\backups\DoL-Lyra-0.5.12.13-CHS-modded.apk.backup_r6_190337"
OUT = r"E:\TAML\_dol\work\index_modded6.html"

PAT = re.compile(r'<script\b([^>]*)>(.*?)</script>', re.S)


def load(p):
    return zipfile.ZipFile(p).read("assets/www/index.html").decode("utf-8", "replace")


def md5(s):
    return hashlib.md5(s.encode("utf-8", "replace")).hexdigest()


gold = load(GOLDEN)
base = load(BASE)

gb = list(PAT.finditer(gold))
bb = list(PAT.finditer(base))
print("golden blocks=%d  base blocks=%d" % (len(gb), len(bb)))
if len(gb) != len(bb):
    print("❌ 块数不一致，停止")
    sys.exit(1)

# 安全检查：只允许替换 index 3 / 11，且 golden 对应块必须比 base 多实体
targets = []
for i in (3, 11):
    ga, gc = gb[i].group(1), gb[i].group(2)
    ba, bc = bb[i].group(1), bb[i].group(2)
    gq, bq = gc.count("&quot;"), bc.count("&quot;")
    gn, bn = len(re.findall(r"&#\d+;", gc)), len(re.findall(r"&#\d+;", bc))
    print("  block %-2d attrs=%-40s golden(quot=%d,num=%d) base(quot=%d,num=%d)" %
          (i, ga.strip()[:40], gq, gn, bq, bn))
    if gq <= bq and gn <= bn:
        print("    ⚠ 该块没有实体丢失，跳过")
        continue
    targets.append((i, gb[i].start(), gb[i].end(), gc))

if not targets:
    print("无需替换")
    sys.exit(0)

# 从后往前替换，避免偏移失效
new = base
for i, s, e, gc in sorted(targets, key=lambda x: -x[1]):
    bs, be = bb[i].start(), bb[i].end()
    new = new[:bs] + PAT.sub(lambda m: m.group(0), "<script" + gb[i].group(1) + ">" + gc + "</script>", count=0)[:0] + new[bs:]  # no-op guard
    new = new[:bs] + "<script" + gb[i].group(1) + ">" + gc + "</script>" + new[be:]

# 校验
nb = list(PAT.finditer(new))
ok = True
for i, _, _, gc in targets:
    same = nb[i].group(2) == gc
    print("  block %-2d restored: %s  md5=%s" % (i, "OK" if same else "FAIL", md5(nb[i].group(2))[:10]))
    ok = ok and same
if not ok:
    print("❌ 替换校验失败")
    sys.exit(1)

# 结构安全阀
npass = len(re.findall(r'<tw-passagedata[^>]*name="', new))
print("passage after: %d (expect 16088)" % npass)
if npass != 16088:
    print("❌ passage 数异常")
    sys.exit(1)

open(OUT, "wb").write(new.encode("utf-8"))
print("✅ 写入", OUT, len(new), "bytes")
