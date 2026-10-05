// QA №4: участник (не организатор) «Отменить покупку» удалял цель у всех. Проверяем лист, действие и вид у остальных.
const o = {}; S.who = 'oleg'; V3_SCEN.group3(); const p = P(); S.who = 'anya'; go('purchase');
openSheet('change'); o.memberSheet = $('#sheet').innerText.replace(/\n+/g, ' | ');
ACT.cancelBuy();   /* прямой вызов действия — даже в обход листа */
o.afterMemberCancel = {stillExists: S.purchases.includes(p), state: p.state, members: p.group.members.join(), gone: (p.group.gone || []).join(), anyaScreen: S.scr};
S.who = 'oleg'; S.cur = p.id; go('purchase'); o.ownerView = [...$$('#view .v3-member, #view .v3-gonerow')].map(x => x.innerText.replace(/\n+/g, ' ')).join(' | ');
openSheet('change'); o.ownerSheet = $('#sheet').innerText.replace(/\n+/g, ' | '); openSheet('cancelAsk'); o.ownerCancelAsk = $('#sheet').innerText.replace(/\n+/g, ' | ');
return o;
