"""查 <<widget "variablesStatic">> 和它的内容。"""
import html
import os
import re
import subprocess
import tempfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
TMP = os.path.join(tempfile.gettempdir(), "dsh_ws_check.js")

g = html.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))

print("=" * 94)
print("1) <<widget \"variablesStatic\">> 定义")
print("=" * 94)
m = re.search(r'<<widget\s+"variablesStatic"\s*>>(.*?)<</widget>>', g, re.S)
if m:
    body = m.group(1)
    print(f"长度 {len(body)}")
    print(f"前 600 字符: {body[:600]!r}")
    print(f"\n后 300 字符: {body[-300:]!r}")

    # 里面的 script
    scripts = re.findall(r"<<script>>(.*?)<</script>>", body, re.S)
    print(f"\n<<script>> 块: {len(scripts)}")
    for i, s in enumerate(scripts):
        open(TMP, "w", encoding="utf-8").write(s)
        r = subprocess.run(["node", "--check", TMP], capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        if r.returncode == 0:
            print(f"  块 {i+1}: ✅ 语法正常（{len(s)} 字符）")
        else:
            print(f"  块 {i+1}: ❌ 语法错误")
            for line in (r.stderr or "").strip().split("\n")[:5]:
                print(f"      {line}")
            print(f"      前 300: {s[:300]!r}")
            print(f"      后 300: {s[-300:]!r}")
else:
    print("  未找到")

print("\n" + "=" * 94)
print("2) 所有 passage 里含 variablesStatic 的")
print("=" * 94)
raw = open(HTML, "rb").read().decode("utf-8", "replace")
for mm in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
    pn = html.unescape(mm.group(1))
    b = html.unescape(mm.group(2))
    if "variablesStatic" in b:
        n_widget = len(re.findall(r'<<widget\s+"variablesStatic"', b))
        n_call = len(re.findall(r"<<variablesStatic\b", b))
        print(f"  {pn}: widget定义 {n_widget}, 调用 {n_call}")
