# Headless test: inject a script into a copy of the deck, read the JSON from data-test in the dumped DOM.
# Usage: python3 test_deck.py [path to presentation.html]
import json, os, re, subprocess, sys, tempfile
H = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(H, '..', 'lectures', 'lecture-1', 'presentation.html')
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
EXPECT = {'fv': '608,326.45', 'fvvar': '419,901.68', 'nper': '3', 'pv': '7,129,861.79', 'pvvar': '345,441.09', 'cmp': '118,814.05', 'flows': '37,919.44', 'fva': '39,586.65',
          'pmtfv': '28,951.00', 'splitfv': '80,536.54', 'pva': '9,272.04', 'loan': '16,607.15', 'splitpv': '67,176.05', 'perp': '16,792,385.66'}
# inputs that reproduce further answers from the lesson: calc -> ({field: value}, expected)
ALT = [('perp', dict(pmt='6000', r='5', g='0', f='2/6'), '123,967.39'), ('perp', dict(pmt='50000', r='8', g='3', f='1'), '1,000,000.00'),
       ('fva', dict(pmt='4000', r='6', n='10', T='10', when='beg'), '55,886.57'), ('fva', dict(pmt='10000', r='4', n='8', T='8', when='end'), '92,142.26'),
       ('pva', dict(pmt='2000', r='2', n='24', f='1'), '37,827.85'), ('pva', dict(pmt='1000', r='1', n='24', f='0'), '21,455.82'),
       ('loan', dict(L='400000', r='0.8', n='600', when='beg'), '3,201.46'), ('pmtfv', dict(fv='500000', r='6', n='12', when='beg'), '27,960.86'),
       ('splitfv', dict(p1='4000', n1='8', r1='6', p2='7000', n2='4', r2='6', T='15'), '96,000.19'), ('flows', dict(a1='20000', t1='1', a2='30000', t2='3', a3='50000', t3='5', a4='0', t4='0', T='5', r='8'), None)]
