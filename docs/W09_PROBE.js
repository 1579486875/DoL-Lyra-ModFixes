// 第9轮：历史修复点全量回归 + 关键模组功能
(() => {
  const S = window.SugarCube;
  const V = S.State.variables;
  const out = {};

  // 1) 饥饿同步
  V.BasicNeeds = V.BasicNeeds || {};
  V.BasicNeeds.hunger = 5000; V.hunger = 1800;
  jQuery(document).trigger(":passagedisplay");
  out.hungerSync1 = { hunger: V.hunger, bn: V.BasicNeeds.hunger };
  V.BasicNeeds.hunger = 3000;
  jQuery(document).trigger(":passagedisplay");
  out.hungerSync2 = { hunger: V.hunger, bn: V.BasicNeeds.hunger };

  // 2) 露出拓展联动
  if (window.mee && window.mee.excrete && window.mee.getexcretes) {
    V.BasicNeeds.bladder = 5000;
    out.meeCanExcrete = window.mee.getexcretes() === false;
    window.mee.excrete();
    out.meeCleared = V.BasicNeeds.bladder === 0;
  } else out.mee = "missing";

  // 3) 作弊变量
  out.desire = typeof V.desire;
  out.satisfaction = typeof V.satisfaction;

  // 4) 解手场景清单
  out.reliefScenes = (window.BN && window.BN.RELIEF_SCENES) ? window.BN.RELIEF_SCENES.length : null;

  // 5) SmartPhone
  out.smartphone = typeof window.smartphone;

  // 6) timemulti
  out.timemulti = V.timemulti;

  // 7) 浴室去重（Bathroom 里静态解手入口应该没有，全靠运行时注入）
  try {
    S.Engine.play("Bathroom");
    const html = jQuery(".passage").last().html() || "";
    out.bathroom = {
      staticPee: (html.match(/小便 \(0:01\)/g) || []).length,
      staticPoo: (html.match(/大便 \(0:05\)/g) || []).length,
    };
  } catch (e) { out.bathroomErr = String(e); }

  return out;
})()
