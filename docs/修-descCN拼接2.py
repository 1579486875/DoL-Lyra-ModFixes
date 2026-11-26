# -*- coding: utf-8 -*-
"""修 descCN —— 直接改 work\\index_modded6.html（打包流程的权威源）。

之前的 DoL-descCN.apk 改的是 out\\ 里的旧 index，work 里的改动没进去，作废。
"""
import re

P = r"E:\TAML\_dol\work\index_modded6.html"
h = open(P, encoding="utf-8").read()

if "DESCCN_CONCAT_FIX" in h:
    print("⚠ 已修过，跳过")
    raise SystemExit(0)

OLD = "        // 复合词：按 _ 或空格拆开逐个译\n        if (/[_\\s]/.test(s)) {"

NEW = '''        /* DESCCN_CONCAT_FIX: 处理 "ruggedman" / "slimgirl" 这类
           体型词与性别词直接拼接、既无下划线也无空格的形式。
           例：ruggedman -> 粗犷 + 男人 = 粗犷男人
               slimwoman -> 纤细 + 女人 = 纤细女人
           只在整串恰好 = 体型词 + 性别词时生效，避免误伤普通英文单词。 */
        var _CONCAT_HEAD = /^(tall|short|average|thin|slim|slender|curvy|plump|chubby|muscular|toned|athletic|fat|skinny|stocky|petite|slight|lanky|lissome|lithe|trim|lean|taut|bulky|broad|robust|rugged|willowy|statuesque|sturdy|wiry|compact|big|brutish|burly|fit|graceful|heavyset|lush|mousy|plush|shapely|voluptuous|thick)(man|woman|boy|girl|person|human)$/i;
        var _cm = _CONCAT_HEAD.exec(s);
        if (_cm) {
            var _h = _cm[1].toLowerCase(), _t = _cm[2].toLowerCase();
            var _hcn = Object.prototype.hasOwnProperty.call(_DESC, _h) ? _DESC[_h] : _cm[1];
            var _tcn = Object.prototype.hasOwnProperty.call(_DESC, _t) ? _DESC[_t] : _cm[2];
            return _hcn + _tcn;
        }
        // 复合词：按 _ 或空格拆开逐个译
        if (/[_\\s]/.test(s)) {'''

if OLD not in h:
    print("❌ 未找到精确锚点，尝试宽松匹配")
    m = re.search(r"// 复合词[^\n]*\n(\s*)if \(/\[_\\s\]/\.test\(s\)\) \{", h)
    if not m:
        print("  列出所有 descCN 相关行：")
        for mm in re.finditer(r"复合词", h):
            print("   @%d: %s" % (mm.start(), h[max(0, mm.start() - 100):mm.start() + 150].replace("\n", " ")[:250]))
        raise SystemExit(1)
    h2 = h[:m.start()] + NEW + h[m.start() + len(m.group(0)):]
else:
    h2 = h.replace(OLD, NEW, 1)

assert h2 != h
open(P, "w", encoding="utf-8").write(h2)

print("✅ 已插入 DESCCN_CONCAT_FIX")
print("   _CONCAT_HEAD:", h2.count("_CONCAT_HEAD"))
print("   descCN 定义:", h2.count("function descCN"))
print("   index: %d -> %d 字符" % (len(h), len(h2)))

# 同时校验 CHEAT_FACE_FIX_V2 和 ARTICLE_FIX 在不在
for k in ("CHEAT_FACE_FIX_V2", "ARTICLE_FIX", "articleFix", "POSSESSIVE_FIX"):
    print("   %-22s %s" % (k, "✅" if k in h2 else "❌"))
