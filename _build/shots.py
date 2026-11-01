# Screenshot chosen slides with every reveal shown. Usage: python3 shots.py outdir [ids...] (no ids: all, in parallel)
import os, re, subprocess, sys, tempfile, concurrent.futures as cf
H = os.path.dirname(os.path.abspath(__file__))
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
src = open(os.path.join(H, '..', 'lectures', 'lecture-1', 'presentation.html'), encoding='utf8').read()
ids = sys.argv[2:] or re.findall(r'<section class="slide[^"]*" id="([^"]+)"', src)
d = tempfile.mkdtemp(dir=os.environ.get('TMPDIR'))
INJ = '''<style>*{transition:none!important;animation:none!important}</style><script>const D=window.__deck;const s=D.slides.find(x=>x.id===location.hash.slice(1));D.go(s.id);D.setAll(s,true);D.next&&0;s.querySelectorAll('.mc').forEach(m=>{m.classList.add('done');m.querySelectorAll('.o')[+m.dataset.a].classList.add('ok');});</script></body>'''
p = os.path.join(d, 't.html')
open(p, 'w', encoding='utf8').write(src.replace('</body>', INJ))
all_ids = re.findall(r'<section class="slide[^"]*" id="([^"]+)"', src)
def one(i):
    n = all_ids.index(i) + 1
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', f'--user-data-dir={d}/p{n}', '--window-size=1280,764', '--virtual-time-budget=3000', '--hide-scrollbars', f'--screenshot={out}/{n:03d}-{i}.png', f'file://{p}#{i}'], capture_output=True, timeout=120)
with cf.ThreadPoolExecutor(6) as ex:
    list(ex.map(one, ids))
print(len(ids))
