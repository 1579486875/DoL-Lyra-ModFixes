"""V02：部署候选 A + 生成候选 B（vanilla 最小改动再签），并排好让用户逐个试。"""
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

os.makedirs(TESTDIR, exist_ok=True)

print("=" * 90)
print("候选 A：删 META-INF 元数据 + SHA256 重签")
print("=" * 90)
A = os.path.join(WORK, "candidates", "signedA", "candidateA-aligned-signed.apk")
if os.path.exists(A):
    dst = os.path.join(TESTDIR, "1_候选A_精简METAINF.apk")
    shutil.copy2(A, dst)
    print(f"  ✅ {os.path.basename(dst)}  ({os.path.getsize(dst)/1048576:.2f} MB)")
    print(f"     SHA256 {hashlib.sha256(open(dst,'rb').read()).hexdigest().upper()}")

print("\n" + "=" * 90)
print("候选 B：vanilla 原包（只加一个无害注释条）重签")
print("=" * 90)
src = zipfile.ZipFile(VAN)
names = src.namelist()
DROP = [n for n in names if n.startswith("META-INF/") and
        (n.endswith(".version") or n.endswith(".properties"))]

B_unsigned = os.path.join(WORK, "candidates", "candidateB_unsigned.apk")
drop_set = set(DROP)
with zipfile.ZipFile(B_unsigned, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in src.infolist():
        if info.filename in drop_set:
            continue
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        data = src.read(info.filename)
        if info.filename == "assets/www/index.html":
            # 加一个无害的 HTML 注释（不改变游戏行为）
            data = data.replace(b"<html", b"<!-- probe --><html", 1)
        zo.writestr(zi, data)
src.close()
print(f"  ✅ unsigned {os.path.getsize(B_unsigned)/1048576:.2f} MB")

out_b = os.path.join(WORK, "candidates", "signedB")
if os.path.exists(out_b):
    shutil.rmtree(out_b, ignore_errors=True)
r = subprocess.run([
    "java", "-jar", SIGNER, "-a", B_unsigned, "--out", out_b,
    "-ks", KS, "--ksAlias", "dol", "--ksKeyPass", os.environ["DOL_KS_PASS"], "--ksPass", os.environ["DOL_KS_PASS"],
], capture_output=True, text=True, encoding="utf-8", errors="replace")
for line in ((r.stdout or "") + (r.stderr or "")).split("\n"):
    if any(k in line for k in ("signature", "zipalign", "Successfully", "ERROR")):
        print("  " + line.strip())

B = os.path.join(out_b, "candidateB_unsigned-aligned-signed.apk")
if os.path.exists(B):
    dst = os.path.join(TESTDIR, "2_候选B_原版最小改动.apk")
    shutil.copy2(B, dst)
    print(f"  ✅ {os.path.basename(dst)}  ({os.path.getsize(dst)/1048576:.2f} MB)")
    print(f"     SHA256 {hashlib.sha256(open(dst,'rb').read()).hexdigest().upper()}")

print("\n" + "=" * 90)
print("候选 C：vanilla 原包原样复制（Lyra 官方签名，完全没动）")
print("=" * 90)
dst = os.path.join(TESTDIR, "3_候选C_原版未改.apk")
shutil.copy2(VAN, dst)
print(f"  ✅ {os.path.basename(dst)}  ({os.path.getsize(dst)/1048576:.2f} MB)")
print(f"     SHA256 {hashlib.sha256(open(dst,'rb').read()).hexdigest().upper()}")
print("     （这是 Lyra 官方原包，签名 A0:04:92，如果它也装不上，就是手机侧限制）")

print("\n" + "=" * 90)
print("测试包目录")
print("=" * 90)
for f in sorted(os.listdir(TESTDIR)):
    p = os.path.join(TESTDIR, f)
    print(f"  {f}  ({os.path.getsize(p)/1048576:.2f} MB)")
