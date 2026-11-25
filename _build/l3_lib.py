# Lesson 3 helpers, executed after core.py: NPV curves drawn step by step, explanation buttons, cash-flow tables.
_XB = [0]


def XB(label, text):
    """A button that opens a short explanation over the slide (deck). In the PDF the explanation is printed in place."""
    _XB[0] += 1
    body = f'<b>{TX(label)}</b>' + ''.join(f'<p>{TX(p)}</p>' for p in ([text] if isinstance(text, str) else text))
    return f'<span class="xbw"><button class="xbtn" type="button" data-k="x{_XB[0]}">{TX("ⓘ " + label)}</button><span class="xnote">{body}</span></span>'


def NPVF(cf):
    """The NPV of a cash flow list (time 0 first) as a function of the rate r (a decimal)."""
    return lambda r: sum(c / (1 + r) ** t for t, c in enumerate(cf))


_ANC = {'start': 'end', 'end': 'start', 'middle': 'middle'}   # the labels are RTL text: 'start' here means the text runs to the right of x


def _iso(t):
    """Isolate every number in an RTL chart label, so '−50' does not print as '50−'."""
    return re.sub(r'[A-Za-z]\w*(?:\([^)]*\))?\s*=\s*[−-]?\d+(?:[.,]\d+)*%?|(?:(?<![\u0590-\u05ff])[−-])?\d+(?:[.,]\d+)*%?', lambda m: '\u2066' + m.group(0) + '\u2069', str(t))


def CURVE(series, xmax, ymin, ymax, xt, yt, marks=(), zones=(), W=1120, H=330, ylab='NPV', xlab='r', yfmt=None, note=None):
    """An NPV curve. series: dicts f (function of r), c (colour), lab (label text), n (reveal step), lx (r where the label sits).
    marks: dicts x, y, t (text), n, c, dy (text offset), v (draw a dotted line down to the axis), anchor.
    zones: dicts x0, x1, c (fill), t (text), n. The axis r runs left to right, as in every textbook graph."""
    L, Rr, T, B = 86, W - 40, 22, H - 46
    X = lambda r: L + (Rr - L) * r / xmax
    Y = lambda v: T + (B - T) * (ymax - v) / (ymax - ymin)
    yf = yfmt or (lambda v: f'{v:,.0f}'.replace('-', '−'))
    cid = f'cv{len(SL)}{abs(hash(str(xt) + str(yt))) % 9999}'
    o = [f'<svg class="cvx" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img">',
         f'<defs><clipPath id="{cid}"><rect x="{L}" y="{T - 4}" width="{Rr - L + 4}" height="{B - T + 8}"/></clipPath></defs>']
    for z in zones:
        o.append(f'<g class="st" data-n="{z["n"] * 10}"><rect x="{X(z["x0"]):.1f}" y="{T}" width="{X(z["x1"]) - X(z["x0"]):.1f}" height="{B - T}" fill="{z["c"]}" opacity=".16"/>'
                 + (f'<text x="{(X(z["x0"]) + X(z["x1"])) / 2:.1f}" y="{(Y(z["ty"]) if "ty" in z else T + 22):.1f}" text-anchor="middle" font-size="18" font-weight="800" fill="{z.get("tc", "#2a3858")}" direction="rtl">{_iso(z["t"])}</text>' if z.get('t') else '') + '</g>')
    for v in yt:
        y = Y(v)
        o.append(f'<line x1="{L}" y1="{y:.1f}" x2="{Rr}" y2="{y:.1f}" stroke="#e3ddd0" stroke-width="1"/>'
                 f'<text x="{L - 10}" y="{y + 6:.1f}" text-anchor="end" font-size="17" fill="#5d6a86">{yf(v)}</text>')
    for r in xt:
        x = X(r)
        o.append(f'<line x1="{x:.1f}" y1="{T}" x2="{x:.1f}" y2="{B}" stroke="#efe9de" stroke-width="1"/>'
                 f'<text x="{x:.1f}" y="{B + 26}" text-anchor="middle" font-size="17" fill="#5d6a86">{r * 100:.0f}%</text>')
    y0 = Y(0) if ymin <= 0 <= ymax else B
    o.append(f'<line x1="{L}" y1="{y0:.1f}" x2="{Rr + 14}" y2="{y0:.1f}" stroke="#1b2d55" stroke-width="2.6"/>'
             f'<polygon points="{Rr + 22},{y0:.1f} {Rr + 9},{y0 - 6:.1f} {Rr + 9},{y0 + 6:.1f}" fill="#1b2d55"/>'
             f'<text x="{Rr + 18}" y="{y0 - 12:.1f}" text-anchor="end" font-size="19" font-weight="800" fill="#1b2d55">{xlab}</text>'
             f'<line x1="{L}" y1="{B}" x2="{L}" y2="{T - 12}" stroke="#1b2d55" stroke-width="2.6"/>'
             f'<polygon points="{L},{T - 20} {L - 6},{T - 7} {L + 6},{T - 7}" fill="#1b2d55"/>'
             f'<text x="{L + 10}" y="{T - 4}" font-size="19" font-weight="800" fill="#1b2d55">{ylab}</text>')
    for s in series:
        pts = []
        for i in range(161):
            r = xmax * i / 160
            pts.append(f'{X(r):.1f},{Y(s["f"](r)):.1f}')
        lab = ''
        if s.get('lab'):
            lx = s.get('lx', xmax * .1)
            ly = Y(s['f'](lx)) + s.get('ldy', -14)
            lab = f'<text x="{X(lx):.1f}" y="{ly:.1f}" font-size="18" font-weight="800" fill="{s["c"]}" text-anchor="middle" direction="rtl">{_iso(s["lab"])}</text>'
        o.append(f'<g class="st" data-n="{s["n"] * 10}"><polyline class="cvl" pathLength="1" clip-path="url(#{cid})" points="{" ".join(pts)}" fill="none" stroke="{s["c"]}" stroke-width="4.2" stroke-linejoin="round"/>{lab}</g>')
    for m in marks:
        x, y = X(m['x']), Y(m['y'])
        c = m.get('c', '#ff6a4d')
        g = ''
        if m.get('v'):
            g += f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x:.1f}" y2="{y0:.1f}" stroke="{c}" stroke-width="1.8" stroke-dasharray="4 5"/>'
        if m.get('h'):
            g += f'<line x1="{L}" y1="{y:.1f}" x2="{Rr}" y2="{y:.1f}" stroke="{c}" stroke-width="2" stroke-dasharray="7 6"/>'
        if m.get('dot', True):
            g += f'<circle class="cpt" cx="{x:.1f}" cy="{y:.1f}" r="7.5" fill="#fff" stroke="{c}" stroke-width="3.4"/>'
        if m.get('t'):
            g += (f'<text x="{x + m.get("dx", 0):.1f}" y="{y + m.get("dy", -16):.1f}" text-anchor="{_ANC.get(m.get("anchor", "middle"))}" font-size="18" font-weight="800" '
                  f'fill="{m.get("tc", c)}" direction="rtl">{_iso(m["t"])}</text>')
        o.append(f'<g class="st" data-n="{m["n"] * 10}">{g}</g>' if m.get('n') else g)
    o.append('</svg>')
    svg = ''.join(o)
    return svg + (f'<p class="cap">{TX(note)}</p>' if note else '')


