"""DoL 整合包一键构建 + 自动归档。

用法：
    python build.py "说明文字"

步骤：
    1. build_all.py       重建 index（模组数组 + 翻译 + 补丁）
    2. rebuild2.py        打包 APK
    3. apply_all_patches  返回键 / harmony / 金币图
    4. 补 iris 图          foxy / gloomy / makeup 的 iris.png
    5. 签名                uber-apk-signer
    6. 归档 + 部署         复制到 archive/（不覆盖）+ 覆盖 out/ 最新版
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime

W = r"E:\TAML\_dol\work"
OUT = r"E:\TAML\_dol\out"
ARCHIVE = r"E:\TAML\_dol\archive"
SIGNER = os.path.join(W, "uber-apk-signer.jar")
KEYSTORE = os.path.join(W, "dol.jks")


def run(cmd, desc, cwd=None):
    print(f"\n[{desc}]", flush=True)
    r = subprocess.run(cmd, cwd=cwd or W, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    tail = (r.stdout or "").strip().split("\n")[-6:]
    for line in tail:
        print("  " + line)
    if r.returncode != 0:
        print(f"  ❌ 失败 (exit {r.returncode})")
        print((r.stderr or "")[:600])
        sys.exit(1)
    return r


def main():
    note = sys.argv[1] if len(sys.argv) > 1 else ""
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    # 1) 重建 index
    run([sys.executable, os.path.join(W, "build_all.py")], "1/6 重建 index")

    # 2) 打包
    os.environ["NEWHTML"] = os.path.join(W, "index_modded6.html")
    run([sys.executable, os.path.join(W, "rebuild2_fast.py")], "2/6 打包 APK（图片 STORED 加速）")

    # 3) 补丁
    run([sys.executable, os.path.join(W, "apply_all_patches.py")], "3/6 应用补丁")

    # 4) 补 iris 图
    print("\n[4/6 补 iris 图]", flush=True)
    src = os.path.join(W, "build6_unsigned.apk")
    dst = os.path.join(W, "build_next_unsigned.apk")
    z = zipfile.ZipFile(src)
    iris = z.read("assets/www/img/face/default/default/iris.png")
    REP = ["assets/www/img/face/default/foxy/iris.png",
           "assets/www/img/face/default/gloomy/iris.png",
           "assets/www/img/face/default/makeup/iris.png"]
    import io
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
        for info in z.infolist():
            data = iris if info.filename in REP else z.read(info.filename)
            zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
            zi.compress_type = info.compress_type
            zi.external_attr = info.external_attr
            zo.writestr(zi, data)
    z.close()
    open(dst, "wb").write(buf.getvalue())
    print(f"  ✅ {os.path.getsize(dst)/1048576:.2f} MB")

    # 5) 签名
    sign_dir = os.path.join(W, f"signed_{stamp}")
    run(["java", "-jar", SIGNER, "-a", "build_next_unsigned.apk",
         "--out", f"signed_{stamp}",
         "-ks", KEYSTORE, "--ksAlias", "dol",
         "--ksKeyPass", "dolchs", "--ksPass", "dolchs"],
        "5/6 签名")

    signed = os.path.join(sign_dir, "build_next_unsigned-aligned-signed.apk")
    if not os.path.exists(signed):
        print(f"❌ 签名产物未找到: {signed}")
        sys.exit(1)

    # 6) 归档 + 部署
    print("\n[6/6 归档 + 部署]", flush=True)
    run([sys.executable, os.path.join(W, "RC01_auto_archive.py"), signed, note],
        "归档", cwd=W)
    shutil.copy2(signed, os.path.join(OUT, "DoL-Lyra-0.5.12.13-CHS-modded.apk"))

    # 7) 守门员
    print("\n[7/7 守门员 validate.py]", flush=True)
    vr = subprocess.run([sys.executable, os.path.join(W, "validate.py")],
                        cwd=W, capture_output=True, text=True,
                        encoding="utf-8", errors="replace")
    tail = (vr.stdout or "").strip().split("\n")
    for line in tail[-12:]:
        print("  " + line)
    if vr.returncode != 0:
        print("\n⚠️ 守门员报告问题（见上），请人工确认后再分发")
    else:
        print("\n✅ 守门员全部通过")

    # 8) 真实执行验证（失败阻止分发）
    print("\n[8/8 真实执行验证 exec_verify.py]", flush=True)
    vr = subprocess.run([sys.executable, os.path.join(W, "exec_verify.py")],
                        cwd=W, capture_output=True, text=True,
                        encoding="utf-8", errors="replace")
    for line in (vr.stdout or "").strip().split("\n")[-14:]:
        print("  " + line)
    if vr.returncode != 0:
        print("\n" + "!" * 70)
        print("❌ 真实执行验证失败 —— 生成的 APK 不可分发")
        print("   上面列出的 setup 函数没有真的挂载，游戏里会报 'is not a function'")
        print("!" * 70)
        sys.exit(1)
    print("\n✅ 真实执行验证通过（函数真的挂载了，调用返回中文）")

    # 汇报
    final = os.path.join(OUT, "DoL-Lyra-0.5.12.13-CHS-modded.apk")
    h = hashlib.sha256(open(final, "rb").read()).hexdigest().upper()
    print("\n" + "=" * 70)
    print("✅ 构建完成")
    print("=" * 70)
    print(f"  最新包 : {final}")
    print(f"  大小   : {os.path.getsize(final)/1048576:.2f} MB")
    print(f"  SHA256 : {h}")
    print(f"  归档   : {ARCHIVE}")
    n = len([f for f in os.listdir(ARCHIVE) if f.endswith(".apk")])
    print(f"  历史包 : {n} 个")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
