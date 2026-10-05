import sys, io, re, html, subprocess, os
SRC = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))   # папка prototype
CH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
here = os.path.dirname(os.path.abspath(__file__))
t = io.open(os.path.join(here, 'flowtest.js'), encoding='utf-8').read()
for f in sys.argv[1:]:
    p = os.path.join(SRC, f); s = io.open(p, encoding='utf-8').read(); i = s.rindex('</body>')
    q = p.replace('.html', '_ft.html'); io.open(q, 'w', encoding='utf-8').write(s[:i] + t + s[i:])
    r = subprocess.run([CH, '--headless=new', '--disable-gpu', '--user-data-dir=' + os.path.join(here, 'prof'), '--enable-logging=stderr', '--v=0',
                        '--virtual-time-budget=4000', '--window-size=1200,900', '--dump-dom', 'file:///' + q.replace('\\', '/')], capture_output=True)
    os.remove(q)
    d = r.stdout.decode('utf-8', 'replace'); m = re.search(r'<pre id="T">(.*?)</pre>', d, re.S)
    res = html.unescape(m.group(1)) if m else 'NO RESULT'
    cons = [l for l in r.stderr.decode('utf-8', 'replace').splitlines() if 'CONSOLE' in l]
    sys.stdout.buffer.write(f'=== {f}\n{res}\nPASS {res.count("PASS ")} / FAIL {res.count("FAIL ")} · console: {len(cons)}\n'.encode('utf-8'))
    for l in cons[:5]: sys.stdout.buffer.write((l[:300] + '\n').encode('utf-8'))
