# -*- coding: utf-8 -*-
"""在 makeFn 兜底里加「直接查 NPCTypeList_cn_name」，解决 baker/bartender/chef 等漏译。"""
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))

OLD = """            /* [fallback] fullDescription 形如 "slim plantgirl"：拆成 描述词 + 物种 */"""
NEW = """            /* [fallback] 直接查物种/头衔表（makeFn 在 maplebirch 包装之外，最可靠） */
            try {
                var _st0 = window.setup;
                var _keys0 = ["NPCTypeList_cn_name", "NPCTitleList_cn_name"];
                for (var _ki = 0; _ki &lt; _keys0.length; _ki++) {
                    var _raw0 = _st0 && _st0[_keys0[_ki]];
                    if (typeof _raw0 !== "string") continue;
                    var _seg = _raw0.split("|");
                    for (var _si = 0; _si &lt; _seg.length; _si++) {
                        var _p0 = _seg[_si];
                        var _c0 = _p0.indexOf(",");
                        if (_c0 &lt; 0) continue;
                        if (_p0.slice(0, _c0).trim().toLowerCase() === k) return _p0.slice(_c0 + 1).trim();
                    }
                }
            } catch (e01) {}
            /* [fallback] fullDescription 形如 "slim plantgirl"：拆成 描述词 + 物种 */"""

if OLD not in raw:
    print("❌ 锚点未找到")
    sys.exit(1)

raw2 = raw.replace(OLD, NEW, 1)
print("已注入类型表直查兜底")

npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
print("passage:", npass, "->", npass2)
if npass2 != npass:
    sys.exit(1)
open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写入")
