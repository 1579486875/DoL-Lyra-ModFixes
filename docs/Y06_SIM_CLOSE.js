// 直接复刻修复后的 fallback 逻辑，验证「点空白」是否同时移除 ta 和 hint
(() => {
  const _text = '{"name":"修女服","upper":"sexy nun\'s habit"}';
  // —— 复刻修复后的 _fallback ——
  const ta = document.createElement("textarea");
  ta.value = _text;
  ta.setAttribute("readonly", "readonly");
  ta.style.cssText = "position:fixed;left:6%;top:22%;width:88%;height:46%;z-index:99999;font-size:12px;padding:8px;";
  document.body.appendChild(ta);
  const hint = document.createElement("div");
  hint.textContent = "已复制到剪贴板（点任意处关闭）";
  hint.style.cssText = "position:fixed;left:6%;top:15%;z-index:99999;color:#fff;background:#333;padding:6px 10px;border-radius:4px;font-size:13px;";
  document.body.appendChild(hint);

  let _closed = false;
  const close = function (ev) {
    if (_closed) return;
    try {
      if (ev && (ev.target === ta || (ta.contains && ta.contains(ev.target)))) return;
    } catch (e0) {}
    _closed = true;
    try { ta.remove(); } catch (e1) {}
    try { hint.remove(); } catch (e2) {}
    try {
      document.removeEventListener("click", close, true);
      document.removeEventListener("touchend", close, true);
      document.removeEventListener("mousedown", close, true);
    } catch (e3) {}
  };
  window.setTimeout(function () {
    try {
      document.addEventListener("click", close, true);
      document.addEventListener("touchend", close, true);
      document.addEventListener("mousedown", close, true);
    } catch (e4) {}
  }, 300);

  const before = { ta: jQuery("textarea[readonly]").length, hint: jQuery("div").filter(function () { return (jQuery(this).text() || "").indexOf("点任意处关闭") >= 0; }).length };

  return new Promise(resolve => {
    setTimeout(() => {
      // 模拟点「空白」（body 上远离 ta 的位置）
      const evt = new MouseEvent("click", { bubbles: true, clientX: 5, clientY: 1800 });
      document.body.dispatchEvent(evt);
      setTimeout(() => {
        const after = { ta: jQuery("textarea[readonly]").length, hint: jQuery("div").filter(function () { return (jQuery(this).text() || "").indexOf("点任意处关闭") >= 0; }).length };
        resolve({ before, after });
      }, 200);
    }, 600);
  });
})()
