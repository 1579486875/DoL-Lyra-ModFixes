// 全联动回归测试 v8：每个测试前重置 worn，避免联动 2 污染
(() => {
  const out = {};
  const S = window.SugarCube;
  const V = () => S.State.variables;

  out.modLoaded = typeof window.系统联动 !== 'undefined';
  try { jQuery(document).trigger(':passageend'); } catch (e) {}
  if (!V().联动) { out.fatal = '状态未初始化'; return out; }

  const cleanWorn = (v) => {
    v.worn = v.worn || {};
    ['upper', 'lower', 'under_upper', 'under_lower'].forEach(s => {
      v.worn[s] = { name: '测试', integrity: 100, integrity_max: 100 };
    });
  };
  const reset = (v) => {
    cleanWorn(v);                    // ← 关键：每个测试前修好衣服
    v.联动.cool = {};
    v.联动.tearFamed_upper = false;  // ← 重置走光标记
    v.联动.tearFamed_lower = false;
    v.stress = 0; v.trauma = 0; v.arousal = 0;
    if (!v.fame) v.fame = {};
    v.fame.exhibitionism = 0;
    v.pregnancies = [];
    v.combat = false;
    v.BasicNeeds = v.BasicNeeds || {};
    v.BasicNeeds.thirst = 0;
    v.BasicNeeds.bladder = 0;
  };
  const snap = (v) => ({ stress: v.stress, fame: v.fame.exhibitionism, trauma: v.trauma, arousal: v.arousal });
  const diff = (a, b) => ({
    stress: b.stress - a.stress, fame: b.fame - a.fame,
    trauma: b.trauma - a.trauma, arousal: b.arousal - a.arousal
  });

  const go = (passage, setup, fire, label) => {
    try { S.Engine.play(passage); } catch (e) {}
    const v = V();
    reset(v);
    if (setup) setup(v);
    const a = snap(v);
    try { fire(v); } catch (e) { out['err_' + label] = String(e).slice(0, 60); }
    return diff(a, snap(V()));
  };

  // 1 失禁
  out['1_公共羞耻'] = go('Oxford Street', v => { v.uncomfortable = { nude: true }; }, () => window.系统联动.onAccident(), 'a1');
  out['1_公共不在意'] = go('Oxford Street', v => { v.uncomfortable = { nude: false }; }, () => window.系统联动.onAccident(), 'a2');
  out['1_私密'] = go('Bedroom', v => { v.uncomfortable = { nude: true }; }, () => window.系统联动.onAccident(), 'a3');
  out['1_在家裸体'] = go('Deadwood Reblooms Property Bathroom', v => { v.uncomfortable = { nude: true }; }, () => window.系统联动.onAccident(), 'a4');

  // 2 破损
  out['2_完好'] = go('Oxford Street', v => { v.worn.upper.integrity = 90; }, v => window.系统联动.tick(), 't0');
  out['2_半透'] = go('Oxford Street', v => { v.worn.upper.integrity = 50; }, v => window.系统联动.tick(), 't1');
  out['2_走光首次'] = go('Oxford Street', v => { v.worn.upper.integrity = 20; }, v => window.系统联动.tick(), 't2');
  out['2_走光第二次(不该加名声)'] = go('Oxford Street', v => {
    v.worn.upper.integrity = 20;
    v.联动.tearFamed_upper = true;      // 模拟已经计过一次
  }, v => window.系统联动.tick(), 't3');

  // 3 战斗
  out['3_战斗尿急'] = go('Oxford Street', v => { v.BasicNeeds.bladder = 8500; }, v => {
    window.系统联动.tick();
    V().combat = 1;
    window.系统联动.tick();
  }, 'b1');
  out['3_战斗口渴'] = go('Oxford Street', v => { v.BasicNeeds.thirst = 8500; }, v => {
    window.系统联动.tick();
    V().combat = 1;
    window.系统联动.tick();
  }, 'b2');
  out['3_战斗正常'] = go('Oxford Street', v => {}, v => {
    window.系统联动.tick();
    V().combat = 1;
    window.系统联动.tick();
  }, 'b3');

  // 4 拍照
  out['4_暴露拍照'] = go('Oxford Street', v => {
    v.exposed = 1; v.Phone = v.Phone || {}; v.Phone.photography = 999;
    v.daily = v.daily || {}; v.daily.cameraShots = 3;
    v.联动.lastPhoto = 999; v.联动.lastShots = 3;
  }, v => { V().daily.cameraShots = 4; window.系统联动.tick(); }, 'p1');
  out['4_公共拍照'] = go('Oxford Street', v => {
    v.exposed = 0; v.Phone = v.Phone || {}; v.Phone.photography = 100;
    v.联动.lastPhoto = 100; v.联动.lastShots = 0;
  }, v => { V().Phone.photography = 101; window.系统联动.tick(); }, 'p2');

  // 5 在家
  out['5_在家放松'] = go('Deadwood Reblooms Property Bathroom', v => { v.exposed = 1; v.stress = 1000; }, v => window.系统联动.tick(), 'h1');
  out['5_在外面'] = go('Oxford Street', v => { v.exposed = 1; v.stress = 1000; }, v => window.系统联动.tick(), 'h2');

  // 6 怀孕
  out['6_怀孕尿急'] = go('Orphanage', v => {
    v.pregnancies = [{ carrier: 'player', deliveredDate: null }];
    v.BasicNeeds.bladder = 7500;
  }, v => window.系统联动.tick(), 'g1');
  out['6_没怀孕'] = go('Orphanage', v => { v.BasicNeeds.bladder = 7500; }, v => window.系统联动.tick(), 'g2');

  return out;
})()
