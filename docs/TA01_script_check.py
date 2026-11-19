"""找出 variablesStatic 里所有 <<script>> 块，逐个用 Node 语法检查。"""
import html
import os
import re
import subprocess
import tempfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
TMP = os.path.join(tempfile.gettempdir(), "dsh_script_check.js")

g = html.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))

# 取 variablesStatic passage
m = re.search(r'<tw-passagedata[^>]*name="Widgets variablesStatic"[^>]*>(.*?)</tw-passagedata>',
              open(HTML, "rb").read().decode("utf-8", "replace"), re.S)
body = html.unescape(m.group(1)) if m else ""
print(f"Widgets variablesStatic 长度: {len(body)}")

# 提取所有 <<script>>...</script>>
scripts = re.findall(r"<<script>>(.*?)<</script>>", body, re.S)
print(f"<<script>> 块数: {len(scripts)}")

ok_n = bad_n = 0
for i, s in enumerate(scripts):
    open(TMP, "w", encoding="utf-8").write(s)
    r = subprocess.run(["node", "--check", TMP], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode == 0:
        ok_n += 1
    else:
        bad_n += 1
        err = (r.stderr or "").strip().split("\n")
        print(f"\n❌ 第 {i+1} 个 <<script>> 语法错误:")
        for line in err[:6]:
            print(f"    {line}")
        print(f"\n    长度 {len(s)}，前 400 字符:")
        print(f"    {s[:400]!r}")
        print(f"\n    后 400 字符:")
        print(f"    {s[-400:]!r}")

print(f"\n=== 汇总：正常 {ok_n} / 错误 {bad_n} ===")
