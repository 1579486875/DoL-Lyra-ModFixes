"""AX01（第13轮）：仓库提交前的密钥扫描 / 脱敏（GitGuardian 报签名口令进了公开仓库之后建立）。

用法:
  python AX01_secret_scan.py <目录>            只扫描，发现就 exit 1
  python AX01_secret_scan.py <目录> --redact   把已知口令替换成占位符后再扫描
扫描内容：
  ① 本机 work\\keystore.local 里的口令原文（不在本脚本里写明文）；
  ② keytool / apksigner / uber-apk-signer 的口令参数后面跟着的字面值；
  ③ 密钥库 / 证书文件（.jks .keystore .p12 .pfx）。
"""
import os
import re
import sys

W = os.path.dirname(os.path.abspath(__file__))
root = sys.argv[1]
redact = "--redact" in sys.argv
secret = open(os.path.join(W, "keystore.local"), encoding="utf-8").read().strip()
PLACE_CODE = 'os.environ["DOL_KS_PASS"]'
PLACE_TEXT = "<签名口令：见本机 work\\keystore.local，不入库>"
ARG = re.compile(r"(-storepass|-keypass|--ksPass|--ksKeyPass|--ks-pass|--key-pass)\s+(?!<|\$|_kp|os\.)(\S+)")
hits = []
for dp, dn, fn in os.walk(root):
    if ".git" in dp.split(os.sep):
        continue
    for f in fn:
        p = os.path.join(dp, f)
        if f.lower().endswith((".jks", ".keystore", ".p12", ".pfx")):
            hits.append((p, 0, "密钥库/证书文件"))
            continue
        if not f.lower().endswith((".py", ".js", ".md", ".txt", ".json", ".ps1", ".bat", ".sh", ".yml", ".yaml", ".html")):
            continue
        try:
            s = open(p, encoding="utf-8").read()
        except Exception:
            continue
        if redact and secret in s:
            if f.endswith(".py"):
                s = s.replace('"' + secret + '"', PLACE_CODE).replace("'" + secret + "'", PLACE_CODE)
                if PLACE_CODE in s and not re.search(r"^import os|^import .*\bos\b", s, re.M):
                    s = "import os\n" + s
            s = s.replace(secret, PLACE_TEXT)
            open(p, "w", encoding="utf-8", newline="").write(s)
        for i, line in enumerate(s.split("\n"), 1):
            if secret in line:
                hits.append((p, i, "口令原文"))
            for m in ARG.finditer(line):
                hits.append((p, i, "口令参数 %s %s" % (m.group(1), m.group(2)[:3] + "…")))
for h in hits:
    print("  ⚠ %s:%d  %s" % h)
print("[AX01] %s：%d 处" % ("扫描（已脱敏）" if redact else "扫描", len(hits)))
sys.exit(1 if hits else 0)
