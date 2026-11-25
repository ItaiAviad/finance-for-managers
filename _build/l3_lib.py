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
                 + (f'<text x="{(X(z["x0"]) + X(z["x1"])) / 2:.1f}" y="{(Y(z["ty"]) if "ty" in z else T + 22):.1f}" text-anchor="middle" font-size="18" font-weight="800" fill="{z.get("tc", "#2a3858")}" direction="rtl">{z["t"]}</text>' if z.get('t') else '') + '</g>')
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
            lab = f'<text x="{X(lx):.1f}" y="{ly:.1f}" font-size="18" font-weight="800" fill="{s["c"]}" text-anchor="middle" direction="rtl">{s["lab"]}</text>'
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
                  f'fill="{m.get("tc", c)}" direction="rtl">{m["t"]}</text>')
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
SYM[:0] = [('NPV', 'NPV', 'ערך נוכחי נקי'), ('IRR', 'IRR', 'שיעור תשואה פנימי'), ('I_{0}', 'I<sub>0</sub>', 'ההשקעה בזמן 0'),
           ('CF_{t}', 'CF<sub>t</sub>', 'התזרים בשנה t'), ('CF_{1}', 'CF<sub>1</sub>, CF<sub>2</sub>', 'התזרים בשנה 1, בשנה 2'),
           ('CF', 'CF', 'התזרים השנתי'), ('EAC', 'EAC', 'עלות שנתית שקולה'), ('OC', 'OC', 'עלות הפעלה שנתית'), ('PI', 'PI', 'מדד הרווחיות'), ('EAV', 'EAV', 'שווה הערך השנתי')]
AUTO[:0] = [('NPV', 'npv'), ('IRR', 'irr')]
FORMULA.update({'npv': 'NPV = -I_{0} + \\f{CF_{1}}{(1 + r)^{1}} + \\f{CF_{2}}{(1 + r)^{2}} + ...',
                'npva': 'NPV = -I_{0} + CF × \\f{1 - (1 + r)^{-t}}{r}',
                'pi': 'PI = \\f{NPV}{I_{0}}', 'npvsum': 'NPV_{total} = NPV_{1} + NPV_{2} + ...', 'eac': 'EAC = \\f{I_{0}}{PVFA(r,t)} + OC', 'eav': 'EAV = \\f{NPV}{PVFA(r,t)}'})
_fam0 = families


def families(e):
    f = _fam0(e)
    if re.match(r'\s*NPV', e):
        rhs = e.split('=', 1)[1] if '=' in e else ''
        if not re.match(r'\s*-', rhs):          # no investment on the right: a sum of NPVs, NPVs moved in time, or a loan
            if re.match(r'\s*[\d,.]+(?:\s*\+\s*[\d,.]+)+\s*(=|$)', rhs) or re.match(r'\s*\d+ × [\d,.]+ \+', rhs): f.add('npvsum')
        else:
            uneven = bool(re.search(r'\\f\{[^{}]*\}\{\(?1', e)) and 'pvs' not in f
            f.add('npv' if uneven else 'npva'); f -= {'pvs', 'fv1', 'perp'}
            if uneven: f -= {'pv1', 'fvv', 'pvv'}
    if re.match(r'\s*PI\b', e): f.add('pi')
    if re.match(r'\s*EAV', e): f.add('eav'); f.discard('pvs')
    if re.match(r'\s*EAC', e): f -= {'pvs'}; f.add('eac')
    if 'IRR' in e or re.match(r'\s*X', e): f -= {'perp', 'pv1', 'fv1'}
    return f