def CFT(rows, years=None, head='שנה', cls='', nohead=False):
    """A cash-flow table: one row per item, one column per year. A cell is a number (shown with a minus sign when negative),
    text, or (value, step) to reveal it on a click."""
    years = years if years is not None else list(range(len(rows[0][1])))
    h = f'<th>{TX(head)}</th>' + ''.join(f'<th>{TX(str(y))}</th>' for y in years)

    def cell(v):
        n = 0
        if isinstance(v, tuple): v, n = v
        if isinstance(v, (int, float)):
            t = f'{abs(v):,.0f}' if float(v).is_integer() else f'{abs(v):,.2f}'
            t = ('−' if v < 0 else '') + t
            k = 'neg' if v < 0 else 'pos'
        else:
            t, k = str(v), ''
        inner = TX(t) if not t.startswith('−') else '<span class="n">' + t + '</span>'
        return (f'<td class="st {k}" data-n="{n * 10}">{inner}</td>' if n else f'<td class="{k}">{inner}</td>')
    body = ''.join('<tr><td><b>' + TX(lab) + '</b></td>' + ''.join(cell(v) for v in vals) + '</tr>' for lab, vals in rows)
    return f'<table class="tbl2 cft {cls}">' + ('' if nohead else f'<tr>{h}</tr>') + f'{body}</table>'


# lesson 3 notation: NPV, IRR, PI and EAV formulas count as general formulas, get a legend and a formula chip
import lib as _lib
_isf0 = _lib.is_formula


def is_formula(s):
    if _isf0(s): return True
    if not re.search(r'\b(NPV|IRR|PI|EAV|EAC)\b|CF_\{|I_\{0\}', s): return False
    rest = re.sub(r'_\{[^}]*\}|\^\{-?[\dt]\}', '', s)
    return not re.search(r'\d[\d,]*\.\d|\d{2,}|\d%|[2-9]', rest)


