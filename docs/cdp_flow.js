/**
 * 完整流程模拟：Start -> 角色创建 -> 进入游戏 -> 走几步。
 * 用 Engine.play 逐个跳，收集每步错误。
 */
const { spawn, execSync } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");
const http = require("http");

const APK = process.argv[2];
const WORK = path.join(os.tmpdir(), "dsh-flow-" + Date.now());
const PORT_HTTP = 8851;
const PORT_CDP = 9451;

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// 从 Start 出发的真实流程
const FLOW = [
  ["Start", "开局页"],
  ["Character Creation", "角色创建"],
  ["Character Creation Body", "体型选择"],
  ["Character Creation Gender", "性别选择"],
  ["Bedroom", "卧室（游戏内）"],
  ["Bedroom Mirror", "卧室镜子"],
  ["Wardrobe", "衣柜"],
  ["Hallway", "走廊"],
  ["Orphanage", "孤儿院"],
  ["Outside", "户外"],
];

(async () => {
  fs.mkdirSync(WORK, { recursive: true });
  console.log("[1/5] 提取 APK ...");
  execSync(`python -c "import zipfile,os;p=r'${WORK}';z=zipfile.ZipFile(r'${APK}');` +
    `open(os.path.join(p,'index.html'),'wb').write(z.read('assets/www/index.html'));` +
    `ns=[n for n in z.namelist() if n.startswith('assets/www/img/face/masks')];` +
    `[ (os.makedirs(os.path.dirname(os.path.join(p,n.replace('assets/www/',''))),exist_ok=True), open(os.path.join(p,n.replace('assets/www/','')),'wb').write(z.read(n))) for n in ns ]"`,
    { stdio: "inherit" });

  const server = http.createServer((req, res) => {
    const p = path.join(WORK, decodeURIComponent(req.url.split("?")[0]));
    if (!fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); res.end(""); return; }
    res.writeHead(200, { "Content-Type": p.endsWith(".html") ? "text/html; charset=utf-8" : "image/png" });
    fs.createReadStream(p).pipe(res);
  });
  await new Promise(r => server.listen(PORT_HTTP, "127.0.0.1", r));

  console.log("[2/5] 启动 Edge ...");
  const PROFILE = path.join(os.tmpdir(), "dsh-fl-" + Date.now());
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
    return new Promise(res => { pend.set(i, res); setTimeout(() => { if (pend.has(i)) { pend.delete(i); res(null); } }, 60000); });
  };
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });

  let bucket = [];
  ws.onmessage = e => {
    let m; try { m = JSON.parse(e.data); } catch (_) { return; }
    if (m.id && pend.has(m.id)) { pend.get(m.id)(m.result); pend.delete(m.id); return; }
    if (m.method === "Runtime.exceptionThrown") {
      const d = m.params.exceptionDetails;
      const t = d.exception && (d.exception.description || d.exception.value) || d.text;
      bucket.push(String(t).split("\n")[0].slice(0, 250));
    } else if (m.method === "Runtime.consoleAPICalled" && m.params.type === "error") {
      const a = (m.params.args || []).map(x => x.value !== undefined ? String(x.value) : (x.description || x.type)).join(" ");
      bucket.push(a.split("\n")[0].slice(0, 250));
    }
  };

  await send("Runtime.enable");
  await send("Page.enable");
  await send("Page.navigate", { url: `http://127.0.0.1:${PORT_HTTP}/index.html` });

  console.log("[3/5] 等待就绪 ...");
  const t0 = Date.now();
  while ((Date.now() - t0) / 1000 < 250) {
    await sleep(2000);
    const r = await send("Runtime.evaluate", {
      expression: "typeof setup!=='undefined'&&typeof State!=='undefined'&&!!State.passage",
      returnByValue: true,
    });
    if (r && r.result && r.result.value === true) break;
  }
  console.log(`    ${Math.round((Date.now() - t0) / 1000)}s`);
  await sleep(10000);

  const evalJs = async (expr) => {
    const r = await send("Runtime.evaluate", { expression: expr, returnByValue: true });
    return r && r.result ? (r.result.value !== undefined ? r.result.value : null) : null;
  };

  console.log("\n[4/5] 流程模拟 ...\n");
  const results = [];
  for (const [pn, desc] of FLOW) {
    bucket = [];
    const nav = await evalJs(`(function(){
      try {
        var SC = window.SugarCube;
        if (!SC || !SC.Engine || typeof SC.Engine.play !== "function") return "NO_ENGINE";
        var t = ${JSON.stringify(pn)};
        if (!SC.Story.get(t)) return "NO_PASSAGE";
        setTimeout(function(){ try { SC.Engine.play(t); } catch(e){} }, 0);
        return "QUEUED";
      } catch(e) { return "ERR:" + e.message; }
    })()`);
    await sleep(2500);
    const actual = await evalJs("typeof State!=='undefined' ? State.passage : null");

    const real = bucket.filter(x =>
      !/tryReplaceStringFuzzyWithHint/.test(x) &&
      !/ModOrderContainer|ModI18NTypeB/.test(x) &&
      !/Failed to load resource|404|DOCTYPE|"nf"/.test(x) &&
      !/Failed to load mask|Failed to load img/.test(x) &&
      !/drawImage|non-finite/.test(x) &&
      !/randomInt called with invalid/.test(x)
    );
    results.push({ pn, desc, nav, actual, total: bucket.length, real });
    const mark = real.length === 0 ? "✅" : "❌";
    console.log(`  ${mark} ${desc.padEnd(14)} ${pn.padEnd(26)} → ${String(actual).padEnd(26)} 总=${String(bucket.length).padStart(3)} 真=${real.length}`);
    for (const x of real.slice(0, 2)) console.log(`       ${x}`);
  }

  console.log("\n" + "=".repeat(80));
  const bad = results.filter(r => r.real.length > 0);
  const noPassage = results.filter(r => r.nav === "NO_PASSAGE");
  console.log(`流程 ${results.length} 步：${results.length - bad.length} 步零错误，${bad.length} 步有真问题`);
  if (noPassage.length) {
    console.log(`不存在 passage: ${noPassage.map(r => r.pn).join(", ")}`);
  }
  console.log("=".repeat(80));

  try { ws.close(); } catch (e) { }
  try { proc.kill(); } catch (e) { }
  server.close();
  await sleep(600);
  try { fs.rmSync(PROFILE, { recursive: true, force: true }); } catch (e) { }
  try { fs.rmSync(WORK, { recursive: true, force: true }); } catch (e) { }
  process.exit(0);
})().catch(e => { console.error(e); process.exit(2); });
