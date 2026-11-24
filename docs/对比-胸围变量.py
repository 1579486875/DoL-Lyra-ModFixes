# -*- coding: utf-8 -*-
"""对比原版/我们：确认「两套胸围变量不一致」是不是原版就有。"""
import re
import zipfile

APKS = [
    ("原版基础", r"E:\TAML\_dol\apk\对照-基础版-无美化.apk"),
    ("我们", r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"),
]

for label, path in APKS:
    z = zipfile.ZipFile(path)
    h = z.read("assets/www/index.html").decode("utf-8", "replace")

    print("\n" + "=" * 60)
    print("【%s】" % label)
    print("=" * 60)

    # 1) JS: T.modeloptions.breast_size 用哪个
    m1 = re.search(r"T\.modeloptions\.breast_size\s*=\s*breastSizeMap\[([^\]]+)\]", h)
    print("  JS T.modeloptions.breast_size <- %s" % (m1.group(1) if m1 else "?"))
    # 2) JS: options.breastSize <- ?
    m2 = re.search(r"options\.breastSize\s*=\s*Math\.clamp\(breastSize, 0, 4\)", h)
    m3 = re.search(r"const breastSize = Math\.round\(([^)]+)\)", h)
    print("  JS options.breastSize <- %s" % (m3.group(1) if m3 else "?"))
    # 3) Twee: _breastSize 用哪个
    m4 = re.search(r"<<switch \$player\.(perceived_)?breastsize>>", h)
    print("  Twee _breastSize  <- switch $player.%sbreastsize" % (m4.group(1) or "" if m4 else "?"))
    # 4) _modeloptions.breast_size
    m5 = re.search(r"_modeloptions\.breast_size\s*=\s*([^\s<]+)", h)
    print("  Twee _modeloptions.breast_size <- %s" % (m5.group(1) if m5 else "?"))

    # 5) 统计
    print("  perceived_breastsize 出现: %d" % len(re.findall(r"perceived_breastsize", h)))
    print("  $player.breastsize 出现: %d" % len(re.findall(r"\$player\.breastsize", h)))