_lib.is_formula = is_formula
_lib.NUM = re.compile(r'(?<![\w.,/])−?\d+(?:,\d{3})*(?:\.\d+)?%?')     # a comma after a number stays outside it
SYM[:0] = [('NPV', 'NPV', 'ערך נוכחי נקי'), ('IRR', 'IRR', 'שיעור תשואה פנימי'), ('I_{0}', 'I<sub>0</sub>', 'ההשקעה בזמן 0'),
           ('CF_{t}', 'CF<sub>t</sub>', 'התזרים בשנה t'), ('CF_{1}', 'CF<sub>1</sub>, CF<sub>2</sub>', 'התזרים בשנה 1, בשנה 2'),
           ('CF', 'CF', 'התזרים השנתי'), ('EAC', 'EAC', 'עלות שנתית שקולה'), ('OC', 'OC', 'עלות הפעלה שנתית'), ('PI', 'PI', 'מדד הרווחיות'), ('EAV', 'EAV', 'שווה הערך השנתי')]
AUTO[:0] = [('NPV', 'npv'), ('IRR', 'irr')]
FORMULA.update({'npv': 'NPV = -I_{0} + \\f{CF_{1}}{(1 + r)^{1}} + \\f{CF_{2}}{(1 + r)^{2}} + ...',
                'npva': 'NPV = -I_{0} + CF × \\f{1 - (1 + r)^{-t}}{r}',
                'pi': 'PI = \\f{NPV}{I_{0}}', 'npvpv': 'NPV = -I_{0} + PV', 'npvsum': 'NPV_{A+B} = NPV_{A} + NPV_{B}',
                'npvf': 'NPV = -I_{0} + CF × PVFA(r,t) + F × (1 + r)^{-t}', 'pvfa': 'PVFA(r,t) = \\f{1 - (1 + r)^{-t}}{r}',
                'rper': 'r_{n} = (1 + r)^{n} - 1', 'pvs': 'PV = CF × \\f{1 - (1 + r)^{-t}}{r}', 'pv1': 'PV = \\f{FV}{(1 + r)^{t}} = FV × (1 + r)^{-t}', 'eac': 'EAC = \\f{I_{0}}{PVFA(r,t)} + OC', 'eav': 'EAV = \\f{NPV}{PVFA(r,t)}'})
_fam0 = families


def families(e):
    f = _fam0(e)
    if re.match(r'\s*NPV', e):
        rhs = e.split('=', 1)[1] if '=' in e else ''
        r1 = rhs.split(' = ')[0]
        if re.fullmatch(r'\s*-\s*(I_\{0\}|[\d,.]+)(\s*\+\s*(PV(_\{[^}]*\})?|[\d,.]+))+\s*', r1):
            return {'npvpv'}
        if re.fullmatch(r'\s*-?[\d,.]+(\s*[+−-]\s*[\d,.]+)+\s*', r1):
            return set()                        # plain arithmetic of values already on the slide (NPV at r = 0)
        if not re.match(r'\s*-', rhs):          # no investment on the right: a sum of NPVs, NPVs moved in time, or a loan
            if re.match(r'\s*[\d,.]+(?:\s*\+\s*[\d,.]+)+\s*(=|$)', rhs) or re.match(r'\s*\d+ × [\d,.]+ \+', rhs): f.add('npvsum')
        else:
            uneven = bool(re.search(r'\\f\{(?:[^{}]|\{[^{}]*\})*\}\{\(?1', e)) and 'pvs' not in f
            flat = r1
            while re.search(r'\{[^{}]*\}', flat): flat = re.sub(r'\{[^{}]*\}', '', flat)
            terms = len(re.findall(r' \+ ', flat))
            f.add('npv' if uneven else ('npvf' if terms >= 2 and '×' in r1 else 'npva')); f -= {'pvs', 'fv1', 'perp'}
            if not uneven and terms >= 2: f -= {'pv1'}
            if uneven: f -= {'pv1', 'fvv', 'pvv'}
    if re.match(r'\s*PI(?![A-Za-z])', e): f.add('pi')
    if re.match(r'\s*PVFA', e): return {'pvfa'}
    if re.match(r'\s*r_\{\d+\}', e): return {'rper'}
    if re.search(r'\\f\{[A-Z]\w*\}\{\(1 \+ r\)\^\{t\}\}', e): f.add('pv1')
    if re.match(r'\s*EAV', e): f.add('eav'); f.discard('pvs')
    if re.match(r'\s*EAC', e): f -= {'pvs'}; f.add('eac')
    if 'IRR' in e or re.match(r'\s*X', e): f -= {'perp', 'pv1', 'fv1'}
    return f


# ================================================================ lesson 3: a finer click by click (the lecturer's review, 2026-11-25)
# A worked question now runs: the data first, one figure per click (its symbol, its value and what it is; the same click marks
# the figure in the question and draws its arrow on the timeline), then one sentence per click, a formula on its own click
# before its substitution, and the given figures keep their colour inside every equation. Interim results inside sentences
# (A = B = C) also appear piece by piece. Lessons 1 and 2 do not run this file, so they are unchanged.
import sys as _sys