TEST = r'''
(function(){
const D=window.__deckT,R={errors:[],overflow:[],small:[],mc:[],calc:[],alt:[],reveal:[],terms:[],abbr:{},chars:[],eqwide:[]};
window.addEventListener('error',e=>R.errors.push(e.message));
const st=document.createElement('style');st.textContent='*{transition:none!important;animation:none!important}';document.head.appendChild(st);
const stage=document.getElementById('stage');
function rel(e){const s=stage.getBoundingClientRect(),r=e.getBoundingClientRect(),k=s.width/1280;return{t:(r.top-s.top)/k,b:(r.bottom-s.top)/k,l:(r.left-s.left)/k,r:(r.right-s.left)/k};}
D.slides.forEach((s,i)=>{D.show(i);D.setAll(s,true);
 // reveal every multiple choice answer so that the open state is what gets measured
 s.querySelectorAll('.mc').forEach(m=>{m.classList.add('done');const a=+m.dataset.a;m.querySelectorAll('.o')[a].classList.add('ok');});
 const foot=s.querySelector('.ft');const limit=foot?720-36:716;let worst=0,who='',wl=0,wr=1280;
 s.querySelectorAll('*').forEach(e=>{if(e.closest('.ft')||e.closest('.pd-num')||e.classList.contains('orb')||e.closest('.orb'))return;const c=getComputedStyle(e);if(c.display==='none'||c.visibility==='hidden')return;const r=rel(e);if(r.b-r.t<1)return;
  if(r.b>worst){worst=r.b;who=e.tagName+'.'+(e.className.baseVal??e.className);}if(r.l<wl)wl=r.l;if(r.r>wr)wr=r.r;});
 if(worst>limit+.5||wl<-.5||wr>1280.5)R.overflow.push({i:i+1,id:s.id,bottom:Math.round(worst),limit,who,l:Math.round(wl),r:Math.round(wr)});
 // equations wider than their container
 s.querySelectorAll('.eq').forEach(e=>{const box=e.closest('.card,.solw,.cout,.fm,td,.slide');const inner=document.createRange();inner.selectNodeContents(e);const a=inner.getBoundingClientRect(),b=box.getBoundingClientRect();if(a.left<b.left-1||a.right>b.right+1)R.eqwide.push({id:s.id,t:e.textContent.slice(0,60),over:Math.round(Math.max(b.left-a.left,a.right-b.right))});});
 // text smaller than the board minimum
 const tw=document.createTreeWalker(s,NodeFilter.SHOW_TEXT);let n;const seen={};while((n=tw.nextNode())){if(!n.nodeValue.trim())continue;const p=n.parentElement;if(p.closest('.ft,sup,sub,tspan'))continue;let fs=parseFloat(getComputedStyle(p).fontSize);const svg=p.closest('svg');if(svg){const vb=svg.viewBox.baseVal.width;fs*=svg.getBoundingClientRect().width/(stage.getBoundingClientRect().width/1280)/vb;if(fs<14.5)seen['svg '+fs.toFixed(1)]=n.nodeValue.slice(0,24);}else if(fs<16.5)seen[fs]=n.nodeValue.slice(0,24);}
 if(Object.keys(seen).length)R.small.push({id:s.id,seen});
 // forbidden characters
 const txt=s.textContent;[['em','—'],['maqaf','־'],['en','–'],['ell','…'],['arrow','→'],['arrow2','⇒'],['q1','“'],['q2','”']].forEach(([k,c])=>{if(txt.includes(c))R.chars.push({id:s.id,k});});
 // abbreviations: remember the first slide of each, and whether it is explained there
 ['PV','FV','PMT','FVFA','PVFA','סר״ת','מעע״ס','מענ״ס'].forEach(a=>{if(!(a in R.abbr)&&txt.includes(a))R.abbr[a]=s.id;});
 s.querySelectorAll('.mc').forEach(m=>{m.classList.remove('done');m.querySelectorAll('.o').forEach(o=>o.classList.remove('ok','bad'));});
 D.setAll(s,false);
});
// reveals
D.slides.forEach((s,i)=>{const g=D.groups(s).length;D.show(i);let c=0;while(D.pending(s).length&&c<60){D.next();c++;}if(c!==g||D.cur()!==i)R.reveal.push({id:s.id,g,c,cur:D.cur()});const shownAll=[...s.querySelectorAll('.st')].every(e=>e.classList.contains('show'));if(!shownAll)R.reveal.push({id:s.id,err:'not all shown'});let b=0;while(D.groups(s).some(x=>x[0].classList.contains('show'))&&b<60){D.prev();b++;}if(b!==g||D.cur()!==i)R.reveal.push({id:s.id,back:b,g});});
D.show(0);let k=0;while(D.cur()<D.slides.length-1&&k<2000){D.next();k++;}R.walked=[k,D.cur()];
// multiple choice: wrong answer then right answer
document.querySelectorAll('.mc').forEach(m=>{const a=+m.dataset.a,os=[...m.querySelectorAll('.o')],w=m.querySelector('.w');const sl=m.closest('.slide');D.go(sl.id);
 const wrong=(a+1)%os.length;os[wrong].click();let ok=m.classList.contains('done')&&os[wrong].classList.contains('bad')&&os[a].classList.contains('ok')&&getComputedStyle(w).display!=='none'&&w.textContent.length>15;
 m.classList.remove('done');os.forEach(o=>o.classList.remove('ok','bad'));os[a].click();ok=ok&&os[a].classList.contains('ok')&&!os[wrong].classList.contains('bad');
 m.classList.remove('done');os.forEach(o=>o.classList.remove('ok','bad'));R.mc.push(ok?1:m.id);});
// calculators
const fire=e=>e.dispatchEvent(new Event('input',{bubbles:true}));
document.querySelectorAll('.calc').forEach(b=>{const id=b.dataset.calc,out=document.getElementById('out-'+id),res=()=>{const x=out.querySelector('[data-res]');return x?x.textContent:(out.textContent.slice(0,40));};
 const r0=res(),ins=[...b.querySelectorAll('input')],first=ins[0],v=first.value;first.value=String(parseFloat(v.replace(/,/g,''))*2);fire(first);const r1=res();first.value='abc';fire(first);const bad=!!out.querySelector('.err');first.value=v;fire(first);const r2=res();
 const overflow=(()=>{D.go('c-'+id);const q=rel(out),l=rel(b);return Math.round(Math.max(q.b,l.b));})();
 R.calc.push({id,r0,r1,changed:r0!==r1,bad,restored:r0===r2,bottom:overflow,inputs:ins.length});});
(document.querySelector('.calc')?window.__ALT:[]).forEach(([id,vals,exp])=>{const b=document.querySelector('.calc[data-calc="'+id+'"]'),out=document.getElementById('out-'+id);const saved=[...b.querySelectorAll('[data-k]')].map(e=>[e,e.value]);Object.entries(vals).forEach(([k,v])=>{const e=b.querySelector('[data-k="'+k+'"]');e.value=v;fire(e);});const x=out.querySelector('[data-res]');const got=x?x.textContent:out.textContent.slice(0,50);D.go('c-'+id);const rq=rel(out);R.alt.push({id,exp,got,ok:exp?got===exp:true,bottom:Math.round(rq.b)});saved.forEach(([e,v])=>{e.value=v;fire(e);});});
// glossary and links
document.querySelectorAll('[data-t]').forEach(t=>{if(!D.G[t.dataset.t])R.terms.push(t.dataset.t);});
R.termsUsed=new Set([...document.querySelectorAll('.slide [data-t]')].map(t=>t.dataset.t)).size;R.termsTotal=Object.keys(D.G).length;
R.unusedTerms=Object.keys(D.G).filter(k=>!document.querySelector('.slide [data-t="'+k+'"]'));
Object.keys(D.G).forEach(k=>{D.openTerm(k);const a=document.getElementById('dp').textContent,b=document.getElementById('dex').textContent;if(a.length<8||b.length<8)R.terms.push('empty '+k);});D.closeOverlays();
R.go=[...document.querySelectorAll('[data-go]')].filter(g=>!document.getElementById(g.dataset.go)).map(g=>g.dataset.go);
R.count=D.slides.length;R.opener=[...document.querySelectorAll('.pd')].length;R.st=document.querySelectorAll('.st').length;R.mcN=document.querySelectorAll('.mc').length;R.calcN=document.querySelectorAll('.calc').length;
document.documentElement.setAttribute('data-test',JSON.stringify(R));
})();
'''
html = open(SRC, encoding='utf8').read()
# expose the deck object to the test
html = html.replace('window.__deck={', 'window.__deckT={G,')
inj = '<script>window.__ALT=' + json.dumps(ALT, ensure_ascii=False) + ';' + TEST + '</script></body>'
html = html.replace('</body>', inj)
d = tempfile.mkdtemp(dir=os.environ.get('TMPDIR'))
p = os.path.join(d, 't.html')
open(p, 'w', encoding='utf8').write(html)
out = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', f'--user-data-dir={d}/prof', '--window-size=1280,764', '--virtual-time-budget=60000', '--dump-dom', 'file://' + p], capture_output=True, text=True, timeout=300).stdout
m = re.search(r'<html[^>]*data-test="([^"]*)"', out)
if not m:
    print('NO RESULT'); print(out[:400]); sys.exit(1)
