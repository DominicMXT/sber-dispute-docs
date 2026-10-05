const W = s => (s.match(/[A-Za-zА-Яа-яЁё0-9]+/g) || []).length; const o = {};
for (const k of ['how','policy','remind','save','change','where','weeksum']) { openSheet(k); o[k] = W($('#sheet').innerText); closeSheet(); }
go('data'); o.dataFirst = W($('#view').innerText); return o;
