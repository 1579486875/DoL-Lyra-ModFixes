"""V01：做多个候选包，逐一排除安装失败原因。

候选：
  A. 删掉 META-INF 下所有未受签名保护的文件（.version / .properties）
  B. 同时也删掉 .idsig（v4 签名附属文件）
  C. 纯净版：直接拿 vanilla 原包只改一个字节再重签（验证是不是包内容问题）
"""
import hashlib
import os
import shutil
import subprocess
import sys
import zipfile

WORK = r"E:\TAML\_dol\work"
UNSIGNED = os.path.join(WORK, "build_next_unsigned.apk")
OUTDIR = os.path.join(WORK, "candidates")
SIGNER = os.path.join(WORK, "uber-apk-signer.jar")
KS = os.path.join(WORK, "dol_sha256.jks")

os.makedirs(OUTDIR, exist_ok=True)

print("=" * 90)
print("A) 删掉 META-INF 下未受签名保护的元数据文件")
print("=" * 90)

src = zipfile.ZipFile(UNSIGNED)
names = src.namelist()

DROP = [n for n in names
        if n.startswith("META-INF/") and
        (n.endswith(".version") or n.endswith(".properties") or n.endswith(".idsig"))]
print(f"  要删 {len(DROP)} 个:")
for n in DROP[:6]:
    print(f"    {n}")
if len(DROP) > 6:
    print(f"    ... 还有 {len(DROP)-6} 个")

dst_a = os.path.join(OUTDIR, "candidateA.apk")
drop_set = set(DROP)
with zipfile.ZipFile(dst_a, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in src.infolist():
        if info.filename in drop_set:
            continue
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zo.writestr(zi, src.read(info.filename))
src.close()
print(f"  ✅ 已生成 {os.path.basename(dst_a)}  ({os.path.getsize(dst_a)/1048576:.2f} MB)")

print("\n" + "=" * 90)
print("B) 重新签名 A")
print("=" * 90)

out_b = os.path.join(OUTDIR, "signedA")
if os.path.exists(out_b):
    shutil.rmtree(out_b, ignore_errors=True)
r = subprocess.run([
    "java", "-jar", SIGNER, "-a", dst_a, "--out", out_b,
    "-ks", KS, "--ksAlias", "dol", "--ksKeyPass", os.environ["DOL_KS_PASS"], "--ksPass", os.environ["DOL_KS_PASS"],
], capture_output=True, text=True, encoding="utf-8", errors="replace")
out = (r.stdout or "") + (r.stderr or "")
for line in out.split("\n"):
    if any(k in line for k in ("signature", "zipalign", "Successfully", "ERROR", "warnings")):
        print("  " + line.strip())

signed_a = os.path.join(out_b, "candidateA-aligned-signed.apk")
if os.path.exists(signed_a):
    h = hashlib.sha256(open(signed_a, "rb").read()).hexdigest().upper()
    print(f"\n  ✅ {os.path.basename(signed_a)}  ({os.path.getsize(signed_a)/1048576:.2f} MB)")
    print(f"     SHA256 {h}")
else:
    print(f"  ❌ 未找到 {signed_a}")

print("\n" + "=" * 90)
print("验证 A 的签名")
print("=" * 90)
if os.path.exists(signed_a):
    rr = subprocess.run(["keytool", "-printcert", "-jarfile", signed_a],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
    o = (rr.stdout or "") + (rr.stderr or "")
    print("  SHA256withRSA:", "SHA256withRSA" in o)
    z = zipfile.ZipFile(signed_a)
    meta = [n for n in z.namelist() if n.startswith("META-INF/")]
    print(f"  META-INF: {len(meta)} 个 -> {[n.split('/')[-1] for n in meta]}")
    print(f"  ZIP 条目: {len(z.namelist()):,}")
    print(f"  testzip: {'OK' if z.testzip() is None else 'BAD'}")
