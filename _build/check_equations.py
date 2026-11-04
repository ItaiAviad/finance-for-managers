# Arithmetic check of every equation in the built deck: each "=" chain whose sides are all numeric must agree.
# Usage: python3 check_equations.py [presentation.html]
import html, os, re, sys
from html.parser import HTMLParser
H = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(H, '..', 'lectures', 'lecture-' + os.environ.get('LESSON', '1'), 'presentation.html')


class Node:
    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.parent, self.kids = tag, dict(attrs), parent, []

    @property
    def cls(self): return self.attrs.get('class', '').split()


class P(HTMLParser):
    VOID = {'br', 'img', 'input', 'meta', 'link', 'hr', 'circle', 'line', 'polygon', 'path'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node('root', [], None); self.cur = self.root; self.slide = None

    def handle_starttag(self, t, a):
        n = Node(t, a, self.cur); self.cur.kids.append(n)
        if t not in self.VOID: self.cur = n

    def handle_endtag(self, t):
        x = self.cur
        while x is not self.root and x.tag != t: x = x.parent
        if x is not self.root: self.cur = x.parent

    def handle_data(self, d): self.cur.kids.append(d)


def expr(n):
    """Node -> python-ish expression string."""
    if isinstance(n, str): return n
    if n.tag in ('svg', 'script', 'style'): return ''
    if 'frac' in n.cls:
        parts = [k for k in n.kids if not isinstance(k, str)]
        return '((' + expr(parts[0]) + ')/(' + expr(parts[1]) + '))'
    if 'mh' in n.cls: return '§'
    inner = ''.join(expr(k) for k in n.kids)
    if n.tag == 'sup': return '**(' + inner + ')'
    if n.tag == 'sub': return '_' + re.sub(r'\W', '', inner)
    return inner


def FVFA(r, t): return ((1 + r) ** t - 1) / r
def PVFA(r, t): return (1 - (1 + r) ** -t) / r if t != float('inf') else 1 / r


def norm(s):
    s = s.replace(' ', '').replace('×', '*').replace('·', '*').replace('−', '-').replace('∞', 'INF').replace('÷', '/')
    s = re.sub(r'(?<=\d),(?=\d{3})', '', s)
    s = re.sub(r'(\d+(?:\.\d+)?)%', r'(\1/100)', s)
    s = re.sub(r'\)\s*\(', ')*(', s)
    s = re.sub(r'(?<=[\d)])\s*\(', '*(', s).replace('FVFA*(', 'FVFA(').replace('PVFA*(', 'PVFA(')
    return s


def ev(seg):
    seg = seg.strip()
    if not seg or re.search(r'[A-Za-z_§]', re.sub(r'\b(FVFA|PVFA|INF)\b', '', seg)): return None
    try:
        return float(eval(seg, {'__builtins__': {}}, {'FVFA': FVFA, 'PVFA': PVFA, 'INF': float('inf')}))
    except Exception:
        return None


p = P(); p.feed(open(SRC, encoding='utf8').read())
slides = []


def walk(n, sid):
    if isinstance(n, str): return
    if n.tag == 'section' and 'slide' in n.cls: sid = n.attrs.get('id')
    if 'eq' in n.cls or 'm' in n.cls:
        slides.append((sid, n)); return
    for k in n.kids: walk(k, sid)


walk(p.root, None)
checked = bad = 0
prev = (None, '')
for sid, n in slides:
    raw = expr(n)
    s = norm(raw)
    # a line that starts with "=" continues the previous display equation on the same slide
    if 'eq' in n.cls and s.strip().startswith('=') and prev[0] == sid and prev[1]:
        s = prev[1] + ' ' + s
    if 'eq' in n.cls:
        prev = (sid, re.split(r'=|≈', s)[-1])
    if '§' in s: s = s.split(':', 1)[-1]          # a Hebrew label before the equation
    for piece in re.split(r',\s(?=[A-Za-z(])', s):  # "PMT = 100, t = 12"
        segs = re.split(r'=|≈', piece)
        vals = [ev(x) for x in segs]
        for a, b, sa, sb in zip(vals, vals[1:], segs, segs[1:]):
            if a is None or b is None: continue
            checked += 1
            tol = max(abs(b) * 3e-6, 0.021)
            if abs(a - b) > tol:
                bad += 1
                print(f'{sid}: {sa.strip()[:60]} = {sb.strip()[:40]}  ({a:,.4f} vs {b:,.4f})')
print('equation pairs checked', checked, 'mismatches', bad)
