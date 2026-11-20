JSON.stringify((function () {
  var out = {};
  var G = (typeof SugarCube !== "undefined") ? SugarCube.Story : null;
  if (!G) return { error: "no Story" };

  function check(passageName, marker, desc) {
    try {
      var p = G.get(passageName);
      if (!p) return { passage: passageName, exists: false };
      var t = p.text || "";
      return {
        passage: passageName,
        exists: true,
        len: t.length,
        hasMarker: t.indexOf(marker) >= 0,
        markerDesc: desc,
        snippet: t.indexOf(marker) >= 0
          ? t.substring(Math.max(0, t.indexOf(marker) - 60), t.indexOf(marker) + 180)
          : t.substring(0, 120)
      };
    } catch (e) {
      return { passage: passageName, error: String(e).slice(0, 120) };
    }
  }

  // ① relation-box：<<if>> 里不应有宏
  out.relationBox = check("Widgets", "$wraith.mimic is _npcData.nam", "比较用英文原名");
  // 反查：不该有 <<if (<<NPC_CN_NAME
  try {
    var p1 = G.get("Widgets");
    out.relationBox_badPattern = p1 ? (p1.text.indexOf("<<if (<<NPC_CN_NAME") >= 0) : "NO_PASSAGE";
  } catch (e) { out.rbBadErr = String(e).slice(0, 80); }

  // ② combatperson：应用 $description_CN || $description
  out.combatperson = check("Widgets Text", "$description_CN || $description", "CN 优先");

  // ③ generateshoppage：slot 兜底
  out.slotFix = check("Clothing Shop v2 Widgets", "Object.keys(setup.clothes).find", "slot 兜底");

  // ④ 反查：不该有裸 _item.slot（不带兜底）
  try {
    var p3 = G.get("Clothing Shop v2 Widgets");
    var t3 = p3 ? p3.text : "";
    out.rawSlotPattern = t3.indexOf("? _item.slot :") >= 0 ? "STILL_PRESENT" : "GONE";
  } catch (e) { out.rsErr = String(e).slice(0, 80); }

  // ⑤ Story 的可用方法
  try {
    out.storyProtoKeys = Object.getOwnPropertyNames(Object.getPrototypeOf(G)).slice(0, 25);
  } catch (e) { out.spErr = String(e).slice(0, 80); }

  return out;
})())
