const ss = [...document.styleSheets].find(s => !s.href);
const cs = getComputedStyle(document.documentElement);
const out = {scr:S.scr, mqNot: matchMedia('not (prefers-contrast: more)').matches, mqMore: matchMedia('(prefers-contrast: more)').matches, rm: reduce(),
 media:[...ss.cssRules].filter(r => r.media).map(r => r.media.mediaText)};
for (const th of ['light','dark']) { document.documentElement.dataset.theme = th; const c = getComputedStyle(document.documentElement); out[th] = ['--ink2','--ai','--line','--fill'].map(k => k + '=' + c.getPropertyValue(k).trim()).join(' '); }
return out;