def D(sym, val, heb, at=(), hl=None, alt=(), show=None):
    """One given figure: its symbol (math), its value as written, what it is in words, the timeline ticks it draws,
    the text to mark in the question (default: the value) and other ways the value is written in equations (0.10 for 10%)."""
    at = at if isinstance(at, (list, tuple)) else [at]
    return dict(sym=sym, val=val, heb=heb, at=[str(a) for a in at], hl=hl, alt=tuple(alt) if isinstance(alt, (list, tuple)) else (alt,), show=show)


_DATA = [[]]          # the figures of the question being rendered, for the colours inside its equations


def _sents(t):
    """Split prose into sentences, never inside math or inside a tag pair. '<b>כותרת.</b> המשך' splits after the bold."""
    out, cur, i, inm, depth = [], '', 0, False, 0
    while i < len(t):
        c = t[i]
        if c == '<' and not inm and re.match(r'</?[a-zA-Z][^<>]*>', t[i:]):
            j = t.index('>', i); tag = t[i:j + 1]; cur += tag; i = j + 1
            if tag.startswith('</'): depth -= 1
            elif not tag.endswith('/>') and not re.match(r'<(br|img|input)\b', tag): depth += 1
            if depth == 0 and tag.startswith('</') and re.search(r'[.?!]$', re.sub(r'<[^>]+>', '', cur).rstrip()) and t[i:i + 1] == ' ':
                out.append(cur.strip()); cur = ''; i += 1
            continue
        cur += c; i += 1
        if c == '$': inm = not inm
        if c in '.?!' and not inm and depth == 0 and t[i:i + 1] == ' ':
            out.append(cur.strip()); cur = ''; i += 1
    if cur.strip(): out.append(cur.strip())
    j = 0
    while j < len(out) - 1:                 # a bold run-in heading alone ("<b>שלב 1.</b>") stays with its sentence
        if re.fullmatch(r'<b>[^<]*</b>', out[j]): out[j:j + 2] = [out[j] + ' ' + out[j + 1]]
        else: j += 1
    return out


def _pieces(m):
    """An inline calculation A = B = C splits into 'A = B', '= C'. A formula or a single relation stays whole."""
    ps = _split_eq(m)
    if len(ps) < 3 or not re.search(r'\d', m): return [m]
    if ps[0][1] == '': return [f'{sg} {x}' for sg, x in ps[1:]]
    return [f'{ps[0][1]} {ps[1][0]} {ps[1][1]}'] + [f'{sg} {x}' for sg, x in ps[2:]]


def _atoms(text, step):
    """Prose as sentences and calculation pieces, each on its own reveal step. step(k) gives the data-n of atom k.
    Returns (html, number of atoms)."""
    html, k = '', 0
    for si, sn in enumerate(_sents(text)):
        if si: k += 1; html += ' '
        parts = re.split(r'(\$[^$]+\$)', sn)
        depth, split_ok = 0, True
        for p in parts:                    # a tag that spans a calculation keeps the sentence whole
            if p.startswith('$') and depth: split_ok = False
            if not p.startswith('$'):
                depth += len(re.findall(r'<(?!/)(?![^>]*/>)[^>]+>', p)) - len(re.findall(r'</[^>]+>', p))
        if not split_ok:
            html += f'<span class="st" data-n="{step(k)}">{TX(sn)}</span>'; continue
        calcs = 0
        for p in parts:
            if p.startswith('$') and p.endswith('$') and len(p) > 1:
                pcs = _pieces(p[1:-1])
                if len(pcs) > 1:
                    if calcs: k += 1        # a second calculation in the sentence waits for its own click
                    calcs += 1
                inner = ''
                for j, pc in enumerate(pcs):
                    if j: k += 1
                    inner += f'<span class="st" data-n="{step(k)}">{_colour(M(pc))}{" " if j < len(pcs) - 1 else ""}</span>'
                html += f'<span class="m" dir="ltr">{inner}</span>'
            elif p:
                html += f'<span class="st" data-n="{step(k)}">{TX(p)}</span>'
    return html, k + 1


def SUB(n):
    """Sub-steps inside one numbered step of an ordinary slide: n*10, n*10.4, ... (so the slide's own numbering stays)."""
    return lambda k: f'{n * 10 + k * 0.4:.1f}'.rstrip('0').rstrip('.')


def TXS(text, n):
    """Prose that appears sentence by sentence (and calculation by calculation) from step n of an ordinary slide."""
    return _atoms(text, SUB(n))[0] if n else TX(text)


def DEF(name, text, demo, n=0, trm=None):
    """A definition: the name and its meaning, sentence by sentence, and then the numerical example."""
    hd = f'[[{trm}|{name}]]' if trm else name
    if not n:
        return f'<div class="card def"><b class="dn">{TX(hd)}</b><p>{TX(text)}</p><div class="demo"><b>דוגמה:</b> {TX(demo)}</div></div>'
    st = SUB(n)
    a, c = _atoms(text, st)
    b, _ = _atoms(demo, lambda k: st(c + 1 + k))
    inner = f'<b class="dn">{TX(hd)}</b><p>{a}</p><div class="demo st" data-n="{st(c)}"><b>דוגמה:</b> {b}</div>'
    return ST(n, inner, cls='card def')


