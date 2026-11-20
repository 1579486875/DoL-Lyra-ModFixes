"""F16（第13轮）：CSS 选择器/属性里的中文 + JS 标识符里的中文。"""
import html as H
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
raw = zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace")
g = H.unescape(raw)
TICK = chr(96)

print("=" * 100)
print("1) CSS 块里的中文（选择器/属性名）")
print("=" * 100)
n = 0
for m in re.finditer(r"<style[^>]*>(.*?)</style>", g, re.S):
    css = m.group(1)
    # 找选择器里的中文
    for mm in re.finditer(r"([.#][A-Za-z0-9_\-]*[\u4e00-\u9fff][A-Za-z0-9_\-\u4e00-\u9fff]*)\s*\{", css):
        n += 1
        print(f"  ❌ 选择器含中文: {mm.group(1)!r}")
    # 找属性名里的中文（冒号左边）
    for mm in re.finditer(r"(?m)^\s*([\u4e00-\u9fff][A-Za-z0-9_\-\u4e00-\u9fff]*)\s*:", css):
        n += 1
        print(f"  ❌ 属性名含中文: {mm.group(1)!r}")
print(f"  共 {n} 处")

print("\n" + "=" * 100)
print("2) <<script>> 块里的中文标识符")
print("=" * 100)
n2 = 0
for m in re.finditer(r"<<script>>(.*?)<</script>>", g, re.S):
    js = m.group(1)
    # 变量名/函数名/属性名含中文
    for mm in re.finditer(r"\b(?:var|let|const|function)\s+([A-Za-z_$][A-Za-z0-9_$]*[\u4e00-\u9fff][A-Za-z0-9_$\u4e00-\u9fff]*)", js):
        n2 += 1
        print(f"  ❌ 标识符含中文: {mm.group(1)!r}")
    for mm in re.finditer(r"\.([A-Za-z_$][A-Za-z0-9_$]*[\u4e00-\u9fff][A-Za-z0-9_$\u4e00-\u9fff]*)", js):
        n2 += 1
        if n2 <= 20:
            print(f"  ❌ 属性含中文: {mm.group(1)!r}")
print(f"  共 {n2} 处")

print("\n" + "=" * 100)
print("3) JS 函数调用名含中文")
print("=" * 100)
n3 = 0
for mm in re.finditer(r"\b([A-Za-z_$][A-Za-z0-9_$]*[\u4e00-\u9fff][A-Za-z0-9_$\u4e00-\u9fff]*)\s*\(", g):
    n3 += 1
    if n3 <= 25:
        ctx = g[max(0, mm.start() - 100):mm.start() + 100]
        print(f"  {mm.group(1)!r}")
        print(f"    {ctx!r}")
print(f"  共 {n3} 处")

print("\n" + "=" * 100)
print("4) SugarCube 条件表达式里的中文（更宽）")
print("=" * 100)
n4 = 0
for m in re.finditer(r"<<(if|elseif)\b([^<>]{0,800}?)>>", g):
    body = m.group(2)
    s = re.sub(r'"[^"]*"', lambda x: " " * len(x.group(0)), body)
    s = re.sub(r"'[^']*'", lambda x: " " * len(x.group(0)), s)
    s = re.sub(TICK + "[^" + TICK + "]*" + TICK, lambda x: " " * len(x.group(0)), s)
    if re.search(r"[\u4e00-\u9fff]", s):
        n4 += 1
        print(f"  ❌ {m.group(0)[:200]!r}")
print(f"  共 {n4} 处")
