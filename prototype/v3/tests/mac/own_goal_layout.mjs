import { createRequire } from 'module'; import { pathToFileURL } from 'url';
const require = createRequire(process.cwd() + '/package.json'); const { chromium } = require('playwright');
const f = pathToFileURL(process.argv[2]).href; const b = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe' });
const errs = [];
for (const vp of [{ width: 320, height: 568 }, { width: 812, height: 375 }, { width: 375, height: 812 }]) {
  const p = await b.newPage({ viewport: vp }); p.on('pageerror', e => errs.push(e.message));
  await p.goto(f + '?clean&s=fresh'); await p.waitForTimeout(300);
  await p.click('#skip').catch(() => {}); await p.waitForTimeout(200);
  const clickT = async t => { const el = p.locator('button', { hasText: t }).first(); await el.click(); await p.waitForTimeout(800); };
  await clickT('Согласен'); await clickT('Создать свою цель');
  await p.fill('#phrase', 'Ноутбук 150 тысяч к 1 марта'); await clickT('Посчитать'); await clickT('всю сумму'); await clickT('Сохранить цель'); const sh = await p.evaluate(() => S.sheet); console.log('  sheet after save:', sh); await clickT('Войти через VK ID'); await clickT('Пока только я');
  const r = await p.evaluate(() => { const bar = $('#bottom .bottom') || $('#view .bottom.p-flow'), q = x => x && Math.round(x.getBoundingClientRect().height);
    const left = [...document.querySelectorAll('#view .left .num, #view [data-v3-money]')][0], lb = left && left.getBoundingClientRect();
    return { scr: S.scr, flow: !!$('#view .bottom.p-flow'), btns: bar ? bar.querySelectorAll('button').length : 0, barH: q(bar), H: innerHeight, sumVisible: lb ? lb.bottom <= innerHeight - (bar && !bar.classList.contains('p-flow') ? bar.getBoundingClientRect().height + 64 : 64) : null,
      hs: document.documentElement.scrollWidth > innerWidth }; });
  console.log(vp.width + '×' + vp.height, JSON.stringify(r));
  await p.screenshot({ path: process.env.TEMP + `/own_${vp.width}x${vp.height}.png` });
  /* «назад» с цели не ведёт на «Копить вместе?» */
  await p.goBack(); await p.waitForTimeout(500); console.log('  back →', await p.evaluate(() => S.scr));
  await p.close();
}
console.log('errors', errs.length, errs.slice(0, 3)); await b.close();
