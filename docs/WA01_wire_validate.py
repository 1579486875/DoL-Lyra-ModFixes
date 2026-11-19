# -*- coding: utf-8 -*-
"""把 validate.py 接入 build.py 的最后一步。"""
import re

P = r"E:\TAML\_dol\work\build.py"
s = open(P, encoding="utf-8").read()

OLD = '''    # 汇报
    final = os.path.join(OUT, "DoL-Lyra-0.5.12.13-CHS-modded.apk")'''

NEW = '''    # 7) 守门员
    print("\\n[7/7 守门员 validate.py]", flush=True)
    vr = subprocess.run([sys.executable, os.path.join(W, "validate.py")],
                        cwd=W, capture_output=True, text=True,
                        encoding="utf-8", errors="replace")
    tail = (vr.stdout or "").strip().split("\\n")
    for line in tail[-12:]:
        print("  " + line)
    if vr.returncode != 0:
        print("\\n⚠️ 守门员报告问题（见上），请人工确认后再分发")
    else:
        print("\\n✅ 守门员全部通过")

    # 汇报
    final = os.path.join(OUT, "DoL-Lyra-0.5.12.13-CHS-modded.apk")'''

if OLD in s and "[7/7 守门员" not in s:
    s = s.replace(OLD, NEW, 1)
    open(P, "w", encoding="utf-8").write(s)
    print("✅ validate.py 已接入 build.py")
else:
    print("（已存在或未找到锚点）")
