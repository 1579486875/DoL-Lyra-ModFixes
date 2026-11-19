/**
 * 关键界面遍历测试 v2：单次加载，异步 Engine.play，逐界面收集错误。
 * 用 window.SugarCube.Engine.play（SugarCube 2 的正确入口）。
 */
const { spawn, execSync } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");
const http = require("http");

const APK = process.argv[2];
const WORK = path.join(os.tmpdir(), "dsh-pass2-" + Date.now());
const PORT_HTTP = 8831;
const PORT_CDP = 9421;

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

const PASSAGES = [
  "Options", "Cheats", "Wardrobe", "Characteristics", "Settings",
  "Journal", "Social", "Bodywriting", "Transformations", "Museum",
  "Shop", "Forest", "Beach", "School", "Hospital", "Tutorial",
];

(async () => {
  fs.mkdirSync(WORK, { recursive: true });
  console.log("[1/5] 提取 APK index + 必要图片 ...");
  execSync(`python -c "import zipfile,os;p=r'${WORK}';z=zipfile.ZipFile(r'${APK}');` +
    `open(os.path.join(p,'index.html'),'wb').write(z.read('assets/www/index.html'));` +
    `ns=[n for n in z.namelist() if n.startswith('assets/www/img/face/masks') or n.startswith('assets/www/img/ui')];` +
    `[ (os.makedirs(os.path.dirname(os.path.join(p,n.replace('assets/www/',''))),exist_ok=True), open(os.path.join(p,n.replace('assets/www/','')),'wb').write(z.read(n))) for n in ns ]"`,
    { stdio: "inherit" });

  const server = http.createServer((req, res) => {
    const p = path.join(WORK, decodeURIComponent(req.url.split("?")[0]));
    if (!fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); res.end(""); return; }
    const ext = path.extname(p).toLowerCase();
    const ct = ext === ".html" ? "text/html; charset=utf-8"
      : ext === ".png" ? "image/png"
      : ext === ".jpg" || ext === ".jpeg" ? "image/jpeg"
      : ext === ".svg" ? "image/svg+xml"
      : "application/octet-stream";
    res.writeHead(200, { "Content-Type": ct });
    fs.createReadStream(p).pipe(res);
  });
  await new Promise(r => server.listen(PORT_HTTP, "127.0.0.1", r));

  console.log("[2/5] 启动 Edge ...");
  const PROFILE = path.join(os.tmpdir(), "dsh-e-pass2-" + Date.now());
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
    return new Promise(res => {
      pend.set(i, res);
      setTimeout(() => { if (pend.has(i)) { pend.delete(i); res(null); } }, 45000);
    });
  };
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });

  let bucket = [];
  ws.onmessage = e => {
    let m; try { m = JSON.parse(e.data); } catch (_) { return; }
    if (m.id && pend.has(m.id)) { pend.get(m.id)(m.result); pend.delete(m.id); return; }
    if (m.method === "Runtime.exceptionThrown") {
      const d = m.params.exceptionDetails;
      const t = d.exception && (d.exception.description || d.exception.value) || d.text;
      bucket.push({ k: "exception", t: String(t).split("\n")[0].slice(0, 300) });
    } else if (m.method === "Runtime.consoleAPICalled" && m.params.type === "error") {
      const a = (m.params.args || []).map(x => x.value !== undefined ? String(x.value) : (x.description || x.type)).join(" ");
      bucket.push({ k: "console.error", t: a.split("\n")[0].slice(0, 300) });
    }
  };

  await send("Runtime.enable");
  await send("Page.enable");
  await send("Page.navigate", { url: `http://127.0.0.1:${PORT_HTTP}/index.html` });

  console.log("[3/5] 等待游戏就绪 ...");
  const t0 = Date.now();
  let ready = false;
  while ((Date.now() - t0) / 1000 < 260) {
    await sleep(2000);
    const r = await send("Runtime.evaluate", {
      expression: "typeof setup!=='undefined'&&typeof State!=='undefined'&&!!State.passage",
      returnByValue: true,
    });
    if (r && r.result && r.result.value === true) {
      console.log(`    就绪 ${Math.round((Date.now() - t0) / 1000)}s`);
      ready = true;
      break;
    }
  }
  if (!ready) { console.log("    ⚠️ 未就绪，继续尝试"); }
  await sleep(12000);

  // 探测 Engine 入口
  const eng = await send("Runtime.evaluate", {
    expression: `JSON.stringify((function(){
      var SC = window.SugarCube;
      if (!SC) return {err:"no SC"};
      var E = SC.Engine;
      return {
        hasEngine: typeof E,
        hasPlay: E ? typeof E.play : "no",
        keys: E ? Object.keys(E).slice(0,15) : []
      };
    })())`,
    returnByValue: true,
  });
  console.log("\n[4/5] Engine 探测:", eng && eng.result && eng.result.value);

  console.log("\n[5/5] 遍历界面 ...\n");
  const results = [];

  for (const p of PASSAGES) {
    bucket = [];
    // 异步调用，避免同步递归
    const r = await send("Runtime.evaluate", {
      expression: `(function(){
        try {
          var SC = window.SugarCube;
          var E = SC && SC.Engine;
          if (!E || typeof E.play !== "function") return "NO_ENGINE";
          var target = ${JSON.stringify(p)};
          setTimeout(function(){ try { E.play(target); } catch(e){ window.__lastPlayErr = e.message; } }, 0);
          return "QUEUED";
        } catch(e) { return "ERR:" + e.message; }
      })()`,
      returnByValue: true,
    });
    const nav = r && r.result && r.result.value;
    await sleep(3000);

    // 检查实际到了哪个 passage
    const st = await send("Runtime.evaluate", {
      expression: "typeof State!=='undefined' ? State.passage : null",
      returnByValue: true,
    });
    const actual = st && st.result && st.result.value;

    // 过滤环境噪音
    const real = bucket.filter(x =>
      !/tryReplaceStringFuzzyWithHint/.test(x.t) &&
      !/ModOrderContainer|ModI18NTypeB|cannot find name\/alias/.test(x.t) &&
      !/Failed to load resource|404|DOCTYPE|is not valid JSON|"nf"/.test(x.t) &&
      !/Failed to load mask|Failed to load img/.test(x.t) &&
      !/drawImage|non-finite/.test(x.t) &&
      !/randomInt called with invalid/.test(x.t)
    );

    results.push({ passage: p, nav, actual, total: bucket.length, real });
    const mark = real.length === 0 ? "✅" : "❌";
    console.log(`  ${mark} ${p.padEnd(20)} → ${String(actual).padEnd(22)} 总=${String(bucket.length).padStart(4)} 真=${real.length}`);
    for (const x of real.slice(0, 3)) console.log(`       [${x.k}] ${x.t}`);
  }

  console.log("\n" + "=".repeat(80));
  const bad = results.filter(r => r.real.length > 0);
  console.log(`遍历 ${results.length} 个界面，有真问题 ${bad.length} 个`);
  console.log("=".repeat(80));
  if (bad.length) {
    const groups = new Map();
    for (const b of bad) for (const x of b.real) {
      const k = x.t.replace(/\d+/g, "N").slice(0, 100);
      groups.set(k, (groups.get(k) || 0) + 1);
    }
    for (const [k, n] of [...groups.entries()].sort((a, b) => b[1] - a[1])) {
      console.log(`  ×${String(n).padStart(3)}  ${k}`);
    }
  }

  try { ws.close(); } catch (e) { }
  try { proc.kill(); } catch (e) { }
  server.close();
  await sleep(600);
  try { fs.rmSync(PROFILE, { recursive: true, force: true }); } catch (e) { }
  try { fs.rmSync(WORK, { recursive: true, force: true }); } catch (e) { }
  process.exit(bad.length ? 1 : 0);
})().catch(e => { console.error(e); process.exit(2); });
