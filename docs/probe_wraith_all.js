JSON.stringify((function () {
  var all = ['generateWraith','initWraith','statsWraith','startWraith','continueWraith','endWraith','rainWraith','endRainWraith','checkWraith','clearWraith','wraithEyes','wraithShamble','speechWraith','effectsWraith','chastityBreakWraith','apologyWraith','rescueWraith','ejacW','ejaculation-wraith','kissWraith','wHunt','wPersist','wTimerProgress','exitWraith','rngWraith','rngWraithSocial','wraithEventStreet','wraithEventSewers','wraithIntro','wraithCaught','wraith_pass','wraithPossess','wraithExorcise','gobsession','lobsession','possessedWord'];
  var out = {};
  all.forEach(function (n) {
    try {
      var d = document.createElement('div');
      $(d).wiki('<<' + n + '>>');
      var txt = (d.textContent || '');
      if (/does not exist/.test(txt)) out[n] = 'MISSING';
      else if (/errors within widget code|出错/.test(txt)) out[n] = 'ERRORS';
      else out[n] = 'OK';
    } catch (e) {
      out[n] = 'THROW:' + String(e.message || e).slice(0, 40);
    }
  });
  return out;
})())
