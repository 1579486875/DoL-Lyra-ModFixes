# -*- coding: utf-8 -*-
"""修 descCN：处理 "ruggedman" / "slimgirl" 这类「体型词+性别词」无分隔符拼接。

现状：descCN 只按 `_` 或空格拆词，"ruggedman" 原样返回 → 战斗描述里出现英文。
修法：在拆分逻辑前加一条「体型词 + 性别词」的正则拆分。
"""
import re
import zipfile
import os

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
OUT = r"E:\TAML\_dol\work\DoL-descCN.apk"

z = zipfile.ZipFile(APK)
h = z.read("assets/www/index.html").decode("utf-8", "replace")

if "DESCCN_CONCAT_FIX" in h:
    print("⚠ 已修过，跳过")
    raise SystemExit(0)

OLD = '''        // 复合词：按 _ 或空格拆开逐个译
        if (/[_\\s]/.test(s)) {'''

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
    print("❌ 未找到锚点，尝试宽松匹配")
    m = re.search(r"// 复合词：按 _ 或空格拆开逐个译\s*\n\s*if \(/\[_\\s\]/\.test\(s\)\) \{", h)
    if not m:
        # 再宽一点，只用那行注释
        m = re.search(r"// 复合词[^\n]*\n(\s*)if \(", h)
    if not m:
        raise SystemExit("❌ 无法定位")
    s2 = h[:m.start()] + NEW + h[h.index("\n", m.start()) + 1:]
else:
    s2 = h.replace(OLD, NEW, 1)

assert s2 != h, "未替换"

# 校验
print("✅ 已插入 DESCCN_CONCAT_FIX")
print("   _CONCAT_HEAD 出现:", s2.count("_CONCAT_HEAD"))
print("   descCN 定义:", s2.count("function descCN"))

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as zo:
    for info in z.infolist():
        d = s2.encode("utf-8") if info.filename == "assets/www/index.html" else z.read(info.filename)
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zo.writestr(zi, d)

print("\n✅ 输出:", OUT, "%.2f MB" % (os.path.getsize(OUT) / 1024 / 1024))
print("   index: %d -> %d 字节" % (len(h), len(s2)))
