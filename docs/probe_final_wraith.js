JSON.stringify((function () {
  var names = ["rngWraith", "wHunt", "wPersist", "wraithIntro", "wraithCaught",
    "wraith_pass", "wraithPossess", "wraithExorcise", "gobsession", "lobsession",
    "possessedWord", "effectsWraith", "speechWraith", "kissWraith", "ejacW"];
  var out = {};
  names.forEach(function (n) {
    try {
      var div = document.createElement("div");
      $(div).wiki("<<" + n + ">>");
      var t = div.textContent || "";
      out[n] = /does not exist/.test(t) ? "MISSING" : (/出错/.test(t) ? "ERRORS" : "OK");
    } catch (e) { out[n] = "THROW"; }
  });
  return { passage: (typeof State !== "undefined" ? State.passage : null), widgets: out };
})())
