V3_SCEN.group3(); const p = P(); const d = $('#view').textContent;
const own = {left: fmt(leftOf(p,'oleg')), perDay: fmt(perDay(p,'oleg'))};
return {own, hasLeft: d.includes(own.left), hasPer: d.includes(own.perDay), snap: p.group.snap, text: $('#view').innerText.slice(0, 1500)};
