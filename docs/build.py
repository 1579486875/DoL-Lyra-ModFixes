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
KEYSTORE = os.path.join(W, "dol_sha256.jks")   # SHA256withRSA（旧 dol.jks 是 SHA384，HarmonyOS 拒装）


def _keystore_pass():
    """签名口令不写进脚本（第13轮：GitGuardian 报口令随脚本副本进了公开仓库）。
    优先读环境变量 DOL_KS_PASS，否则读本机文件 work\\keystore.local（不入库、不复制进 repo）。"""
    v = os.environ.get("DOL_KS_PASS")
    if v:
        return v
    p = os.path.join(W, "keystore.local")
    if os.path.exists(p):
        return open(p, encoding="utf-8").read().strip()
    print("❌ 缺少签名口令：请设置环境变量 DOL_KS_PASS，或在 work\\keystore.local 写入口令")
    sys.exit(1)


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

    # 1) 重建 index（BUILD_SKIP_ALL=1 时跳过：用于先单独跑 build_all.py 并保留完整日志）
    if os.environ.get("BUILD_SKIP_ALL") == "1":
        print("\n[1/6 重建 index] 跳过（BUILD_SKIP_ALL=1，使用已有 index_modded6.html）", flush=True)
    else:
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
            zi.compress_type = zipfile.ZIP_STORED if info.filename in ('resources.arsc',) else info.compress_type  # resources.arsc 必须 STORED
            zi.external_attr = info.external_attr
            zo.writestr(zi, data)
    z.close()
    open(dst, "wb").write(buf.getvalue())
    print(f"  ✅ {os.path.getsize(dst)/1048576:.2f} MB")

    # 5) 签名
    sign_dir = os.path.join(W, f"signed_{stamp}")
    _kp = _keystore_pass()
    run(["java", "-jar", SIGNER, "-a", "build_next_unsigned.apk",
         "--out", f"signed_{stamp}",
         "-ks", KEYSTORE, "--ksAlias", "dol",
         "--ksKeyPass", _kp, "--ksPass", _kp],
        "5/6 签名")

    signed = os.path.join(sign_dir, "build_next_unsigned-aligned-signed.apk")
    if not os.path.exists(signed):
        print(f"❌ 签名产物未找到: {signed}")
        sys.exit(1)

    # 6) 部署前验证（第12轮：改为「先验后发」——任何一项失败都不归档、不覆盖 out/）
    #    旧流程是先覆盖 out/ 再跑回归，且回归/守门员失败只告警 —— 坏包照样会被部署。
    env = dict(os.environ, DOL_APK=signed)
    gates = [
        ("6a/8 回归测试 REGRESS_ALL.py", [sys.executable, os.path.join(W, "REGRESS_ALL.py")], 6),
        ("6b/8 守门员 validate.py", [sys.executable, os.path.join(W, "validate.py")], 10),
        ("6c/8 真实执行验证 exec_verify.py", [sys.executable, os.path.join(W, "exec_verify.py"), signed], 12),
        ("6d/8 运行时验证门 RT_GATE.py（浏览器加载整包）", [sys.executable, os.path.join(W, "RT_GATE.py"), signed], 12),
    ]
    for desc, cmd, ntail in gates:
        print(f"\n[{desc}]", flush=True)
        vr = subprocess.run(cmd, cwd=W, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", env=env)
        for line in (vr.stdout or "").strip().split("\n")[-ntail:]:
            print("  " + line)
        if vr.returncode != 0:
            print("\n" + "!" * 70)
            print(f"❌ {desc} 失败（exit {vr.returncode}）—— 不归档、不覆盖 out/，旧包保持不变")
            print("   未部署的产物：" + signed)
            print("!" * 70)
            sys.exit(1)
        print(f"  ✅ 通过")

    # 7) 归档 + 部署（只有全部验证通过才会走到这里）
    print("\n[7/8 归档 + 部署]", flush=True)
    run([sys.executable, os.path.join(W, "RC01_auto_archive.py"), signed, note],
        "归档", cwd=W)
    shutil.copy2(signed, os.path.join(OUT, "DoL-Lyra-0.5.12.13-CHS-modded.apk"))

    # 8) 部署后复核：out/ 里的包与验证过的包逐字节一致
    final = os.path.join(OUT, "DoL-Lyra-0.5.12.13-CHS-modded.apk")
    h_signed = hashlib.sha256(open(signed, "rb").read()).hexdigest().upper()
    h = hashlib.sha256(open(final, "rb").read()).hexdigest().upper()
    if h != h_signed:
        print(f"❌ 部署后哈希不一致: {h} != {h_signed}")
        sys.exit(1)

    # 汇报
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
