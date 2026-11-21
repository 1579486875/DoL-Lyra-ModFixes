(function () {
  // 第14轮：用户报 Forest Shop「筛选器」reading 'desc' —— 找出各商店里在售衣物的 type（特质）在 setup.shopDetails 里没有定义的
  var s = SugarCube.setup, out = { shops: {}, missing: {}, sampleDetail: null };
  var all = Object.keys(s.clothes).flatMap(function (k) { return Array.isArray(s.clothes[k]) ? s.clothes[k] : []; });
  var shops = {};
  all.forEach(function (x) { (x.shop || []).forEach(function (sh) { shops[sh] = 1; }); });
  out.sampleDetail = s.shopDetails ? JSON.stringify(s.shopDetails[Object.keys(s.shopDetails)[0]]).slice(0, 300) : null;
  out.shopDetailsKeys = s.shopDetails ? Object.keys(s.shopDetails).length : -1;
  Object.keys(shops).forEach(function (sh) {
    var items = all.filter(function (x) { return (x.shop || []).includes(sh); });
    var types = {};
    items.forEach(function (x) { (x.type || []).forEach(function (t) { types[t] = (types[t] || []); if (types[t].length < 4) types[t].push((x.modder || "") + ":" + x.variable + "/" + x.name); }); });
    out.shops[sh] = items.length;
    Object.keys(types).forEach(function (t) {
      if (!s.shopDetails || !s.shopDetails[t]) {
        out.missing[t] = out.missing[t] || { shops: [], items: types[t] };
        out.missing[t].shops.push(sh);
      }
    });
  });
  // 全部衣物（不限商店）里用到但 shopDetails 没有的特质
  var allTypes = {};
  all.forEach(function (x) { (x.type || []).forEach(function (t) { allTypes[t] = (allTypes[t] || 0) + 1; }); });
  out.allMissing = Object.keys(allTypes).filter(function (t) { return !s.shopDetails[t]; }).map(function (t) { return [t, allTypes[t]]; });
  return JSON.stringify(out);
})()
