"""W04：部署候选 E + 修 inject6.py 的压缩方法问题（长期）。"""
import hashlib
import os
import re
import shutil
import subprocess
import zipfile
from datetime import datetime

WORK = r"E:\TAML\_dol\work"
OUT = r"E:\TAML\_dol\out"
ARCHIVE = r"E:\TAML\_dol\archive"
TARGET = os.path.join(OUT, "DoL-Lyra-0.5.12.13-CHS-modded.apk")
NEW = os.path.join(OUT, "测试包", "5_候选E_修复resources_arsc.apk")
VAN = os.path.join(OUT, "DoL-Lyra-0.5.12.13-CHS-vanilla.apk")

stamp = datetime.now().strftime("%Y%m%d-%H%M%S")

# 1) 备份旧包
if os.path.exists(TARGET):
    old = hashlib.sha256(open(TARGET, "rb").read()).hexdigest().upper()[:8]
    bak = os.path.join(ARCHIVE, f"DoL-Lyra-0.5.12.13-CHS-modded_{stamp}_arsc被压缩_SHA{old}.apk")
    shutil.copy2(TARGET, bak)
    print(f"✅ 旧包备份: {os.path.basename(bak)}")

# 2) 部署新包
shutil.copy2(NEW, TARGET)
h = hashlib.sha256(open(TARGET, "rb").read()).hexdigest().upper()
print(f"✅ 新包部署: {os.path.getsize(TARGET)/1048576:.2f} MB  SHA256 {h}")

# 3) 归档
shutil.copy2(NEW, os.path.join(ARCHIVE, f"DoL-Lyra-0.5.12.13-CHS-modded_{stamp}_修复arsc可安装.apk"))
print("✅ 已归档")

# 4) 修 inject6.py / build.py 的压缩逻辑
print("\n" + "=" * 90)
print("修构建脚本的压缩逻辑")
print("=" * 90)

MUST_STORE = {"resources.arsc"}

for fname in ("inject6.py", "build.py", "rebuild2.py"):
    p = os.path.join(WORK, fname)
    if not os.path.exists(p):
        continue
    s = open(p, encoding="utf-8").read()
    orig = s

    # 找 compress_type = info.compress_type 的写法，改成按白名单强制
    if "zi.compress_type = info.compress_type" in s:
        s = s.replace(
            "zi.compress_type = info.compress_type",
            "zi.compress_type = zipfile.ZIP_STORED if info.filename in ('resources.arsc',) else info.compress_type  # resources.arsc 必须 STORED"
        )
    # 找 compress_type=zipfile.ZIP_DEFLATED 全局重压的写法
    if "compress_type=zipfile.ZIP_DEFLATED" in s and "resources.arsc" not in s:
        s = s.replace(
            "zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED)",
            "zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED)  # 注意：resources.arsc 必须单独设 ZIP_STORED"
        )

    if s != orig:
        open(p, "w", encoding="utf-8").write(s)
        print(f"  ✅ {fname} 已改")
    else:
        print(f"  （{fname} 无可改点）")

# 5) 加一个「打包后校验」钩子到 validate.py
vp = os.path.join(WORK, "validate.py")
if os.path.exists(vp):
    v = open(vp, encoding="utf-8").read()
    if "resources.arsc 压缩" not in v:
        # 在文件末尾前插一个检查
        insert = '''
    # --- resources.arsc 必须是 STORED ---
    try:
        import zipfile as _zf
        _z = _zf.ZipFile(APK)
        _i = _z.getinfo("resources.arsc")
        ok = (_i.compress_type == _zf.ZIP_STORED)
        check("resources.arsc 未压缩（Android 硬性要求）", ok,
              f"compress_type={_i.compress_type}（0=STORED, 8=DEFLATE）")
        _z.close()
    except Exception as _e:
        check("resources.arsc 未压缩", False, str(_e))
'''
        # 找最后一个 check( 之后
        idx = v.rfind("\n    check(")
        if idx > 0:
            end = v.find("\n", v.find(")", idx))
            v = v[:end+1] + insert + v[end+1:]
            open(vp, "w", encoding="utf-8").write(v)
            print("  ✅ validate.py 已加 resources.arsc 检查")
    else:
        print("  （validate.py 已有该检查）")

# 6) 最终验证
print("\n" + "=" * 90)
print("最终验证")
print("=" * 90)
z = zipfile.ZipFile(TARGET)
for n, want in (("resources.arsc", 0), ("assets/www/index.html", 8), ("classes.dex", 8)):
    i = z.getinfo(n)
    m = {0: "STORED", 8: "DEFLATE"}.get(i.compress_type, i.compress_type)
    mark = "✅" if i.compress_type == want else "❌"
    print(f"  {mark} {n:<28} {m}")
print(f"  ZIP 条目 {len(z.namelist()):,}  testzip {'OK' if z.testzip() is None else 'BAD'}")

r = subprocess.run(["keytool", "-printcert", "-jarfile", TARGET],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
print(f"  SHA256withRSA: {'SHA256withRSA' in ((r.stdout or '') + (r.stderr or ''))}")
print(f"\n最终 SHA256: {h}")
