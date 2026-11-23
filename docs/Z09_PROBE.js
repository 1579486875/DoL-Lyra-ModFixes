// 第9轮：历史修复点全量回归 + $Phone 初始化验证
(() => {
  const S = window.SugarCube;
  const V = S.State.variables;
  const out = {};

  // 1) $Phone 初始化（第 26 轮修复）
  out.phone = {
    exists: V.Phone !== undefined,
    type: typeof V.Phone,
    taskDanger: V.Phone && V.Phone.TaskDanger,
    task: V.Phone && V.Phone.Task,
    taskRun: V.Phone && V.Phone.TaskRun,
  };

  // 2) 饥饿同步
  V.BasicNeeds = V.BasicNeeds || {};
  V.BasicNeeds.hunger = 5000; V.hunger = 1800;
  jQuery(document).trigger(":passagedisplay");
  out.hunger1 = { hunger: V.hunger, bn: V.BasicNeeds.hunger };
  V.BasicNeeds.hunger = 3000;
  jQuery(document).trigger(":passagedisplay");
  out.hunger2 = { hunger: V.hunger, bn: V.BasicNeeds.hunger };

  // 3) 露出联动
  if (window.mee && window.mee.excrete) {
    V.BasicNeeds.bladder = 5000;
    out.meeCan = window.mee.getexcretes() === false;
    window.mee.excrete();
    out.meeCleared = V.BasicNeeds.bladder === 0;
  }

  // 4) 对照表抽查
  const t = (fn, ks) => { const r = {}; ks.forEach(k => { try { r[k] = setup[fn](k); } catch (e) { r[k] = "ERR"; } }); return r; };
  out.title = t("NPC_CN_TITLE", ["baker", "chef", "alpha", "mayor", "anonymous"]);
  out.type = t("NPC_CN_TYPE", ["wolf", "fish", "shark", "carp", "starfish", "plantgirl"]);
  out.name = t("NPC_CN_NAME", ["Robin", "Whitney", "slim plantgirl", "thick dog"]);
  out.tool = t("NPC_CN_TOOLNAME", ["pen", "pencil", "dildo"]);
  out.body = t("BODYPARTS_CN_NAME", ["right", "left", "hand", "right hand"]);
  out.desc = t("description_CN", ["thick", "brutish", "voluptuous", "lissome"]);

  // 5) 关键模组
  out.mods = {
    smartphone: typeof window.smartphone,
    BN: typeof window.BN,
    reliefScenes: (window.BN && window.BN.RELIEF_SCENES) ? window.BN.RELIEF_SCENES.length : null,
  };

  // 6) 浴室去重
  try {
    S.Engine.play("Bathroom");
    const html = jQuery(".passage").last().html() || "";
    out.bathroom = {
      staticPee: (html.match(/小便 \(0:01\)/g) || []).length,
      staticPoo: (html.match(/大便 \(0:05\)/g) || []).length,
    };
  } catch (e) {}

  return out;
})()
