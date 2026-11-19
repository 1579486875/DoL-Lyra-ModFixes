/**
 * 用 Edge headless + CDP 真实加载游戏，捕获所有运行时错误。
 *
 * 用法: node cdp_test.js <html路径> [等待秒数]
 *
 * 不需要安装任何 npm 包（Node 24 原生 fetch + WebSocket）。
 */
const { spawn } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const HTML = process.argv[2];
const WAIT_SEC = parseInt(process.argv[3] || "25", 10);
const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const PORT = 9333;
const PROFILE = path.join(os.tmpdir(), "dsh-edge-profile-" + Date.now());

const errors = [];
const warnings = [];
const logs = [];

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function main() {
  let targetUrl;
  let sizeMB = "?";
  if (/^https?:/.test(HTML)) {
    targetUrl = HTML;
  } else {
    const abs = path.resolve(HTML);
    if (!fs.existsSync(abs)) {
      console.error("❌ HTML 不存在:", abs);
      process.exit(2);
    }
    sizeMB = (fs.statSync(abs).size / 1048576).toFixed(1);
    targetUrl = "file:///" + abs.replace(/\\/g, "/");
  }
  console.log(`[CDP] 目标: ${targetUrl} (${sizeMB} MB)`);
  console.log(`[CDP] 等待 ${WAIT_SEC} 秒收集错误\n`);

  fs.mkdirSync(PROFILE, { recursive: true });

  const args = [
    "--headless=new",
    `--remote-debugging-port=${PORT}`,
    `--user-data-dir=${PROFILE}`,
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--allow-file-access-from-files",
    "--autoplay-policy=no-user-gesture-required",
    "--js-flags=--max-old-space-size=4096",
    "about:blank",
  ];

  const proc = spawn(EDGE, args, { stdio: ["ignore", "pipe", "pipe"] });
  let browserErr = "";
  proc.stderr.on("data", d => { browserErr += d.toString(); });

  // 等 CDP 端口就绪
  let targets = null;
  for (let i = 0; i < 60; i++) {
    await sleep(500);
    try {
      const r = await fetch(`http://127.0.0.1:${PORT}/json/list`);
      targets = await r.json();
      if (targets && targets.length) break;
    } catch (e) { /* 还没起来 */ }
  }
  if (!targets || !targets.length) {
    console.error("❌ CDP 端口未就绪");
    console.error(browserErr.slice(-800));
    proc.kill();
    process.exit(2);
  }

  const page = targets.find(t => t.type === "page") || targets[0];
  console.log("[CDP] 已连接:", page.title || page.url);

  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let msgId = 0;
  const pending = new Map();

  function send(method, params) {
    const id = ++msgId;
    ws.send(JSON.stringify({ id, method, params: params || {} }));
    return new Promise((resolve, reject) => {
      pending.set(id, { resolve, reject });
      setTimeout(() => {
        if (pending.has(id)) { pending.delete(id); resolve(null); }
      }, 15000);
    });
  }

  await new Promise((resolve, reject) => {
    ws.onopen = resolve;
    ws.onerror = reject;
  });

  ws.onmessage = (ev) => {
    let msg;
    try { msg = JSON.parse(ev.data); } catch (e) { return; }

    if (msg.id && pending.has(msg.id)) {
      pending.get(msg.id).resolve(msg.result);
      pending.delete(msg.id);
      return;
    }

    const m = msg.method;
    if (m === "Runtime.exceptionThrown") {
      const d = msg.params.exceptionDetails;
      const text = d.exception && (d.exception.description || d.exception.value) || d.text;
      errors.push({
        kind: "exception",
        text: String(text).slice(0, 500),
        url: d.url || "",
        line: d.lineNumber,
        col: d.columnNumber,
      });
    } else if (m === "Runtime.consoleAPICalled") {
      const t = msg.params.type;
      const args = (msg.params.args || []).map(a => {
        if (a.value !== undefined) return String(a.value);
        if (a.description) return a.description;
        return a.type;
      }).join(" ");
      if (t === "error") errors.push({ kind: "console.error", text: args.slice(0, 500) });
      else if (t === "warning") warnings.push({ kind: "console.warn", text: args.slice(0, 400) });
      else logs.push({ kind: t, text: args.slice(0, 300) });
    } else if (m === "Log.entryAdded") {
      const e = msg.params.entry;
      const txt = (e.text || "").slice(0, 500);
      if (e.level === "error") errors.push({ kind: "log.error", text: txt, url: e.url || "" });
      else if (e.level === "warning") warnings.push({ kind: "log.warn", text: txt });
    }
  };

  await send("Runtime.enable");
  await send("Log.enable");
  await send("Page.enable");
  await send("Page.navigate", { url: targetUrl });

  console.log("[CDP] 已导航，等待游戏启动...\n");
  await sleep(WAIT_SEC * 1000);

  // 探测游戏状态
  const probe = await send("Runtime.evaluate", {
    expression: `JSON.stringify({
      hasSugarCube: typeof window.SugarCube !== "undefined",
      hasSetup: typeof window.setup !== "undefined",
      hasState: typeof window.State !== "undefined",
      passage: (typeof window.State !== "undefined" && State.passage) || null,
      setupFns: (function(){
        if (typeof window.setup === "undefined") return null;
        var want = ["description_CN","NPC_CN_TOOLNAME","NPC_CN_TYPE","NPC_CN_NAME","NPC_CN_TITLE","BODYPARTS_CN_NAME","CAFE_FOOD_CN","DirectionCN","brothelshowType_CN","update_cloth_cn"];
        var o = {};
        want.forEach(function(k){ o[k] = typeof setup[k]; });
        return o;
      })(),
      callDesc: (function(){ try { return typeof setup !== "undefined" && setup.description_CN ? setup.description_CN("tall") : "NOFN"; } catch(e){ return "ERR:"+e.message; } })(),
      callType: (function(){ try { return typeof setup !== "undefined" && setup.NPC_CN_TYPE ? setup.NPC_CN_TYPE("lizard") : "NOFN"; } catch(e){ return "ERR:"+e.message; } })(),
      bodyLen: document.body ? document.body.innerText.length : 0,
      bodyHead: document.body ? document.body.innerText.slice(0, 300) : ""
    })`,
    returnByValue: true,
  });

  let state = null;
  try {
    const v = probe && probe.result && probe.result.value;
    state = v ? JSON.parse(v) : null;
  } catch (e) { }

  console.log("=".repeat(80));
  console.log("游戏状态探测");
  console.log("=".repeat(80));
  if (state) {
    console.log("  SugarCube 对象:", state.hasSugarCube);
    console.log("  setup 对象    :", state.hasSetup);
    console.log("  State 对象    :", state.hasState);
    console.log("  当前 passage  :", state.passage);
    console.log("  正文长度      :", state.bodyLen);
    console.log("  正文开头      :", JSON.stringify((state.bodyHead || "").slice(0, 150)));
    if (state.setupFns) {
      console.log("\n  setup 函数:");
      for (const k in state.setupFns) {
        const t = state.setupFns[k];
        console.log(`    ${t === "function" ? "✅" : "❌"} ${k}: ${t}`);
      }
    }
    console.log("\n  实际调用:");
    console.log("    description_CN('tall') =", JSON.stringify(state.callDesc));
    console.log("    NPC_CN_TYPE('lizard')  =", JSON.stringify(state.callType));
  } else {
    console.log("  (探测失败)");
  }

  console.log("\n" + "=".repeat(80));
  console.log(`错误 ${errors.length} 条 / 警告 ${warnings.length} 条`);
  console.log("=".repeat(80));
  const seen = new Set();
  for (const e of errors) {
    const key = e.text.slice(0, 120);
    if (seen.has(key)) continue;
    seen.add(key);
    console.log(`\n  ❌ [${e.kind}] ${e.text}`);
    if (e.url) console.log(`      @${e.url}:${e.line}`);
  }
  if (errors.length === 0) console.log("  ✅ 无错误");

  if (warnings.length) {
    console.log("\n--- 警告（去重前 15 条）---");
    const ws2 = new Set();
    for (const w of warnings) {
      const k = w.text.slice(0, 100);
      if (ws2.has(k)) continue;
      ws2.add(k);
      if (ws2.size > 15) break;
      console.log(`  ⚠️ [${w.kind}] ${w.text}`);
    }
  }

  try { ws.close(); } catch (e) { }
  try { proc.kill(); } catch (e) { }
  await sleep(500);
  try { fs.rmSync(PROFILE, { recursive: true, force: true }); } catch (e) { }

  process.exit(errors.length ? 1 : 0);
}

main().catch(e => {
  console.error("测试器异常:", e);
  process.exit(2);
});
