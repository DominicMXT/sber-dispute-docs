const sleep = ms => new Promise(r => setTimeout(r, ms)); const o = {};
const vt = () => $('#view').innerText.replace(/\n+/g, ' | ').slice(0, 700);
const click = sel => { const b = $(sel); if (!b) throw new Error('no ' + sel); b.click(); };
const pult = code => { $('#fab').click(); const b = $(`#panel [data-sc="${code}"]`); b.click(); return {panelOpen: $('#panel').classList.contains('open'), panelDisplay: getComputedStyle($('#panel')).display}; };
// A. pult v3 buttons leave the panel open (narrow screen)
o.panel = {}; for (const c of ['example','solo','group2','group3','dayprice','slip','weeksum3','nextgoal','themeSet','mid']) { $('#panel').classList.remove('open'); o.panel[c] = pult(c); await sleep(20); }
// B. solo goal, switch to Аня via pult
V3_SCEN.solo(); $('#panel [data-who="anya"]').click(); o.soloAnya = {who:S.who, scr:S.scr, invited:P().invited, view: vt()}; S.tab = 'buy'; go('list'); o.soloAnyaList = vt();
// C. user-made solo goal via onboarding then v2 «Партнёр отложил сегодня»
scenario('fresh'); await sleep(10); ACT.consentOk(); o.afterConsent = S.scr; ACT.v3own(); $('#phrase').value = 'Велосипед 60 тысяч к 1 мая'; ACT.phraseGo(); await sleep(700);
o.flowScr1 = S.scr + ' :: ' + vt();
if (S.scr === 'clarify') { $('#clar').value = 'всю сумму сам'; $('#clarf').requestSubmit(); }
o.flowScr2 = S.scr; if (S.scr === 'answer') { $('#bottom .main').click(); } o.flowScr3 = S.scr; if (S.scr === 'together') click('[data-act="v3alone"]'); closeSheet();
o.mySolo = {scr:S.scr, solo: v3solo(P(), 'oleg'), v3flag: !!P().v3};
$('#fab').click(); $('#panel [data-sc="partner"]').click(); o.partnerOnSolo = {scr:S.scr, cur:S.cur, name:P() && P().name, view: vt()};
// D. example: steps persist, list card contradicts
scenario('fresh'); ACT.consentOk(); for (let i = 0; i < 6; i++) $('#view [data-act="v3exStep"]') && $('#view [data-act="v3exStep"]').click();
o.example = {purchases:S.purchases.length, ls:Object.keys(localStorage), ex:S.v3.ex, view: vt(), log:S.v3.log.slice()};
ACT.v3own(); go('list'); o.exList = vt(); ACT.v3showEx(); o.exAgain = vt();
// E. weeksum in solo mentions? how sheet in solo/group
V3_SCEN.solo(); openSheet('how'); o.howSolo = $('#sheet').innerText; openSheet('cancelAsk'); o.cancelSolo = $('#sheet').innerText; openSheet('photo'); o.photoSolo = $('#sheet').innerText.slice(0, 200); closeSheet();
V3_SCEN.group3(); openSheet('cancelAsk'); o.cancelGroup = $('#sheet').innerText; openSheet('change'); o.changeGroup = $('#sheet').innerText; closeSheet();
// F. group: non-owner cancels the whole goal
V3_SCEN.group3(); S.who = 'anya'; go('purchase'); ACT.cancelBuy(); o.cancelByAnya = {purchases:S.purchases.length, scr:S.scr}; S.who = 'oleg'; go('list'); o.cancelByAnyaOlegSees = vt();
// G. group: share above price
V3_SCEN.group3(); openSheet('input', 'share'); $('#inputv').value = '120000'; $('#inputf').requestSubmit(); o.overShare = {share:P().share.oleg, promised: v3promised(P()), price:P().price, view: vt()};
// H. group: anya deletes all data
V3_SCEN.group3(); S.who = 'anya'; go('data'); ACT.delAll(); o.delAnya = {scr:S.scr, text:vt(), members:P('g3') && P('g3').group.members}; S.who = 'oleg'; S.cur = 'g3'; go('purchase'); o.delAnyaOlegSees = vt();
// I. group2 deadline move by partner
V3_SCEN.group2(); const g = P(), dl0 = g.dl, anyaPer0 = perDay(g, 'anya'); g.saved.oleg = 50000; v3took(g, 'oleg', 20000); $('#view [data-act="v3slipDate"]').click();
o.g2slip = {shiftDays: Math.round((g.dl - dl0) / DAY), anyaPerDayBefore: anyaPer0, anyaPerDayAfter: perDay(g, 'anya')};
return o;
