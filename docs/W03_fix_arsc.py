"""W03：修复 resources.arsc 被压缩的问题（必须 STORED + 4 字节对齐）。"""
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
MOD = os.path.join(OUT, "DoL-Lyra-0.5.12.13-CHS-modded.apk")
VAN = os.path.join(OUT, "DoL-Lyra-0.5.12.13-CHS-vanilla.apk")

# Android 要求「必须 STORED」的文件
MUST_STORE = {"resources.arsc"}
# Android 要求「4 字节对齐」的前缀
ALIGN_PREFIX = ("assets/", "lib/", "res/")

print("=" * 90)
print("对比 vanilla 与 modded 的压缩方法差异")
print("=" * 90)
vz = zipfile.ZipFile(VAN)
mz = zipfile.ZipFile(MOD)
vmap = {i.filename: i.compress_type for i in vz.infolist()}
mmap = {i.filename: i.compress_type for i in mz.infolist()}

diffs = []
for n in mz.namelist():
    if n in vmap and vmap[n] != mmap.get(n):
        diffs.append((n, vmap[n], mmap.get(n)))
print(f"压缩方法不一致的文件: {len(diffs)}")
for n, a, b in diffs[:15]:
    print(f"  {n:<50} vanilla={a} modded={b}")
vz.close()

print("\n" + "=" * 90)
print("重建 unsigned：resources.arsc 强制 STORED")
print("=" * 90)

src = zipfile.ZipFile(MOD)
DROP = [n for n in src.namelist() if n.startswith("META-INF/") and
        (n.endswith(".version") or n.endswith(".properties"))]
drop_set = set(DROP)

fixed_unsigned = os.path.join(WORK, "candidates", "fixed_unsigned.apk")
os.makedirs(os.path.dirname(fixed_unsigned), exist_ok=True)

changed = []
with zipfile.ZipFile(fixed_unsigned, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in src.infolist():
        n = info.filename
        if n in drop_set:
            continue
        data = src.read(n)

        # 决定压缩方式
        if n in MUST_STORE:
            ct = zipfile.ZIP_STORED
        elif info.compress_type in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
            ct = info.compress_type
        else:
            ct = zipfile.ZIP_DEFLATED

        if ct != info.compress_type:
            changed.append((n, info.compress_type, ct))

        zi = zipfile.ZipInfo(n, date_time=info.date_time)
        zi.compress_type = ct
        zi.external_attr = info.external_attr
        zi.create_system = info.create_system
        zo.writestr(zi, data)
src.close()

print(f"  改了 {len(changed)} 个文件的压缩方式:")
for n, a, b in changed:
    print(f"    {n:<50} {a} -> {b}")
print(f"  ✅ unsigned {os.path.getsize(fixed_unsigned)/1048576:.2f} MB")

print("\n" + "=" * 90)
print("重签")
print("=" * 90)
out_dir = os.path.join(WORK, "candidates", "signed_fixed")
if os.path.exists(out_dir):
    shutil.rmtree(out_dir, ignore_errors=True)
r = subprocess.run([
    "java", "-jar", SIGNER, "-a", fixed_unsigned, "--out", out_dir,
    "-ks", KS, "--ksAlias", "dol", "--ksKeyPass", os.environ["DOL_KS_PASS"], "--ksPass", os.environ["DOL_KS_PASS"],
], capture_output=True, text=True, encoding="utf-8", errors="replace")
for line in ((r.stdout or "") + (r.stderr or "")).split("\n"):
    if any(k in line for k in ("signature", "zipalign", "Successfully", "ERROR")):
        print("  " + line.strip())

signed = os.path.join(out_dir, "fixed_unsigned-aligned-signed.apk")
if not os.path.exists(signed):
    print(f"  ❌ 未找到 {signed}")
    raise SystemExit(1)

dst = os.path.join(TESTDIR, "5_候选E_修复resources_arsc.apk")
shutil.copy2(signed, dst)
h = hashlib.sha256(open(dst, "rb").read()).hexdigest().upper()
print(f"\n  ✅ {os.path.basename(dst)}  ({os.path.getsize(dst)/1048576:.2f} MB)")
print(f"     SHA256 {h}")

# 验证
print("\n" + "=" * 90)
print("验证")
print("=" * 90)
z = zipfile.ZipFile(dst)
for n in ("resources.arsc", "assets/www/index.html", "classes.dex"):
    i = z.getinfo(n)
    m = {0: "STORED", 8: "DEFLATE"}.get(i.compress_type, i.compress_type)
    print(f"  {n:<28} {m}")
print(f"  ZIP 条目 {len(z.namelist()):,}")
print(f"  testzip {'OK' if z.testzip() is None else 'BAD'}")