def BAND(kind, text, n=0):
    lab = {'dg': 'דגש', 'trap': 'המלכודת', 'note': 'הערה', 'dg2': 'שני דגשים', 'warn': 'חשוב', 'tip': 'טיפ'}.get(kind, '')
    head = f'<b>{lab}:</b> ' if lab else ''
    return ST(n, head + _atoms(text, SUB(n))[0], cls='band ' + kind) if n else f'<div class="band {kind}">{head}{TX(text)}</div>'


_NUMX = re.compile(r'(?<![\d.,])\d(?:\d|,(?=\d{3}))*(?:\.\d+)?%?(?![\d%]|[.,]\d)')


def _colour(h, sub=False):
    """Give every given figure inside rendered math the colour of its data row. One-digit values only in a substitution."""
    if not _DATA[0] or not sub: return h
    look, seen = {}, {}
    for d in _DATA[0]:                      # a value given twice with two meanings stays uncoloured
        v = str(d['val']).replace('−', '').replace('-', '')
        seen[v] = seen.get(v, 0) + 1
    for i, d in enumerate(_DATA[0]):
        for v in (d['val'],) + d['alt']:
            v = str(v).replace('−', '').replace('-', '')
            if len(re.sub(r'\D', '', v)) < 2 and not sub or seen.get(v, 0) > 1: continue
            look.setdefault(v, i % 8 + 1)
    out = []
    for seg in re.split(r'(<[^>]+>)', h):
        if seg.startswith('<'): out.append(seg); continue
        out.append(_NUMX.sub(lambda m: f'<span class="dv d{look[m.group(0)]}">{m.group(0)}</span>' if m.group(0) in look else m.group(0), seg))
    return ''.join(out)


def _seq(e, n, cls='eq', prev=''):
    """As in core, and each given figure keeps its data colour."""
    html = ''
    for k, (m, note) in enumerate(eq_pieces(e, prev)):
        nt = f'<span class="nt">{TX(note)}</span>' if note else ''
        chunks = _chunks(m) if len(m) > 46 else [m]
        sub = k == 0 and note == 'מציבים את הנתונים'
        for c, ch in enumerate(chunks):
            last = c == len(chunks) - 1
            html += f'<span class="sg st" data-n="{(n + k) * 10}"><span class="sm">{_colour(M(ch), sub)}</span>{nt if last else ""}</span>'
    return f'<div class="{cls} seq" dir="ltr">{html}</div>'


def seg_count(it):
    if it.startswith('@') or it.startswith('#fx:'): return 1
    if it.startswith('?'): return 0
    if it.startswith('=!'): return len(eq_pieces(it[2:]))
    if it.startswith('=') and not is_formula(it[1:]): return len(eq_pieces(it[1:]))
    if it.startswith('='): return 1
    return _atoms(it, lambda k: '0')[1]


def _drow(d, i, n, first, static=False):
    k = i % 8 + 1
    hd = f'<b class="dhd">{TX("מה נתון בשאלה")}</b>' if first else ''
    st = '' if static else f' st" data-n="{n * 10}'
    hm = re.fullmatch(r'\\h\{([^}]*)\}', d['sym'])      # a label in words reads right to left: "תחזוקה = 4,000"
    if d.get('show'): sym = f'<span class="dsym rtl">{TX(d["show"])}</span>'
    else: sym = f'<span class="dsym rtl">{TX(hm.group(1) + " = " + d["val"])}</span>' if hm else f'<span class="dsym" dir="ltr">{M(d["sym"] + " = " + d["val"])}</span>'
    return (f'<div class="drow d{k}{st}">{hd}{sym}'
            f'<span class="dheb">{TX(d["heb"])}</span></div>')


def _solitems(items, start=1):
    out, n = [], start
    for it in items:
        if it.startswith('@'):
            i = int(it[1:]); out.append(_drow(_DATA[0][i], i, n, i == 0)); n += 1; continue
        if it.startswith('#fx:'):
            out.append(_chip(set(it[4:].split(',')), n)); n += 1; continue
        if it.startswith('?'):
            lab, _, txt = it[1:].partition('|')
            out.append(f'<div class="st xbq" data-n="{max(n - 1, 1) * 10}">{XB(lab, txt.split(" || "))}</div>'); continue
        if it.startswith('=!'):
            out.append(_seq(it[2:], n, 'eq fit'))
        elif it.startswith('=') and is_formula(it[1:]):
            out.append(ST(n, EQ(it[1:], key=True), cls='fxs'))
        elif it.startswith('='):
            out.append(_seq(it[1:], n, 'eq'))
        else:
            h, c = _atoms(it, lambda k, n=n: (n + k) * 10)
            out.append(f'<p class="sp">{h}</p>'); n += c; continue
        n += seg_count(it)
    return ''.join(out), n


