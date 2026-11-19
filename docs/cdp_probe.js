/**
 * 运行时探针 v2：轮询等待游戏就绪，再执行表达式。
 * 用法: node cdp_probe.js <url> @expr.js [超时秒]
 */
const { spawn } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const URL_ = process.argv[2] || "http://127.0.0.1:8801/index_modded6.html";
let EXPR = process.argv[3] || "1";
if (EXPR.startsWith("@")) EXPR = fs.readFileSync(EXPR.slice(1), "utf-8");
const TIMEOUT = parseInt(process.argv[4] || "180", 10);

const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const PORT = 9335 + Math.floor(Math.random() * 100);
const PROFILE = path.join(os.tmpdir(), "dsh-probe-" + Date.now());

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

(async () => {
  fs.mkdirSync(PROFILE, { recursive: true });
  const proc = spawn(EDGE, [
    "--headless=new", `--remote-debugging-port=${PORT}`,
    `--user-data-dir=${PROFILE}`, "--no-first-run", "--no-default-browser-check",
    "--disable-gpu", "--js-flags=--max-old-space-size=4096", "about:blank",
  ], { stdio: ["ignore", "pipe", "pipe"] });

  let targets = null;
  for (let i = 0; i < 80; i++) {
    await sleep(400);
    try {
      const r = await fetch(`http://127.0.0.1:${PORT}/json/list`);
      targets = await r.json();
      if (targets && targets.length) break;
    } catch (e) { }
  }
  if (!targets) { console.error("CDP 未就绪"); process.exit(2); }

  const page = targets.find(t => t.type === "page") || targets[0];
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let id = 0;
  const pend = new Map();
  const send = (method, params) => {
    const i = ++id;
    ws.send(JSON.stringify({ id: i, method, params: params || {} }));
    return new Promise(res => {
      pend.set(i, res);
      setTimeout(() => { if (pend.has(i)) { pend.delete(i); res(null); } }, 30000);
    });
  };
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  ws.onmessage = e => {
    let m; try { m = JSON.parse(e.data); } catch (_) { return; }
    if (m.id && pend.has(m.id)) { pend.get(m.id)(m.result); pend.delete(m.id); }
  };
  await send("Runtime.enable");
  await send("Page.navigate", { url: URL_ });

  // 轮询等待 setup 就绪
  const t0 = Date.now();
  let ready = false;
  while ((Date.now() - t0) / 1000 < TIMEOUT) {
    await sleep(2000);
    const r = await send("Runtime.evaluate", {
      expression: "typeof setup !== 'undefined' && typeof State !== 'undefined' && !!State.passage",
      returnByValue: true,
    });
    const ok = r && r.result && r.result.value === true;
    const sec = Math.round((Date.now() - t0) / 1000);
    if (ok) {
      console.log(`[探针] 游戏就绪（${sec}s）`);
      ready = true;
      // 再等 8 秒让模组加载完
      await sleep(8000);
      break;
    }
    if (sec % 20 < 2) console.log(`  ...等待中 ${sec}s`);
  }
  if (!ready) {
    console.log("[探针] ⚠️ 超时未就绪，仍尝试执行");
  }

  const r = await send("Runtime.evaluate", {
    expression: EXPR,
    returnByValue: true,
    awaitPromise: true,
  });
  if (r && r.result) {
    const v = r.result.value !== undefined ? r.result.value : r.result;
    console.log(typeof v === "string" ? v : JSON.stringify(v, null, 2));
  } else {
    console.log("(无结果)");
  }

  try { ws.close(); } catch (e) { }
  try { proc.kill(); } catch (e) { }
  await sleep(500);
  try { fs.rmSync(PROFILE, { recursive: true, force: true }); } catch (e) { }
  process.exit(0);
})();
