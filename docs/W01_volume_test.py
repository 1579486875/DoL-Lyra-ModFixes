"""W01：区分「体积问题」还是「内容问题」。

候选 D：vanilla + 17 MB 填充数据，撑到 ~175 MB，重签
  - D 能装  -> 不是体积问题，是 modded 内容问题
  - D 装不上 -> 是体积问题（HarmonyOS 对 APK 大小或单文件大小有限制）
"""
import hashlib
import os
import shutil
import subprocess
import zipfile

WORK = r"E:\TAML\_dol\work"
OUT = r"E:\TAML\_dol\out"
TESTDIR = os.path.join(OUT, "测试包")
SIGNER = os.path.join(WORK, "uber-apk-signer.jar")
KS = os.path.join(WORK, "dol_sha256.jks")
VAN = os.path.join(OUT, "DoL-Lyra-0.5.12.13-CHS-vanilla.apk")
MOD = os.path.join(OUT, "DoL-Lyra-0.5.12.13-CHS-modded.apk")

os.makedirs(TESTDIR, exist_ok=True)

print("=" * 90)
print("先看两个包的体积分布")
print("=" * 90)
for label, p in (("vanilla", VAN), ("modded", MOD)):
    z = zipfile.ZipFile(p)
    # 最大 10 个文件
    items = sorted(((i.file_size, i.filename) for i in z.infolist()), reverse=True)[:8]
    print(f"\n[{label}] {os.path.getsize(p)/1048576:.2f} MB, {len(z.namelist()):,} 条目")
    for sz, n in items:
        print(f"    {sz/1048576:>8.2f} MB  {n}")

print("\n" + "=" * 90)
print("D) vanilla + 17MB 填充，撑到 ~175 MB")
print("=" * 90)

src = zipfile.ZipFile(VAN)
DROP = [n for n in src.namelist() if n.startswith("META-INF/") and
        (n.endswith(".version") or n.endswith(".properties"))]
drop_set = set(DROP)

D_unsigned = os.path.join(WORK, "candidates", "candidateD_unsigned.apk")
os.makedirs(os.path.dirname(D_unsigned), exist_ok=True)

# 17 MB 不可压缩填充（随机字节，deflate 压不动）
FILLER_MB = 17
filler = os.urandom(FILLER_MB * 1024 * 1024)

with zipfile.ZipFile(D_unsigned, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in src.infolist():
        if info.filename in drop_set:
            continue
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zo.writestr(zi, src.read(info.filename))
    # 加填充
    zi = zipfile.ZipInfo("assets/filler.bin", date_time=(2026, 11, 20, 0, 0, 0))
    zi.compress_type = zipfile.ZIP_DEFLATED
    zo.writestr(zi, filler)
src.close()

usize = os.path.getsize(D_unsigned) / 1048576
print(f"  unsigned: {usize:.2f} MB（目标 ~175 MB）")

out_d = os.path.join(WORK, "candidates", "signedD")
if os.path.exists(out_d):
    shutil.rmtree(out_d, ignore_errors=True)
r = subprocess.run([
    "java", "-jar", SIGNER, "-a", D_unsigned, "--out", out_d,
    "-ks", KS, "--ksAlias", "dol", "--ksKeyPass", os.environ["DOL_KS_PASS"], "--ksPass", os.environ["DOL_KS_PASS"],
], capture_output=True, text=True, encoding="utf-8", errors="replace")
for line in ((r.stdout or "") + (r.stderr or "")).split("\n"):
    if any(k in line for k in ("signature", "zipalign", "Successfully", "ERROR")):
        print("  " + line.strip())

D = os.path.join(out_d, "candidateD_unsigned-aligned-signed.apk")
if os.path.exists(D):
    dst = os.path.join(TESTDIR, "4_候选D_原版撑到175MB.apk")
    shutil.copy2(D, dst)
    print(f"  ✅ {os.path.basename(dst)}  ({os.path.getsize(dst)/1048576:.2f} MB)")
    print(f"     SHA256 {hashlib.sha256(open(dst,'rb').read()).hexdigest().upper()}")

print("\n" + "=" * 90)
print("E) modded 去掉假想的大文件（做减法对照）")
print("=" * 90)
z2 = zipfile.ZipFile(MOD)
big = sorted(((i.file_size, i.filename) for i in z2.infolist()), reverse=True)[:3]
print("  modded 最大 3 个文件:")
for sz, n in big:
    print(f"    {sz/1048576:>8.2f} MB  {n}")
print("  （如果 D 装不上，就要考虑是不是 index.html 100MB 超限）")
