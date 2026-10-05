# Тест модуля motivation: полный прогон + открытие каждого кода по #хэшу, на двух размерах окна. Тестовые копии страниц удаляются.
# Размер задаётся через CDP (mt_cdp.mjs): headless Chrome не даёт окно уже 500 px, а телефон — 420×860.
import sys, io, json, subprocess, os
SRC = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))   # папка prototype
here = os.path.dirname(os.path.abspath(__file__))
t = io.open(os.path.join(here, 'mottest.js'), encoding='utf-8').read()
CODES = ['', 'dayprice', 'slip', 'slipPropose', 'weeks', 'weeksum3', 'nextgoal']
SIZES = ['1200,900', '420,860']   # десктоп и телефон
tp = tf = 0
for f in sys.argv[1:]:
    p = os.path.join(SRC, f); s = io.open(p, encoding='utf-8').read(); i = s.rindex('</body>')
    q = p.replace('.html', f'_mt{os.getpid()}.html')   # своё имя копии: параллельный прогон не удалит её из-под нас
    io.open(q, 'w', encoding='utf-8').write(s[:i] + t + s[i:])
    try:
        for size in SIZES:
            for c in CODES:
                url = 'file:///' + q.replace(chr(92), '/') + ('#' + c if c else '')
                for attempt in range(3):   # повтор — только если страница не отдала результат (Chrome не стартовал)
                    r = subprocess.run(['node', os.path.join(here, 'mt_cdp.mjs'), url, size], capture_output=True)
                    try:
                        d = json.loads(r.stdout.decode('utf-8', 'replace').strip().splitlines()[-1])
                    except Exception:
                        d = {'res': 'FAIL NO RESULT ' + r.stderr.decode('utf-8', 'replace')[-300:], 'cons': []}
                    if not d['res'].startswith('FAIL NO RESULT'):
                        break
                res, cons = d['res'], d['cons']
                fails = [l for l in res.splitlines() if l.startswith('FAIL')]
                np_, nf = res.count('PASS '), res.count('FAIL ') + len(cons)
                tp += np_; tf += nf
                out = f'=== {f} [{size}] #{c or "(полный прогон)"} · PASS {np_} / FAIL {nf} · console: {len(cons)}\n'
                out += (res if not c or fails else '\n'.join(l for l in res.splitlines() if l.startswith('INFO'))) + '\n'
                for l in cons[:5]: out += 'CONSOLE ' + l[:300] + '\n'
                sys.stdout.buffer.write(out.encode('utf-8'))
    finally:
        os.remove(q)
sys.stdout.buffer.write(f'ИТОГО PASS {tp} / FAIL {tf}\n'.encode('utf-8'))
