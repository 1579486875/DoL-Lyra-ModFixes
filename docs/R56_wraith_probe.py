"""第 56 轮：在真浏览器里逐块注册 Widgets Wraith，精确定位中断点。

思路：把 Widgets Wraith 的 35 个 widget 定义切成块，
逐个用底层 Wikifier 注册，记录每个的成功/失败与耗时。
"""
import html as H
import json
import os
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
z = zipfile.ZipFile(APK)
g = H.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))

# 提取 Widgets Wraith 的原文
m = re.search(r'<tw-passagedata[^>]*name="Widgets Wraith"[^>]*>(.*?)</tw-passagedata>',
              z.read("assets/www/index.html").decode("utf-8", "replace"), re.S)
body = H.unescape(m.group(1)) if m else ""
print(f"Widgets Wraith 长度 {len(body):,}")

# 切块
blocks = []
i = 0
while True:
    mm = re.search(r'<<widget\s+"([^"]+)"\s*>>', body[i:])
    if not mm:
        break
    start = i + mm.start()
    name = mm.group(1)
    j = i + mm.end()
    depth = 1
    while j < len(body) and depth > 0:
        if body.startswith("<<widget ", j):
            depth += 1
            j += 9
        elif body.startswith("<</widget>>", j):
            depth -= 1
            j += 11
            if depth == 0:
                break
        else:
            j += 1
    blocks.append((name, body[start:j]))
    i = j

print(f"切出 {len(blocks)} 块")

# 生成探针 JS
probe = """
JSON.stringify((function () {
  var SC = window.SugarCube;
  if (!SC || !SC.Macro || !SC.Wikifier) return { err: "NO_API" };
  var Macro = SC.Macro, Wikifier = SC.Wikifier;
  var BLOCKS = %s;
  var out = [];
  var t0 = performance.now();
  for (var i = 0; i < BLOCKS.length; i++) {
    var name = BLOCKS[i][0], src = BLOCKS[i][1];
    var t1 = performance.now();
    var err = null;
    try {
      var div = document.createElement("div");
      new Wikifier(div, src);
    } catch (e) {
      err = String(e.message || e).slice(0, 200);
    }
    var dt = performance.now() - t1;
    out.push({
      i: i + 1,
      name: name,
      len: src.length,
      ms: Math.round(dt),
      ok: Macro.has(name),
      err: err
    });
    if (dt > 3000) { out.push({slow: true, name: name, ms: Math.round(dt)}); }
  }
  return { total: (performance.now() - t0) | 0, blocks: out };
})())
""" % json.dumps([[n, b] for n, b in blocks], ensure_ascii=False)

open(r"E:\TAML\_dol\work\probe_wraith_blocks.js", "w", encoding="utf-8").write(probe)
print("探针已写入 probe_wraith_blocks.js")
print(f"探针大小 {os.path.getsize(r'E:\TAML\_dol\work\probe_wraith_blocks.js'):,} B")