import html as hh
R = json.loads(hh.unescape(m.group(1)))
print('slides', R['count'], 'openers', R['opener'], 'reveal items', R['st'], 'mc', R['mcN'], 'calcs', R['calcN'], 'walk', R['walked'])
print('errors', R['errors'])
print('overflow', len(R['overflow']));[print('  ', o) for o in R['overflow']]
print('eq wider than box', len(R['eqwide']));[print('  ', o) for o in R['eqwide']]
print('small text', len(R['small']));[print('  ', o) for o in R['small'][:40]]
print('chars', R['chars'])
print('abbr first seen', R['abbr'])
print('reveal problems', R['reveal'])
bad = [x for x in R['mc'] if x != 1]
print('mc ok', len(R['mc']) - len(bad), 'bad', bad)
for c in R['calc']:
    exp = EXPECT[c['id']]
    print('  calc', c['id'], 'default', c['r0'], 'OK' if c['r0'] == exp else 'EXPECTED ' + exp, 'changed' if c['changed'] else 'NOCHANGE', 'badinput' if c['bad'] else 'NOERR', 'restored' if c['restored'] else 'NOTRESTORED', 'bottom', c['bottom'])
for a in R['alt']:
    print('  alt', a['id'], a['got'], 'OK' if a['ok'] else 'EXPECTED ' + str(a['exp']), 'bottom', a['bottom'])
print('terms missing', R['terms'], 'used', R['termsUsed'], 'of', R['termsTotal'], 'unused', R['unusedTerms'], 'bad go', R['go'])
