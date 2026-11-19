"""U06：部署 SHA256 重签包 + 归档旧包 + 更新 build.py。"""
import hashlib
import os
import shutil
import subprocess
import sys
from datetime import datetime

WORK = r"E:\TAML\_dol\work"
OUT = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
ARCHIVE = r"E:\TAML\_dol\archive"
NEW = os.path.join(WORK, "signed_sha256", "build_next_unsigned-aligned-signed.apk")

stamp = datetime.now().strftime("%Y%m%d-%H%M%S")

# 1) 备份旧包
if os.path.exists(OUT):
    old_h = hashlib.sha256(open(OUT, "rb").read()).hexdigest().upper()[:8]
    bak = os.path.join(ARCHIVE, f"DoL-Lyra-0.5.12.13-CHS-modded_{stamp}_SHA384签名_SHA{old_h}.apk")
    shutil.copy2(OUT, bak)
    print(f"✅ 旧包已备份: {os.path.basename(bak)}")

# 2) 部署新包
shutil.copy2(NEW, OUT)
h = hashlib.sha256(open(OUT, "rb").read()).hexdigest().upper()
sz = os.path.getsize(OUT) / 1048576
print(f"✅ 新包已部署: {sz:.2f} MB  SHA256 {h}")

# 3) 归档新包
arc = os.path.join(ARCHIVE, f"DoL-Lyra-0.5.12.13-CHS-modded_{stamp}_SHA256签名_可安装.apk")
shutil.copy2(NEW, arc)
print(f"✅ 新包已归档: {os.path.basename(arc)}")

# 4) 更新 build.py 用新 keystore
bp = os.path.join(WORK, "build.py")
s = open(bp, encoding="utf-8").read()
if "dol_sha256.jks" not in s:
    s = s.replace('KEYSTORE = os.path.join(W, "dol.jks")',
                  'KEYSTORE = os.path.join(W, "dol_sha256.jks")   # SHA256withRSA（旧 dol.jks 是 SHA384，HarmonyOS 拒装）')
    open(bp, "w", encoding="utf-8").write(s)
    print("✅ build.py 已切换到 dol_sha256.jks")
else:
    print("（build.py 已用 dol_sha256.jks）")

# 5) 验证
print("\n" + "=" * 90)
print("最终验证")
print("=" * 90)
r = subprocess.run(["keytool", "-printcert", "-jarfile", OUT],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
out = (r.stdout or "") + (r.stderr or "")
print("  签名算法 SHA256withRSA:", "SHA256withRSA" in out)
print("  签名算法 SHA384withRSA:", "SHA384withRSA" in out)

import zipfile
z = zipfile.ZipFile(OUT)
print(f"  ZIP 条目: {len(z.namelist()):,}")
print(f"  testzip: {'OK' if z.testzip() is None else 'BAD'}")
print(f"  index.html: {z.getinfo('assets/www/index.html').file_size/1048576:.2f} MB")
