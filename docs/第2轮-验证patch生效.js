// 验证 TweeReplacer 的 patch 是否真的应用到 SugarCube.Story 的 passage
// 用法: node 第2轮-验证patch生效.js <index.html>
const fs = require("fs");
const path = require("path");
const http = require("http");
const { spawn } = require("child_process");
const os = require("os");

const INDEX = process.argv[2] || "E:\\TAML\\_dol\\work\\index_modded6.html";
const PORT_HTTP = 8893;
const PORT_CDP = 9523;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

(async () => {
  const dir = path.dirname(INDEX);
  const server = http.createServer((req, res) => {
    const p = decodeURIComponent(req.url.split("?")[0]);
    const f = path.join(dir, p === "/" ? "index.html" : p.slice(1));
    fs.readFile(f, (e, d) => {
      if (e) { res.writeHead(404); res.end(); return; }
      const ext = path.extname(f).toLowerCase();
      const ct = ext === ".html" ? "text/html; charset=utf-8"
        : ext === ".png" ? "image/png" : ext === ".css" ? "text/css"
        : ext === ".js" ? "application/javascript" : "application/octet-stream";
      res.writeHead(200, { "Content-Type": ct });
      res.end(d);
    });
  });
  await new Promise((r) => server.listen(PORT_HTTP, "127.0.0.1", r));

  const PROFILE = path.join(os.tmpdir(), "cdp-patchver-" + Date.now());
  fs.mkdirSync(PROFILE, { recursive: true });
  const proc = spawn("C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe", [
    "--headless=new", `--remote-debugging-port=${PORT_CDP}`, `--user-data-dir=${PROFILE}`,
    "--no-first-run", "--no-default-browser-check", "--disable-gpu",
    "--js-flags=--max-old-space-size=6144", "about:blank",
  ], { stdio: "ignore" });

  let targets = null;
  for (let i = 0; i < 225; i++) {
    await sleep(400);
    try {
      targets = await (await fetch(`http://127.0.0.1:${PORT_CDP}/json/list`)).json();
      if (targets && targets.length) break;
    } catch (e) { }
  }
  if (!targets || !targets.length) { console.log("❌ Edge 起不来"); process.exit(1); }
  const page = targets.find((t) => t.type === "page") || targets[0];
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let id = 0;
  const pend = new Map();
  const send = (m, p, to = 120000) => {
    const i = ++id;
    ws.send(JSON.stringify({ id: i, method: m, params: p || {} }));
    return new Promise((res) => { pend.set(i, res); setTimeout(() => { if (pend.has(i)) { pend.delete(i); res(null); } }, to); });
  };
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  ws.onmessage = (e) => {
    let m; try { m = JSON.parse(e.data); } catch (_) { return; }
    if (m.id && pend.has(m.id)) { pend.get(m.id)(m.result); pend.delete(m.id); }
  };
  const evalJs = async (expr, to = 60000) => {
    const r = await send("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true }, to);
    if (!r) return { __timeout: true };
    if (r.exceptionDetails) return { __exception: String(r.exceptionDetails.text).slice(0, 400) };
    return r.result ? r.result.value : null;
  };

  await send("Page.navigate", { url: `http://127.0.0.1:${PORT_HTTP}/index.html` });
  const t0 = Date.now();
  let ready = false;
  while ((Date.now() - t0) / 1000 < 200) {
    await sleep(3000);
    const v = await evalJs("typeof SugarCube!=='undefined' && !!SugarCube.State && !!SugarCube.State.passage", 20000);
    if (v === true) { ready = true; break; }
  }
  console.log("[就绪]", ready, Math.round((Date.now() - t0) / 1000) + "s");
  if (!ready) process.exit(1);

  // 等 patch 全部应用
  await sleep(5000);

  // 检查：对每个"应该有 patch"的 passage，看它是否包含 patch 的插入内容
  const checks = await evalJs(`(function(){
    var out = { total: 0, patched: 0, samples: [], storySize: 0 };
    try {
      var Story = SugarCube.Story;
      if (!Story) return { error: 'no Story' };
      var all = Story.lookup([]);
      out.storySize = all.length;

      // 从 modDataValueZipList 里解析出 patch 清单（只取前 200 条做抽样）
      var h = document.documentElement.innerHTML;
      // 无法直接解析 base64，改为检查已知的几种 patch 特征
      var probes = [
        { passage: 'Shopping Centre', needle: 'Shopping Centre Top', desc: '猫咖：上楼链接' },
        { passage: 'Widgets Actions Generation', needle: 'leftUndressOther', desc: 'GuideToMe：左手脱衣' },
        { passage: 'Containers', needle: '_container.count', desc: 'DoLSims：容器售卖' },
        { passage: 'Widgets Text', needle: 'combat', desc: 'DoLSims：战斗文本' },
        { passage: 'Widgets Combat Man-Combat', needle: 'npcSub', desc: 'DoLSims：npcSub 判断' },
        { passage: 'Widgets Actions Left Hand', needle: 'lefttarget', desc: 'GuideToMe：左手动作' },
        { passage: 'Robin Money', needle: 'robinmoney', desc: 'DomRobin：罗宾金钱' },
        { passage: 'Orphanage Loft', needle: 'loft_spray', desc: 'DomRobin：阁楼喷雾' },
        { passage: 'Widgets Robin', needle: 'lrtrauma', desc: 'DomRobin：罗宾创伤' },
        { passage: 'Widgets children', needle: 'updateChildActivity', desc: 'FertilityExpansion：孩子活动' }
      ];
      for (var i = 0; i < probes.length; i++) {
        var p = probes[i];
        out.total++;
        try {
          var psg = Story.get(p.passage);
          if (!psg) { out.samples.push({ p: p.passage, desc: p.desc, r: 'PASSAGE_MISSING' }); continue; }
          var txt = psg.text || '';
          if (txt.indexOf(p.needle) >= 0) { out.patched++; out.samples.push({ p: p.passage, desc: p.desc, r: 'OK' }); }
          else { out.samples.push({ p: p.passage, desc: p.desc, r: 'NEEDLE_NOT_FOUND', len: txt.length }); }
        } catch (e) {
          out.samples.push({ p: p.passage, desc: p.desc, r: 'ERR: ' + e.message });
        }
      }
    } catch (e) {
      out.error = String(e.message);
    }
    return out;
  })()`, 60000);

  console.log("\\n=== Story 里 passage 总数:", checks && checks.storySize, "===");
  if (checks && checks.samples) {
    for (const s of checks.samples) {
      console.log("  %s %-32s %-24s %s",
        s.r === "OK" ? "OK  " : "⚠   ", s.p, s.desc || "", s.r === "OK" ? "" : (s.r + (s.len ? " (len=" + s.len + ")" : "")));
    }
    console.log("\\n通过 %d / %d", checks.patched, checks.total);
  } else {
    console.log("查询失败:", JSON.stringify(checks).slice(0, 500));
  }

  try { ws.close(); } catch (e) { }
  try { server.close(); } catch (e) { }
  try { proc.kill(); } catch (e) { }
  try { fs.rmSync(PROFILE, { recursive: true, force: true }); } catch (e) { }
  process.exit(0);
})();
