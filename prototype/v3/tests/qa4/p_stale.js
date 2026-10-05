V3_SCEN.group3(); openSheet('v3direct'); const t0 = $('#sheet').innerText.replace(/\n+/g,' | ');
$('#fab').click(); $('#panel [data-sc="groupInvite"]').click();
const b = $('#sheet button'); b && b.focus();
return {before: t0, nowWho: S.who, scr: S.scr, sheetOpen: $('#sheetwrap').classList.contains('open'), staleSheetText: $('#sheet').innerText.replace(/\n+/g,' | '), focusInStale: document.activeElement === b};