def _prep(sol):
    """Insert a formula chip, on its own click, before each calculation that applies a formula not yet shown.
    Returns the new list and, for each old item, its new index."""
    out, idx, seen = [], [], set()
    for it in sol:
        if it.startswith('='):
            body = it[2:] if it.startswith('=!') else it[1:]
            if is_formula(body):
                seen |= families(body)
            else:
                p = _split_eq(body)
                if len(p) > 1 and p[0][1] and is_formula(p[0][1] + ' = ' + p[1][1]):
                    seen |= families(p[0][1] + ' = ' + p[1][1])
                need = families(body) - seen
                if need:
                    out.append('#fx:' + ','.join(k for k in FORMULA if k in need)); seen |= need
        idx.append(len(out)); out.append(it)
    return out, idx


def _mark(stem, data, base, static=False):
    """Mark each given figure in the question text: on its own click (first slide) or already marked (continuation)."""
    paras = list(stem)
    for i, d in enumerate(data):
        want = d['hl'] or d['val']
        if want is False: continue
        rx = re.compile((r'(?<![\d.,])' + re.escape(want) + r'(?![\d%]|[.,]\d)') if re.match(r'[\d−-]', want) else re.escape(want))
        done = False
        for pi, p in enumerate(paras):
            segs = re.split(r'(<[^>]+>|\$[^$]*\$)', p)
            inmark = 0
            for si, sg in enumerate(segs):
                if sg.startswith('<'):
                    if 'class="dvw' in sg: inmark = 1
                    elif sg == '</span>' and inmark: inmark = 0
                    continue
                if inmark or sg.startswith('$'): continue
                m = rx.search(sg)
                if m:
                    cls = 'dvm on' if static else 'dvm st'
                    dn = '' if static else f' data-n="{(base + i) * 10}"'
                    segs[si] = sg[:m.start()] + f'<span class="dvw d{i % 8 + 1}">{m.group(0)}<i class="{cls}"{dn}></i></span>' + sg[m.end():]
                    paras[pi] = ''.join(segs); done = True; break
            if done: break
        if not done and not static:
            print('data mark not found:', d['val'], want, file=_sys.stderr)
    return paras


