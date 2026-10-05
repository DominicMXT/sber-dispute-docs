V3_SCEN.group2(); openSheet('save'); closeSheet(); await new Promise(r => setTimeout(r, 600));
const sh = $('#sheet'), r = sh.getBoundingClientRect(), btn = $('#sheet button, #sheet input');
let focusable = false; if (btn) { btn.focus(); focusable = document.activeElement === btn; }
return {sheetOpen: $('#sheetwrap').classList.contains('open'), ariaModal: sh.getAttribute('aria-modal'), inert: sh.inert, ariaHidden: sh.getAttribute('aria-hidden'), visibility: getComputedStyle(sh).visibility,
  top: Math.round(r.top), vh: innerHeight, staleText: sh.innerText.slice(0, 80), staleFocusable: focusable, focusedTag: document.activeElement.tagName + '#' + document.activeElement.id};
