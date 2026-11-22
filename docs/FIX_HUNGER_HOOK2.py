# -*- coding: utf-8 -*-
"""替换饥饿同步钩子：加 lastH/lastT 游标，避免 syncToBn 抵消 BasicNeeds 进食。"""
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))

NEW = r"""<script id="bn-hunger-sync-hook">
/* [DoL-Lyra] 原版 $hunger/$thirst <-> BasicNeeds 双向桥接（运行时钩子） */
(function () {
  if (window.__bnHungerSyncInstalled) return;
  window.__bnHungerSyncInstalled = true;
  var lastH = null, lastT = null;

  function V() {
    return (window.SugarCube && SugarCube.State) ? SugarCube.State.variables : null;
  }

  // 原版 -> BasicNeeds：只在原版值变化时同步（避免每帧覆盖 BasicNeeds 的进食）
  function syncToBn() {
    try {
      var v = V();
      if (!v || !v.BasicNeeds) return;
      if (typeof v.hunger === "number" && isFinite(v.hunger) && v.hunger !== lastH) {
        lastH = v.hunger;
        var h = Math.min(10000, v.hunger * 5);
        if (h > (v.BasicNeeds.hunger || 0)) v.BasicNeeds.hunger = h;
      }
      if (typeof v.thirst === "number" && isFinite(v.thirst) && v.thirst !== lastT) {
        lastT = v.thirst;
        var t = Math.min(10000, v.thirst * 5);
        if (t > (v.BasicNeeds.thirst || 0)) v.BasicNeeds.thirst = t;
      }
    } catch (e) {}
  }

  // BasicNeeds -> 原版：吃饱了就降低原版饥饿（只降不升）
  function syncToVanilla() {
    try {
      var v = V();
      if (!v || !v.BasicNeeds) return;
      var bn = v.BasicNeeds;
      if (typeof bn.hunger === "number" && isFinite(bn.hunger) && typeof v.hunger === "number") {
        var vh = Math.max(0, Math.min(2000, bn.hunger / 5));
        if (vh < v.hunger) { v.hunger = vh; lastH = vh; }
      }
      if (typeof bn.thirst === "number" && isFinite(bn.thirst) && typeof v.thirst === "number") {
        var vt = Math.max(0, Math.min(2000, bn.thirst / 5));
        if (vt < v.thirst) { v.thirst = vt; lastT = vt; }
      }
    } catch (e) {}
  }

  $(document).on(":passagedisplay", function () { syncToBn(); syncToVanilla(); });
  $(document).on(":passagerender", function () { syncToBn(); });
})();
</script>"""

m = re.search(r'<script id="bn-hunger-sync-hook">.*?</script>', raw, re.S)
if not m:
    print("❌ 找不到旧钩子")
    sys.exit(1)
raw2 = raw[:m.start()] + NEW + raw[m.end():]

npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
print("passage:", npass, "->", npass2)
if npass2 != npass:
    print("❌ passage 变化")
    sys.exit(1)
open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 钩子已替换")
