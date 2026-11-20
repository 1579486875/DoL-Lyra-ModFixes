JSON.stringify((function () {
  var out = {};

  // ===== 1. relation-box 的 <<if>> 是否还有宏嵌套（社交界面崩溃根因）=====
  try {
    var found = false;
    if (SugarCube.Story && SugarCube.Story.passages) {
      for (var i = 0; i < SugarCube.Story.passages.length; i++) {
        var p = SugarCube.Story.passages[i];
        if (!p || !p.text) continue;
        if (p.text.indexOf('widget "relation-box"') >= 0) {
          var mm = p.text.match(/<<if \(<<|<<if <<NPC_CN_NAME/);
          out.relationBoxMacroInIf = mm ? mm[0] : "CLEAN";
          found = true;
          break;
        }
      }
    }
    out.relationBoxFound = found;
  } catch (e) { out.rbErr = String(e).slice(0, 150); }

  // ===== 2. generateshoppage 的 slot 兜底是否在位 =====
  try {
    var hasFix = false;
    if (SugarCube.Story && SugarCube.Story.passages) {
      for (var j = 0; j < SugarCube.Story.passages.length; j++) {
        var q = SugarCube.Story.passages[j];
        if (!q || !q.text) continue;
        if (q.text.indexOf('widget "generateshoppage"') >= 0) {
          hasFix = q.text.indexOf('Object.keys(setup.clothes).find') >= 0;
          break;
        }
      }
    }
    out.slotFallback = hasFix ? "PRESENT" : "MISSING";
  } catch (e) { out.sfErr = String(e).slice(0, 150); }

  // ===== 3. combatperson 是否用 description_CN =====
  try {
    var cpOk = false;
    if (SugarCube.Story && SugarCube.Story.passages) {
      for (var k = 0; k < SugarCube.Story.passages.length; k++) {
        var r = SugarCube.Story.passages[k];
        if (!r || !r.text) continue;
        if (r.text.indexOf('widget "combatperson"') >= 0) {
          var seg = r.text.split('widget "combatperson"')[1] || "";
          cpOk = seg.indexOf("$description_CN || $description") >= 0;
          break;
        }
      }
    }
    out.combatpersonCN = cpOk ? "PRESENT" : "MISSING";
  } catch (e) { out.cpErr = String(e).slice(0, 150); }

  // ===== 4. 5 个 setup 函数实调 =====
  try {
    out.fns = {
      NPC_CN_TYPE_lizard: setup.NPC_CN_TYPE ? setup.NPC_CN_TYPE("lizard") : "NO_FN",
      NPC_CN_TYPE_eels: setup.NPC_CN_TYPE ? setup.NPC_CN_TYPE("eels") : "NO_FN",
      description_CN_tall: setup.description_CN ? setup.description_CN("tall") : "NO_FN",
      NPC_CN_TOOLNAME_dildo: setup.NPC_CN_TOOLNAME ? setup.NPC_CN_TOOLNAME("dildo") : "NO_FN",
      CAFE_FOOD_CN: setup.CAFE_FOOD_CN ? setup.CAFE_FOOD_CN("milkshake") : "NO_FN"
    };
  } catch (e) { out.fnErr = String(e).slice(0, 150); }

  // ===== 5. 关键表状态 =====
  try {
    out.tables = {
      NPCTypeList_len: (setup.NPCTypeList_cn_name || "").length,
      CafeFoodList_len: (setup.CafeFoodList_cn_name || "").length,
      DirectionCN_back: setup.DirectionCN ? setup.DirectionCN("back") : "NO_FN",
      brothelshowType_sex: setup.brothelshowType_CN ? setup.brothelshowType_CN("sex") : "NO_FN"
    };
  } catch (e) { out.tblErr = String(e).slice(0, 150); }

  // ===== 6. Template.add 的名字（不能含中文）=====
  try {
    var tplNames = [];
    if (SugarCube.Story && SugarCube.Story.passages) {
      for (var t = 0; t < SugarCube.Story.passages.length; t++) {
        var tp = SugarCube.Story.passages[t];
        if (!tp || !tp.text) continue;
        var re = /Template\.add\(\s*"([^"]+)"/g, mm2;
        while ((mm2 = re.exec(tp.text))) {
          if (/[\u4e00-\u9fff]/.test(mm2[1])) tplNames.push(mm2[1]);
        }
      }
    }
    out.cnTemplateNames = tplNames;
  } catch (e) { out.tplErr = String(e).slice(0, 150); }

  // ===== 7. _args 泄漏 =====
  try {
    var argsLeak = 0;
    if (SugarCube.Story && SugarCube.Story.passages) {
      for (var u = 0; u < SugarCube.Story.passages.length; u++) {
        var up = SugarCube.Story.passages[u];
        if (!up || !up.text) continue;
        var re2 = /(?<![<>=\w])_args\[\d+\]/g, m3;
        while ((m3 = re2.exec(up.text))) {
          var pre = up.text.slice(Math.max(0, m3.index - 200), m3.index);
          if (pre.lastIndexOf("<<") <= pre.lastIndexOf(">>")) {
            // 不在宏里
            if (/[\u4e00-\u9fff]/.test(up.text.slice(Math.max(0, m3.index - 20), m3.index + 25))) {
              argsLeak++;
            }
          }
        }
      }
    }
    out.argsLeak = argsLeak;
  } catch (e) { out.argsErr = String(e).slice(0, 150); }

  // ===== 8. 双重转义 =====
  try {
    out.doubleEscape = 0;
    if (SugarCube.Story && SugarCube.Story.passages) {
      for (var v = 0; v < SugarCube.Story.passages.length; v++) {
        var vp = SugarCube.Story.passages[v];
        if (!vp || !vp.text) continue;
        if (vp.text.indexOf("&amp;lt;") >= 0) out.doubleEscape++;
      }
    }
  } catch (e) { out.deErr = String(e).slice(0, 150); }

  return out;
})())
