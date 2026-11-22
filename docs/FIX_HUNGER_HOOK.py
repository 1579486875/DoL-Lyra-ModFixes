# -*- coding: utf-8 -*-
"""在 index 的 </body> 前注入一个饥饿同步钩子（纯运行时，不改模组/widget）。"""
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))

HOOK = r"""
<script id="bn-hunger-sync-hook">
/* [DoL-Lyra] 原版 $hunger/$thirst  <->  BasicNeeds 双向桥接（运行时钩子，不改模组） */
(function () {
  if (window.__bnHungerSyncInstalled) return;
  window.__bnHungerSyncInstalled = true;

  function syncToBn() {
    try {
      var V = window.SugarCube && SugarCube.State ? SugarCube.State.variables : null;
      if (!V || !V.BasicNeeds) return;
      if (typeof V.hunger === "number" && isFinite(V.hunger)) {
        var h = Math.max(0, Math.min(10000, V.hunger * 5));
        if (h > (V.BasicNeeds.hunger || 0)) V.BasicNeeds.hunger = h;
      }
      if (typeof V.thirst === "number" && isFinite(V.thirst)) {
        var t = Math.max(0, Math.min(10000, V.thirst * 5));
        if (t > (V.BasicNeeds.thirst || 0)) V.BasicNeeds.thirst = t;
      }
    } catch (e) { /* 静默 */ }
  }

  // BasicNeeds 食物 -> 原版（把 BasicNeeds 的 hunger/thirst 回写到 $hunger/$thirst）
  function syncToVanilla() {
    try {
      var V = window.SugarCube && SugarCube.State ? SugarCube.State.variables : null;
      if (!V || !V.BasicNeeds) return;
      var bn = V.BasicNeeds;
      if (typeof bn.hunger === "number" && isFinite(bn.hunger) && typeof V.hunger === "number") {
        var vh = Math.max(0, Math.min(2000, bn.hunger / 5));
        if (vh < V.hunger) V.hunger = vh;   // BasicNeeds 吃饱了就降低原版饥饿
      }
      if (typeof bn.thirst === "number" && isFinite(bn.thirst) && typeof V.thirst === "number") {
        var vt = Math.max(0, Math.min(2000, bn.thirst / 5));
        if (vt < V.thirst) V.thirst = vt;
      }
    } catch (e) { /* 静默 */ }
  }

  $(document).on(":passagedisplay", function () { syncToBn(); syncToVanilla(); });
  $(document).on(":passagerender", function () { syncToBn(); });
})();
</script>
"""

if "bn-hunger-sync-hook" in raw:
    print("已存在，跳过")
    sys.exit(0)

i = raw.rfind("</body>")
if i < 0:
    print("❌ 找不到 </body>")
    sys.exit(1)
raw2 = raw[:i] + HOOK + raw[i:]

npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
print("passage:", npass, "->", npass2, "| 注入长度:", len(HOOK))
if npass2 != npass:
    print("❌ passage 变化")
    sys.exit(1)
open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写入")