def Q(sid, tag, title, stem, sol, ans, note=None, tl=None, split=None, wide=False, kick=None, stemfs='', data=None, fat=None):
    """A worked question, lesson 3 on: data rows first, then the steps (see the block comment above)."""
    note = note or []
    data = data or []
    k = kick or f'חלק {CUR[0]} · {tag}'
    head = title_s = f'{tag}: {title}'
    real = [i for i, it in enumerate(sol) if not it.startswith('?')]   # step numbers in moves and fat skip the explanation buttons
    sol, idx = _prep(list(sol))
    sol = [f'@{i}' for i in range(len(data))] + sol
    idx = [x + len(data) for x in idx]
    rid = lambda k: idx[real[k - 1]]
    if isinstance(tl, TLS) and tl.kw.get('moves'):
        mv = [dict(m, s=rid(m['s']) + 1) if m.get('s') else dict(m) for m in tl.kw['moves']]
        tl = tl.redo(moves=mv)
    cuts = SPLITS.get(sid, []) if MODE == 'deck' else []
    sol, bounds, tls = _sync(sid, sol, tl, cuts, wide)
    if 'SOLS' in globals(): SOLS[sid] = sol
    _DATA[0] = data
    fs = {}
    for i, d in enumerate(data):
        for a in d['at']: fs.setdefault(a, i + 1)
    if MODE == 'pdf':
        stem_html = ''.join(f'<p>{TX(x)}</p>' for x in _mark(stem, data, 1, True))
        s1, n = _solitems(sol)
        b = (f'<div class="qstem">{stem_html}</div>' if stem else '') + (f'<div class="tlw">{tls[0]}</div>' if tl else '') + f'<div class="sol">{s1}</div><div class="band ans"><b>תשובה:</b> {TX(ans)}</div>' + ''.join(BAND(a, t) for a, t in note)
        S(sid, title_s, head, b, kind='q'); _DATA[0] = []
        return
    last = len(bounds) - 2
    nd = len(data)
    for j in range(last + 1):
        lo = bounds[j]
        drows = ''
        if j == 0 and nd:          # the data rows are rendered apart, to sit between the question and the timeline
            drows, _ = _solitems(sol[:nd]); lo = nd
        part, n = _solitems(sol[lo:bounds[j + 1]], nd + 1 if j == 0 and nd else 1)
        end = (ST(n, f'<b>תשובה:</b> {TX(ans)}', cls='band ans') + ''.join(BAND(a, t, n + 1 + i) for i, (a, t) in enumerate(note))) if j == last else ''
        t = tls[j]
        if isinstance(t, TLS) and (fs or fat):
            fs2, drop = (dict(fs) if j == 0 else {}), []
            for tk, it in (fat or {}).items():      # a flow that appears with a solution step: on that step's slide, at that click
                pos = rid(it)
                if bounds[j] <= pos < bounds[j + 1]: fs2[str(tk)] = sum(seg_count(x) for x in sol[bounds[j]:pos + 1])
                elif pos >= bounds[j + 1]: drop.append(str(tk))
            kw = {}
            if fs2: kw['fsteps'] = fs2
            if drop: kw['flows'] = {a: b for a, b in t.kw['flows'].items() if str(a) not in drop}
            if kw: t = t.redo(**kw)
        hint = '<div class="qhint nostep">' + TX('לחצו כדי לחשוף את הפתרון, שלב אחר שלב' if j == 0 else 'לחצו כדי להמשיך בפתרון') + '</div>'
        st_html = ''.join(f'<p>{TX(x)}</p>' for x in _mark(stem, data, 1, static=bool(j)))
        qs = (f'<div class="card qstem nostep {stemfs}">{st_html}</div>' if j == 0 else f'<div class="card qstem nostep sm cont"><b class="qcont">{TX("השאלה, להמשך הפתרון:")}</b>{st_html}</div>') if stem else ''
        tw = f'<div class="card tlw nostep{" cont" if j else ""}">{t}</div>' if t else ''
        top = tw + qs + drows if wide else qs + drows + tw
        if j:              # a continuation slide repeats the data, the results and the formulas it uses, so nothing is looked up a slide back
            res, fx = _carry(sol, bounds[j], bounds[j + 1])
            if data or res:
                top += ('<div class="dcont nostep">' + ''.join(_drow(d, i, 0, i == 0, True) for i, d in enumerate(data) if not (res and d['val'] == '?'))
                        + ''.join(f'<div class="drow dres"><span class="dsym" dir="ltr">{M(x)}</span></div>' for x in res) + '</div>')
            if fx: top += f'<div class="fxchip nostep"><b>{TX("הנוסחה:")}</b> <span class="fxc" dir="ltr">' + '<span class="fxsep">·</span>'.join(f'<span class="fxone">{M(FORMULA[k])}</span>' for k in FORMULA if k in fx) + '</span></div>'
        body = f'<div class="solw qflow{" wide" if wide else ""}">{top}{hint}{part}{end}</div>'
        suf = '' if j == 0 else ' (המשך)'
        S(sid + ('' if j == 0 else 'bcdefg'[j - 1]), title_s + suf, head + suf, body, kick=k, cls='qslide')
    _DATA[0] = []


def PQ(pid, title, stem, opts, a, why, sol, ans, note, tl=None, split=None, wide=False, data=None, fat=None):
    PNUM[0] += 1
    tag = f'תרגול {PNUM[0]}'
    S('s-' + pid, f'{tag}: {title}', f'{tag}: {title}', f'<div class="mcwide">{mc("m" + pid, " ".join(stem), opts, a, why)}</div>', kick=f'חלק {CUR[0]} · שאלת תרגול')
    Q(pid, f'פתרון {tag}', title, list(stem) + ['<span class="qopts">' + ' · '.join(f'{"אבגדה"[i]}. {o}' for i, o in enumerate(opts)) + '</span>'], sol, ans, note, tl=tl, wide=wide, kick=f'חלק {CUR[0]} · פתרון מלא', stemfs='sm', data=data, fat=fat)


def MCS(sid, title, h, items, tls=None):
    """Check questions, one per slide, as in core; the solution appears sentence by sentence and calculation by calculation."""
    tls = tls or {}
    for i, x in enumerate(items):
        why = getattr(x, 'why', '')
        fams = set()
        for m in re.findall(r'\$([^$]*)\$', why): fams |= families(m)
        steps, k = '', 1
        if i in tls:
            steps += ST(k, tls[i], cls='card tlw'); k += 1
        if fams:
            steps += _chip(fams, k); k += 1
        h2, c = _atoms(why, lambda j, k=k: (k + j) * 10)
        steps += f'<p class="sp">{h2}</p>'; k += c
        if getattr(x, 'ans', ''):
            steps += ST(k, '<b>תשובה:</b> ' + TX(x.ans), cls='band ans')
        body = f'<div class="mcone"><div class="mcq">{x}</div><div class="mcsol"><div class="qhint">' + TX('ענו קודם, ואז לחצו לפתרון שלב אחר שלב') + f'</div>{steps}</div></div>'
        S(sid + ('' if i == 0 else 'bcdefgh'[i - 1]), title + ('' if i == 0 else f' ({i + 1})'), h, body, kick=f'חלק {CUR[0]} · בדיקת הבנה')


