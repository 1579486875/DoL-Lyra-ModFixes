/**
 * APK 真机级测试：提取 APK 的 index.html，跑 CDP，按模式分组统计错误。
 */
const { spawn, execSync } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");
const http = require("http");

const APK = process.argv[2];
const WORK = path.join(os.tmpdir(), "dsh-apk-" + Date.now());
const PORT_HTTP = 8811;
const PORT_CDP = 9401;

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

(async () => {
  // 1) 提取 APK 的 index.html
  fs.mkdirSync(WORK, { recursive: true });
  console.log("[1/4] 提取 APK index.html ...");
  execSync(`python -c "import zipfile,sys;z=zipfile.ZipFile(r'${APK}');open(r'${path.join(WORK, 'index.html')}','wb').write(z.read('assets/www/index.html'))"`,
    { stdio: "inherit" });
  const sz = (fs.statSync(path.join(WORK, "index.html")).size / 1048576).toFixed(1);
  console.log(`    ${sz} MB`);

  // 2) 起 HTTP 服务器
  console.log("[2/4] 启动 HTTP ...");
  const server = http.createServer((req, res) => {
    const p = path.join(WORK, decodeURIComponent(req.url.split("?")[0]));
    if (!fs.existsSync(p) || fs.statSync(p).isDirectory()) {
      res.writeHead(404); res.end("nf"); return;
    }
    res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
    fs.createReadStream(p).pipe(res);
  });
  await new Promise(r => server.listen(PORT_HTTP, "127.0.0.1", r));
  console.log(`    http://127.0.0.1:${PORT_HTTP}/index.html`);

  // 3) 启动 Edge
  console.log("[3/4] 启动 Edge CDP ...");
  const PROFILE = path.join(os.tmpdir(), "dsh-edge2-" + Date.now());
  fs.mkdirSync(PROFILE, { recursive: true });
  const proc = spawn("C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe", [
    "--headless=new", `--remote-debugging-port=${PORT_CDP}`,
    `--user-data-dir=${PROFILE}`, "--no-first-run", "--no-default-browser-check",
    "--disable-gpu", "--js-flags=--max-old-space-size=4096", "about:blank",
  ], { stdio: ["ignore", "pipe", "pipe"] });

  let targets = null;
  for (let i = 0; i < 80; i++) {
    await sleep(400);
    try {
      const r = await fetch(`http://127.0.0.1:${PORT_CDP}/json/list`);
      targets = await r.json();
      if (targets && targets.length) break;
    } catch (e) { }
  }
  const page = targets.find(t => t.type === "page") || targets[0];
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let id = 0;
  const pend = new Map();
  const send = (m, p) => {
    const i = ++id;
    ws.send(JSON.stringify({ id: i, method: m, params: p || {} }));
    return new Promise(res => { pend.set(i, res); setTimeout(() => { if (pend.has(i)) { pend.delete(i); res(null); } }, 30000); });
  };
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });

  const errors = [];
  ws.onmessage = e => {
    let m; try { m = JSON.parse(e.data); } catch (_) { return; }
    if (m.id && pend.has(m.id)) { pend.get(m.id)(m.result); pend.delete(m.id); return; }
    if (m.method === "Runtime.exceptionThrown") {
      const d = m.params.exceptionDetails;
      const t = d.exception && (d.exception.description || d.exception.value) || d.text;
      errors.push(String(t).split("\n")[0].slice(0, 300));
    } else if (m.method === "Runtime.consoleAPICalled" && m.params.type === "error") {
      const a = (m.params.args || []).map(x => x.value !== undefined ? String(x.value) : (x.description || x.type)).join(" ");
      errors.push(a.split("\n")[0].slice(0, 300));
    } else if (m.method === "Log.entryAdded" && m.params.entry.level === "error") {
      errors.push(String(m.params.entry.text || "").split("\n")[0].slice(0, 300));
    }
  };

  await send("Runtime.enable");
  await send("Log.enable");
  await send("Page.enable");
  await send("Page.navigate", { url: `http://127.0.0.1:${PORT_HTTP}/index.html` });

  // 4) 等就绪
  console.log("[4/4] 等待游戏就绪 ...");
  const t0 = Date.now();
  let ready = false;
  while ((Date.now() - t0) / 1000 < 240) {
    await sleep(2000);
    const r = await send("Runtime.evaluate", {
      expression: "typeof setup!=='undefined'&&typeof State!=='undefined'&&!!State.passage",
      returnByValue: true,
    });
    if (r && r.result && r.result.value === true) {
      console.log(`    就绪 ${Math.round((Date.now() - t0) / 1000)}s`);
      ready = true;
      await sleep(12000);  // 让模组和事件都跑完
      break;
    }
  }

  // 探测
  const probe = await send("Runtime.evaluate", {
    expression: `JSON.stringify({
      passage: (typeof State!=='undefined'&&State.passage)||null,
      fns: (function(){var w=["description_CN","NPC_CN_TOOLNAME","NPC_CN_TYPE","NPC_CN_NAME","BODYPARTS_CN_NAME","CAFE_FOOD_CN","DirectionCN","brothelshowType_CN","update_cloth_cn","NPC_CN_TITLE"];var o={};w.forEach(function(k){o[k]=typeof setup[k];});return o;})(),
      t_lizard: setup.NPC_CN_TYPE("lizard"),
      t_whale: setup.NPC_CN_TYPE("whale"),
      t_eels: setup.NPC_CN_TYPE("eels"),
      t_human: setup.NPC_CN_TYPE("human"),
      t_slime: setup.NPC_CN_TYPE("slime"),
      t_spider: setup.NPC_CN_TYPE("spider"),
      t_wolf: setup.NPC_CN_TYPE("wolf"),
      d_tall: setup.description_CN("tall"),
      d_lanky: setup.description_CN("lanky"),
      lockCount: setup.__cnLockCount || 0
    })`,
    returnByValue: true,
  });
  let st = null;
  try { st = JSON.parse(probe.result.value); } catch (e) { }

  console.log("\n" + "=".repeat(80));
  console.log("运行时状态");
  console.log("=".repeat(80));
  if (st) {
    console.log("  passage:", st.passage);
    console.log("  锁定次数:", st.lockCount);
    console.log("\n  setup 函数:");
    for (const k in st.fns) console.log(`    ${st.fns[k] === "function" ? "✅" : "❌"} ${k}: ${st.fns[k]}`);
    console.log("\n  翻译实测:");
    const pairs = [
      ["lizard", st.t_lizard], ["whale", st.t_whale], ["eels", st.t_eels],
      ["human", st.t_human], ["slime", st.t_slime], ["spider", st.t_spider],
      ["wolf", st.t_wolf], ["tall", st.d_tall], ["lanky", st.d_lanky],
    ];
    for (const [en, cn] of pairs) {
      const ok = cn && cn !== en;
      console.log(`    ${ok ? "✅" : "❌"} ${en} -> ${JSON.stringify(cn)}`);
    }
  }

  // 错误分组
  console.log("\n" + "=".repeat(80));
  console.log(`错误总数 ${errors.length}，按模式分组`);
  console.log("=".repeat(80));
  const groups = new Map();
  for (const e of errors) {
    let key = e
      .replace(/Array\(\d+\)/g, "Array(n)")
      .replace(/\d+/g, "N")
      .replace(/0x[0-9a-f]+/gi, "0xX")
      .slice(0, 110);
    groups.set(key, (groups.get(key) || 0) + 1);
  }
  const sorted = [...groups.entries()].sort((a, b) => b[1] - a[1]);
  for (const [k, n] of sorted.slice(0, 25)) {
    const isEnv = /cordova|ERR_FILE_NOT_FOUND|404|DOCTYPE/.test(k);
    const mark = isEnv ? "🔧" : "❌";
    console.log(`  ${mark} ×${String(n).padStart(5)}  ${k}`);
  }

  try { ws.close(); } catch (e) { }
  try { proc.kill(); } catch (e) { }
  server.close();
  await sleep(600);
  try { fs.rmSync(PROFILE, { recursive: true, force: true }); } catch (e) { }
  try { fs.rmSync(WORK, { recursive: true, force: true }); } catch (e) { }
  process.exit(0);
})().catch(e => { console.error(e); process.exit(2); });
