# Fit every worked solution to its slides: build, measure each step in headless Chrome, and start a new
# slide before the first step that runs past the footer. Repeats until nothing overflows. Writes splits.json.
import json, os, re, subprocess, sys, tempfile
H = os.path.dirname(os.path.abspath(__file__))
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
DECK = os.path.join(H, '..', 'lectures', 'lecture-1', 'presentation.html')
MEASURE = r'''<style>*{transition:none!important;animation:none!important}</style><script>
const D=window.__deck,st=document.getElementById('stage'),R={};
D.slides.forEach((s,i)=>{if(!s.classList.contains('qslide'))return;D.show(i);D.setAll(s,true);
 const k=st.getBoundingClientRect().width/1280,top=st.getBoundingClientRect().top,b=e=>(e.getBoundingClientRect().bottom-top)/k;
 const solw=s.querySelector('.solw');const kids=solw?[...solw.children]:[];
 R[s.id]={steps:kids.filter(e=>!e.classList.contains('band')).map(b),bands:kids.filter(e=>e.classList.contains('band')).map(b),
   right:s.querySelector('.qr')?b(s.querySelector('.qr')):0,limit:720-36};});
document.documentElement.setAttribute('data-test',JSON.stringify(R));</script></body>'''


def measure():
    subprocess.run([sys.executable, os.path.join(H, 'build_deck.py')], check=True, capture_output=True)
    html = open(DECK, encoding='utf8').read().replace('</body>', MEASURE)
    d = tempfile.mkdtemp(dir=os.environ.get('TMPDIR'))
    p = os.path.join(d, 'm.html'); open(p, 'w', encoding='utf8').write(html)
    out = subprocess.run([CHROME, '--headless=new', '--disable-gpu', f'--user-data-dir={d}/p', '--window-size=1280,764', '--virtual-time-budget=20000', '--dump-dom', 'file://' + p], capture_output=True, text=True, timeout=300).stdout
    import html as hh
    return json.loads(hh.unescape(re.search(r'data-test="([^"]*)"', out).group(1)))


def is_eq(qid, idx, sols):
    return sols[qid][idx].startswith('=')


def sol_lists():
    """The final step list of every question, after the linking sentences, as the deck builds them."""
    sys.path.insert(0, H)
    R = lambda f: open(os.path.join(H, f), encoding='utf8').read()
    g = {'MODE': 'deck', 'R': R, '__name__': 'x'}
    src = R('content_a.py').replace('    sol, bounds, tls = _sync(sid, sol, tl, cuts)', '    sol, bounds, tls = _sync(sid, sol, tl, cuts); SOLS[sid] = sol')
    exec('SOLS = {}\n' + src, g); exec(R('content_b.py'), g); exec(R('content_c.py'), g)
    return g['SOLS']


SPL = os.path.join(H, 'splits.json')
for rnd in range(8):
    splits = json.load(open(SPL))
    sols = sol_lists()
    M = measure()
    changed, report = False, []
    for qid, sol in sols.items():
        cuts = splits.get(qid, [])
        bounds = [0] + cuts + [len(sol)]
        for j in range(len(bounds) - 1):
            sid = qid + ('' if j == 0 else 'bcdefg'[j - 1])
            m = M.get(sid)
            if not m: continue
            if m['right'] > m['limit'] + .5: report.append(f'{sid}: question and timeline column too tall ({m["right"]:.0f})')
            over = next((i for i, v in enumerate(m['steps']) if v > m['limit'] + .5), None)
            if over is None and m['bands'] and max(m['bands']) > m['limit'] + .5:
                over = len(m['steps']) - 1          # only the answer or notes overflow: the last step moves on
            if over is None: continue
            cut = bounds[j] + over
            if cut > bounds[j] and is_eq(qid, cut, sols) and not is_eq(qid, cut - 1, sols):
                cut -= 1                            # keep a sentence together with the equation it introduces
            if cut <= bounds[j]:
                report.append(f'{sid}: first step does not fit'); continue
            splits[qid] = sorted(set(cuts + [cut])); changed = True
            break
    json.dump(splits, open(SPL, 'w'), indent=0, sort_keys=True)
    print('round', rnd, 'changed' if changed else 'stable', report)
    if not changed: break