def FLOW(q, branches, n0=1):
    """As in anim.py, and each branch opens in stages: its title and meaning, then its formula, then its example."""
    html = f'<div class="fc"><div class="fcq st" data-n="{n0 * 10}">{TX(q)}</div><div class="fcr n{len(branches)}">'
    for i, (t, w, f, ex) in enumerate(branches):
        st = SUB(n0 + i + 1)
        html += (f'<div class="fcb st" data-n="{st(0)}"><i class="fca"></i><div class="fcbox"><b>{TX(t)}</b><span>{TX(w)}</span>'
                 f'<div class="eq st" dir="ltr" data-n="{st(1)}">{M(f)}</div><div class="fcex st" data-n="{st(2)}">{_atoms(ex, lambda j: st(2 + j))[0]}</div></div></div>')
    return html + '</div></div>'


def PROC(steps, n0=1):
    """A process flowchart, right to left: one box per step, each on its own click, its example a click later.
    steps: [(title, what to do, example)]."""
    html = '<div class="proc">'
    for i, (t, w, ex) in enumerate(steps):
        st = SUB(n0 + i)
        if i: html += f'<i class="par st" data-n="{st(0)}"></i>'
        html += (f'<div class="pbx st" data-n="{st(0)}"><b class="pn">{i + 1}</b><b class="pt">{TX(t)}</b><span class="ptx">{TX(w)}</span>'
                 f'<div class="pex st" data-n="{st(1)}">{_atoms(ex, lambda j: st(1 + j))[0]}</div></div>')
    return html + '</div>'


for _i, _x in enumerate(SYM):          # lesson 3 wording of the legend
    if _x[0] == 'r': SYM[_i] = ('r', 'r', 'מחיר ההון, הריבית לתקופה')
SYM.insert(0, ('CF_{0}', 'CF<sub>0</sub>', 'התזרים בזמן 0'))


def _time_of(lhs):
    """A time under a result only for a value that sits at a time: CF, PMT, PV, FV."""
    if not re.match(r'\s*(Δ?CF|PMT|PV|FV)(?![A-Za-z])', lhs): return ''
    m = re.findall(r'_\{([^}]*)\}', lhs)
    if not m: return ''
    t = m[-1].split(',')[-1].strip()
    if re.fullmatch(r'-?\d+', t):
        return 'בזמן מינוס ' + t[1:] if t.startswith('-') else 'בזמן ' + t
    return ''


def TABLE(head, rows, cls='', rev=0):
    """As in core, but with rev every row waits for its click (row i on step rev + i), the first one included."""
    h = ''.join(f'<th>{TX(x)}</th>' for x in head)
    b = ''.join((f'<tr class="st" data-n="{(rev + i) * 10}">' if rev else '<tr>') + ''.join(f'<td>{TX(c)}</td>' for c in r) + '</tr>' for i, r in enumerate(rows))
    return f'<table class="tbl2 {cls}"><tr>{h}</tr>{b}</table>'


def _carry(sol, lo, hi):
    """What a continuation slide needs from the slides before it: the results it uses ('PV_{0} = 12,434.26')
    and the formulas of its calculations that were shown earlier."""
    got, seen, prev = {}, set(), ''
    for it in sol[:lo]:
        if it.startswith('#fx:'): seen |= set(it[4:].split(','))
        if not it.startswith('='): continue
        body = it[2:] if it.startswith('=!') else it[1:]
        if is_formula(body): seen |= families(body); continue
        ps = _split_eq(NOTE_RE.sub('', body))
        lhs = ps[0][1] or prev
        if ps[0][1]: prev = ps[0][1]
        last = ps[-1][1].strip()
        if (len(ps) > 1 and re.fullmatch(r'−?-?[\d,]+(\.\d+)?%?', last) and len(re.sub(r'\D', '', last)) > 1
                and re.match(r'[A-Za-zΔ]', lhs or '') and 'X' not in lhs):      # a named value, not an equation set to 0
            got[last.lstrip('-−')] = (lhs, last)
    res, fx, here = [], set(), set()
    for it in sol[lo:hi]:
        if it.startswith('#fx:'): here |= set(it[4:].split(','))
        if not it.startswith('='): continue
        body = NOTE_RE.sub('', it[2:] if it.startswith('=!') else it[1:])
        if is_formula(body): here |= families(body); continue
        fx |= families(body)
        for num in re.findall(r'(?<![\d.,])\d+(?:,\d{3})*(?:\.\d+)?%?', body):
            if num in got and got[num] not in res: res.append(got[num])
    return [f'{a} = {b}' for a, b in res][:4], (fx & seen) - here


def _chip(fams, n):
    order = [k for k in FORMULA if k in fams]
    eqs = '<span class="fxsep">·</span>'.join(f'<span class="fxone">{M(FORMULA[k])}</span>' for k in order)
    return ST(n, f'<b>{TX("הנוסחה:")}</b> <span class="fxc" dir="ltr">{eqs}</span>', cls='fxchip') if order else ''
