# Lesson 4 look, executed after core.py and l3_lib.py. Written after the lecturer's review of lesson 3 (2026-11-25):
# equations were too large, so a calculation ran over several slides; graphs were missing where the graph IS the solution;
# the NPV formula has to stand beside its full application. Here every calculation is an aligned grid: the general formula
# on top, the substitution under it, term under term, then the values and the result, one row per click, at a smaller size.
# Each part of a question gets its own slide, with the full question and its data repeated, so nothing runs over.
# Components borrowed from the other course decks: number tiles, tool cards, characters with speech bubbles,
# a worksheet table built row by row, and rows to classify with instant feedback.
import math
from lib import _braces

NAVY, CORAL, TEAL, GOLD, VIOLET, BLUE, GREEN, PINK = '#1b2d55', '#ff6a4d', '#0f9d90', '#e8960c', '#6d4df2', '#1f5fbf', '#2f7d32', '#b0306a'
DC = {1: '#c4421f', 2: '#0b6e65', 3: '#5a3bd6', 4: '#9a6200', 5: '#1f5fbf', 6: '#2f7d32', 7: '#b0306a', 8: '#4d5b78'}


def _n(k):
    return f'data-n="{k * 10}"'


def STK(k, html, tag='div', cls=''):
    """Like ST, but k = 0 means always visible."""
    return f'<{tag} class="st {cls}" {_n(k)}>{html}</{tag}>' if k else f'<{tag} class="{cls}">{html}</{tag}>'


# ---------------------------------------------------------------- math: square roots and the arithmetic check
def M4(s):
    """M() plus √{x}, drawn with a bar over the radicand (also inside fractions)."""
    roots = []
    while '√{' in s:
        i = s.find('√{')
        inner, j = _braces(s, i + 1)
        roots.append(M4(inner))
        s = s[:i] + f'§{len(roots) - 1}§' + s[j:]
    html = M(s)
    for n, r in enumerate(roots):
        html = html.replace(f'§{n}§', f'<span class="sq">√<span class="sqx">{r}</span></span>')
    return html


def _num_expr(e):
    """Turn a row of the math markup into a Python expression; None if it holds a symbol."""
    x = e.replace('−', '-').replace('×', '*').replace('·', '*').replace('÷', '/')
    x = re.sub(r'⟦[^⟧]*⟧', '', x)
    for _ in range(3):
        x = re.sub(r'(\d),(\d{3})', r'\1\2', x)
    x = re.sub(r'(\d+(?:\.\d+)?)%', r'(\1/100)', x)
    x = x.replace('PVFA(', 'pvfa(')
    while '\\f{' in x:
        i = x.find('\\f{')
        a, j = _braces(x, i + 2)
        b, k = _braces(x, j)
        x = x[:i] + f'(({a})/({b}))' + x[k:]
    while '√{' in x:
        i = x.find('√{')
        a, j = _braces(x, i + 1)
        x = x[:i] + f'sqrt({a})' + x[j:]
    while '^{' in x:
        i = x.find('^{')
        a, j = _braces(x, i + 1)
        x = x[:i] + f'**({a})' + x[j:]
    rest = re.sub(r'pvfa|sqrt', '', x)
    if re.search(r'[A-Za-z֐-׿_{}\\]', rest):
        return None
    return x


def _ev(e):
    x = _num_expr(e)
    if x is None:
        return None
    try:
        return eval(x, {'pvfa': lambda r, t: (1 - (1 + r) ** -t) / r, 'sqrt': math.sqrt})
    except Exception:
        return None


CHECKED = [0]


def _check(rows, where):
    """Rows that continue one left side ('= ...' rows, or rows with the same left side) must agree when they are all numbers:
    every one of them equals the last of its group."""
    groups, lhs = {}, None
    for r in rows:
        r = NOTE_RE.sub('', r).strip()
        if r.startswith('= '):
            rhs = r[2:]
        elif ' = ' in r:
            lhs, rhs = r.split(' = ', 1)
        else:
            continue
        v = _ev(rhs)
        if v is not None and lhs is not None:
            groups.setdefault(lhs.strip(), []).append((r, v))
    for g, vals in groups.items():
        last = vals[-1][1]
        for r, v in vals[:-1]:
            tol = max(0.021, abs(last) * 3e-6)
            CHECKED[0] += 1
            assert abs(v - last) <= tol, f'{where}: "{r}" gives {v:.6f}, the last row of {g} gives {last:.6f}'


# ---------------------------------------------------------------- the equation grid
def _toks(e):
    """Split a row at its top-level ' = ', ' + ', ' - ' into cells."""
    out, cur, d = [], '', 0
    i = 0
    while i < len(e):
        c = e[i]
        if c in '{(':
            d += 1
        elif c in '})':
            d -= 1
        if d == 0 and e[i:i + 3] in (' = ', ' + ', ' - ', ' − '):
            out.append(cur.strip()); out.append(e[i + 1]); cur = ''; i += 3; continue
        cur += c; i += 1
    out.append(cur.strip())
    return out


AUTO4 = ['הנוסחה', 'מציבים את הנתונים', 'מחשבים כל רכיב', 'התוצאה']


def EQG(rows, k0=1, notes=None, where='', each=True, fx_first=True):
    """rows: math rows; a row that starts with '= ' continues the previous left side. One row per click from k0
    (each=False: all rows on k0). A note per row: '⟦note⟧' at the end of the row, else an automatic one.
    Returns (html, clicks used)."""
    _check(rows, where)
    parsed = []
    for r in rows:
        m = NOTE_RE.search(r)
        note = m.group(1) if m else None
        r = NOTE_RE.sub('', r).strip()
        if r.startswith('= '):
            cells = [''] + _toks(r[2:].strip())
            cells = [''] + ['='] + cells[1:]
        elif ' = ' in r:
            lhs, rhs = r.split(' = ', 1)
            cells = [lhs.strip(), '='] + _toks(rhs.strip())
        else:
            cells = [r]
        parsed.append((cells, note))
    ncol = max(len(c) for c, _ in parsed)
    html = '<table class="eqg"><tbody>'
    for i, (cells, note) in enumerate(parsed):
        sym = _num_expr(' '.join(cells[2:]) if len(cells) > 2 else cells[0]) is None and not re.search(r'[<>≤≥]', ' '.join(cells))
        if not note:
            if i == 0 and sym and fx_first:
                note = AUTO4[0]
            elif i == len(parsed) - 1:
                note = AUTO4[3]
            elif re.search(r'%|\^\{|\\f\{|√', ' '.join(cells[2:])):
                note = AUTO4[1]
            else:
                note = AUTO4[2]
        tds = ''
        for j, c in enumerate(cells):
            span = f' colspan="{ncol - j}"' if j == len(cells) - 1 and len(cells) < ncol else ''
            if c in ('=', '+', '-', '−'):
                tds += f'<td class="op"{span}>{"−" if c in "-−" else c}</td>'
            elif j == 0:
                tds += f'<td class="lhs"{span}>{M4(c)}</td>'
            else:
                tds += f'<td{span}>{M4(c)}</td>'
        cls = 'f' if (i == 0 and sym and fx_first) else ''
        k = (k0 + i) if each else k0
        attr = f' class="st {cls}" {_n(k)}' if k else (f' class="{cls}"' if cls else '')
        html += f'<tr{attr}>{tds}<td class="nt">{TX(note)}</td></tr>'
    html += '</tbody></table>'
    return html, (len(rows) if each else 1)


# ---------------------------------------------------------------- tiles, marks
def TILE(c, sym, val, heb, k=0, big=False):
    s = f'<span class="ts">{M4(sym)}</span>' if sym else ''
    num = re.fullmatch(r'[−\-]?[\d.,]+%?', str(val).strip())
    v = (f'<span class="tv">{M(val) if num else TX(val)}</span>') if val != '' else ''
    return STK(k, s + v + f'<span class="th">{TX(heb)}</span>', cls=f'tile d{c}' + (' big' if big else ''))


def _marks(stem, steps):
    """{{c|text}} in a question: a colour mark that lights up on step steps[c] (None: always on)."""
    def rep(m):
        c, t = int(m.group(1)), m.group(2)
        k = (steps or {}).get(c)
        mk = f'<span class="dvm st" {_n(k)}></span>' if k else '<span class="dvm"></span>'
        return f'<span class="dvw d{c}">{mk}<span class="dv">{TX(t)}</span></span>'
    return re.sub(r'\{\{(\d)\|([^}]*)\}\}', rep, stem)


def _stem_html(stem, steps):
    paras = stem if isinstance(stem, (list, tuple)) else [stem]
    out = ''
    for p in paras:
        out += '<p>' + ''.join(seg if seg.startswith('<') else TX(seg) for seg in re.split(r'(<[^>]+>)', _marks(p, steps))) + '</p>'
    return out


# ---------------------------------------------------------------- graphs
def GF(xmax, ymin, ymax, xt, yt, series=(), marks=(), zones=(), W=690, H=270, ylab='NPV', xlab='r', yfmt=None, keyrow=None):
    """A graph for a solution step: series, marks and zones carry 'n' counted from 0 inside the step.
    Returns a function k -> (html, clicks used)."""
    def f(k):
        def sh(d):
            d = dict(d); d['n'] = (k + d.get('n', 0)) if k else 0; return d
        ss, ms, zs = [sh(s) for s in series], [sh(m) for m in marks], [sh(z) for z in zones]
        used = 1 + max([d.get('n', 0) for d in list(series) + list(marks) + list(zones)] or [0])
        html = CURVE(ss, xmax, ymin, ymax, xt, yt, ms, zs, W=W, H=H, ylab=ylab, xlab=xlab, yfmt=yfmt)
        if keyrow:
            html += KEY(keyrow)
        return html, used
    return f


def SCHEM(kind, k=0, W=320, H=200, lab=None, pts=()):
    """A schematic NPV curve, drawn for its shape and not to scale: 'down' (investment), 'up' (loan),
    'u_above', 'n_below' (no IRR), 'hill' (two IRRs), 'valley'. pts: [(x 0..1, label)] marked on the r axis."""
    L, Rr, T, B = 34, W - 22, 26, H - 30
    y0 = {'u_above': B - 22, 'n_below': T + 26}.get(kind, (T + B) / 2)

    def yv(t):
        return {'down': y0 - 80 + 200 * t - 90 * t * t, 'up': y0 + 80 - 200 * t + 90 * t * t,
                'u_above': y0 - 26 - 300 * (t - .5) ** 2, 'n_below': y0 + 26 + 300 * (t - .5) ** 2,
                'hill': y0 + 44 - 270 * t * (1 - t), 'valley': y0 - 44 + 270 * t * (1 - t)}[kind]
    xs = [L + (Rr - L) * i / 60 for i in range(61)]
    pts_ = ' '.join(f'{x:.1f},{yv((x - L) / (Rr - L)):.1f}' for x in xs)
    c = {'down': CORAL, 'up': BLUE, 'u_above': TEAL, 'n_below': '#c4421f', 'hill': VIOLET, 'valley': GOLD}[kind]
    o = (f'<svg class="sch" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">'
         f'<line x1="{L}" y1="{y0:.1f}" x2="{Rr + 8}" y2="{y0:.1f}" stroke="{NAVY}" stroke-width="2.4"/>'
         f'<polygon points="{Rr + 16},{y0:.1f} {Rr + 5},{y0 - 5:.1f} {Rr + 5},{y0 + 5:.1f}" fill="{NAVY}"/>'
         f'<text x="{Rr + 10}" y="{y0 - 9:.1f}" font-size="17" font-weight="800" fill="{NAVY}" text-anchor="end">r</text>'
         f'<line x1="{L}" y1="{B}" x2="{L}" y2="{T - 8}" stroke="{NAVY}" stroke-width="2.4"/>'
         f'<polygon points="{L},{T - 16} {L - 5},{T - 5} {L + 5},{T - 5}" fill="{NAVY}"/>'
         f'<text x="{L + 8}" y="{T - 6}" font-size="17" font-weight="800" fill="{NAVY}">NPV</text>'
         f'<polyline points="{pts_}" fill="none" stroke="{c}" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"/>')
    for x, t in pts:
        X = L + (Rr - L) * x
        o += (f'<circle cx="{X:.1f}" cy="{y0:.1f}" r="5.5" fill="#fff" stroke="{NAVY}" stroke-width="2.6"/>'
              f'<text x="{X:.1f}" y="{y0 + 24:.1f}" font-size="17" font-weight="800" fill="{NAVY}" text-anchor="middle">{t}</text>')
    o += '</svg>'
    if lab:
        o += f'<div class="schl">{TX(lab)}</div>'
    return STK(k, o, cls='schw')


# ---------------------------------------------------------------- one worked question, one slide per part
def _steps_html(steps, k, where):
    """Render solution steps from click k. Step forms:
    ('eq', caption, rows)            a calculation grid, one row per click (caption with its first row)
    ('eq1', caption, rows)           the same grid on a single click
    ('t', text)                      one sentence block
    ('g', caption, GF(...))          a graph, its own clicks
    ('h', caption, html, clicks)     any ready block (html built for click k is not possible here: give clicks=1)
    ('x', label, text)               an explanation button under the previous step (no click)
    ('b', kind, text)                a band (דגש, טיפ...)
    ('a', text)                      the answer band
    Returns (html, next k)."""
    out, num = '', 0
    for s in steps:
        t = s[0]
        if t == 'x':
            out += XB(s[1], s[2]); continue
        if t in ('eq', 'eq1'):
            num += 1
            g, used = EQG(s[2], k, where=where, each=(t == 'eq'))
            out += STK(k, f'<div class="wst"><span class="bn">{num}</span><div><div class="cap">{TX(s[1])}</div></div></div>', cls='wcap') + f'<div class="wgr">{g}</div>'
            k += used
        elif t == 't':
            out += STK(k, TX(s[1]), 'p', 'wt'); k += 1
        elif t == 'g':
            num += 1
            g, used = s[2](k)
            out += STK(k, f'<div class="wst"><span class="bn">{num}</span><div><div class="cap">{TX(s[1])}</div></div></div>', cls='wcap') + f'<div class="wgw">{g}</div>'
            k += used
        elif t == 'h':
            num += 1 if s[1] else 0
            cap = f'<div class="wst"><span class="bn">{num}</span><div><div class="cap">{TX(s[1])}</div></div></div>' if s[1] else ''
            out += STK(k, cap + s[2], cls='wh'); k += s[3] if len(s) > 3 else 1
        elif t == 'b':
            out += BAND(s[1], s[2], k); k += 1
        elif t == 'a':
            out += STK(k, '<b>תשובה:</b> ' + TX(s[1]), cls='band ans'); k += 1
    return out, k


QN = {'שאלה': 0, 'תרגול': 0}


def W(sid, tag, title, stem, data, parts, tl=None, side=None, kick='מסבירים יחד', cols=3, wide=False):
    """A worked question in the lesson 4 layout. Right column: the question, its data as tiles (on the first slide each
    tile lights its figure in the question, one per click), and an optional timeline or table. Left column: the solution of
    one part. parts: [(label, steps)]. stem marks: {{c|text}} with c the tile colour. data: [(c, sym, val, heb)].
    wide=True: the question and its tiles form a band across the top, and the solution takes the full width under it
    (for worksheets and long tables)."""
    if tag in QN:          # 'שאלה' or 'תרגול': numbered by order of appearance across all the lesson files
        QN[tag] += 1
        tag = f'{tag} {QN[tag]}'
    if wide:               # a long question with a worksheet: the question and its data get a slide of their own first
        k, stepmap, tiles = 1, {}, ''
        for c, sym, val, heb in data:
            stepmap[c] = k; tiles += TILE(c, sym, val, heb, k); k += 1
        S(sid, f'{tag}: {title}', f'{tag}: {title}',
          f'<div class="wintro"><div class="card wstem big">{_stem_html(stem, stepmap)}</div><div class="tiles c{min(len(data), 4)} big">{tiles}</div>'
          + (f'<div class="card wtl">{tl}</div>' if tl else '') + '</div>', kick=f'חלק {CUR[0]} · {kick}', cls='w4s')
        qbtn = XB('השאלה המלאה', [re.sub(r'\{\{\d\|([^}]*)\}\}', r'\1', p) for p in (stem if isinstance(stem, (list, tuple)) else [stem])])
    for pi, (lab, steps) in enumerate(parts):
        first = pi == 0 and not wide
        k, stepmap, tiles = 1, {}, ''
        for c, sym, val, heb in data:
            if first:
                stepmap[c] = k
                tiles += TILE(c, sym, val, heb, k); k += 1
            else:
                tiles += TILE(c, sym, val, heb)
        right = (f'<div class="card wstem"><b class="wqh">{TX("השאלה" if first else "השאלה, להמשך הפתרון")}</b>{_stem_html(stem, stepmap if first else None)}</div>'
                 if not wide else f'<div class="wqb">{qbtn}</div>')
        if data:
            right += f'<div class="tiles c{len(data) if (wide and not first) else cols}{" row" if (wide and not first) else ""}">{tiles}</div>'
        if tl:
            right += f'<div class="card wtl">{tl}</div>'
        if side:
            right += side
        hint = STK(0, TX('לחצו כדי לחשוף את הפתרון, שלב אחר שלב'), 'div', 'qhint') if (first or (wide and pi == 0)) else ''
        sol, k = _steps_html(steps, k, f'{sid} {lab}')
        left = f'<div class="wlab">{TX(lab)}</div>' + hint + sol
        sx = sid + ('' if first else 'bcdefghij'[pi - (0 if wide else 1)])
        S(sx, f'{tag}: {title}' + ('' if first else f' ({lab})'), f'{tag}: {title}',
          f'<div class="w4{" wide" if wide else ""}"><div class="wq">{right}</div><div class="wsol">{left}</div></div>', kick=f'חלק {CUR[0]} · {kick}', cls='w4s')


# ---------------------------------------------------------------- check questions with a graph
def MC4(sid, title, q, opts, a, sents, g=None, fx=None, kick=None, tl=None):
    """One check question: the question and options on the right; on the left, after the answer, the solution sentence by
    sentence, with the formula it rests on and, when the shape decides the answer, the graph."""
    x = mc(sid + '-mc', q, opts, a, 'הפתרון המלא משמאל, שלב אחר שלב.' if MODE == 'deck' else ' '.join(sents))
    k, steps = 1, ''
    if fx:
        steps += STK(k, '<b class="ct">' + TX('הנוסחה') + '</b>' + EQ(fx), cls='card fxs'); k += 1
    if tl:
        steps += STK(k, tl, cls='card wtl'); k += 1
    if g:
        h, used = g(k)
        steps += f'<div class="card wgw">{h}</div>'; k += used
    for s in sents:
        steps += STK(k, TX(s), 'p', 'wt'); k += 1
    steps += STK(k, '<b>תשובה:</b> ' + TX(x.ans), cls='band ans')
    body = (f'<div class="mc4"><div class="mcq">{x}</div><div class="mcsol"><div class="qhint">' + TX('ענו קודם, ואז לחצו לפתרון שלב אחר שלב') +
            f'</div>{steps}</div></div>')
    S(sid, title, title, body, kick=kick or f'חלק {CUR[0]} · בדיקת הבנה')


# ---------------------------------------------------------------- a tool card: question, formula, example, conclusion
def TOOL(sid, title, h, q, fx, eg, concl, legend=None, kick=None, egcap='דוגמה', art=None):
    """The 'tool card' from the financial analysis decks: what it answers, the formula, a worked example, the conclusion.
    eg: html for the example, or a list of EQG rows."""
    k = 1
    c1 = STK(k, f'<b class="ct">{TX("❓ השאלה")}</b><p>{TX(q)}</p>', cls='card tq'); k += 1
    c2 = STK(k, f'<b class="ct">{TX("📐 הנוסחה")}</b>' + EQ(fx, 'big') + (f'<p class="lgd">{TX(legend)}</p>' if legend else ''), cls='card tf'); k += 1
    if isinstance(eg, list):
        g, used = EQG(eg, k, where=sid)
        c3 = STK(k, f'<b class="ct">{TX("🧮 " + egcap)}</b>', cls='tecap') + g; k += used
    else:
        c3 = STK(k, f'<b class="ct">{TX("🧮 " + egcap)}</b>' + eg); k += 1
    c4 = STK(k, f'<b class="ct">{TX("💡 המסקנה")}</b><p>{TX(concl)}</p>', cls='card tc')
    artd = f'<div class="tart">{_svg(TOONS.get(art, art))}</div>' if art and MODE != 'pdf' else ''
    S(sid, title, h, f'<div class="tool">{c1.replace("</div>", artd + "</div>", 1) if artd else c1}{c2}<div class="card te">{c3}</div>{c4}</div>',
      kick=kick or f'חלק {CUR[0]} · כרטיס כלי')


# ---------------------------------------------------------------- number tiles with operators
def NUMS(items, k0=1, each=True):
    """[('NPV', '2,329.08', 'הענ״נ', c), '÷', (...), '=', (...)]: big tiles with the operators between them.
    Each tile appears with the operator before it. Returns (html, clicks)."""
    out, k, pend = '', k0, ''
    for it in items:
        if isinstance(it, str):
            pend = f'<span class="nop">{it}</span>'; continue
        sym, val, heb, c = (tuple(it) + (5,))[:4]
        inner = pend + f'<div class="ntile d{c}"><span class="ns">{M4(sym)}</span><span class="nv">{TX(val)}</span><span class="nh">{TX(heb)}</span></div>'
        out += STK(k, inner, 'div', 'ngrp'); pend = ''
        if each: k += 1
    if not each: k += 1
    return f'<div class="nums">{out}</div>', k - k0


# ---------------------------------------------------------------- characters with speech bubbles
def CHARS(items, k0=1):
    """[(toon, name, quote, role)]: one card per click. Returns (html, clicks)."""
    out = ''
    for i, (toon, name, quote, role) in enumerate(items):
        art = _svg(TOONS.get(toon, toon)) if MODE != 'pdf' else ''
        out += STK(k0 + i, f'<div class="bub">{TX(quote)}</div><div class="who"><span class="wart">{art}</span><b>{TX(name)}</b><small>{TX(role)}</small></div>', cls='chr')
    return f'<div class="chars n{len(items)}">{out}</div>', len(items)


# ---------------------------------------------------------------- the cash flow worksheet, row by row
def _acc(v):
    if v == '' or v is None:
        return ''
    if isinstance(v, str):
        return TX(v)
    t = f'{abs(v):,.0f}' if float(v).is_integer() else f'{abs(v):,.2f}'
    return f'<span class="n">({t})</span>' if v < 0 else f'<span class="n">{t}</span>'


def WS(head, rows, k0=1, how=True, cls=''):
    """head: the year labels. rows: (label, cells, how, kind); kind: '' item, 'sum' a subtotal, 'net' the net cash flow,
    'sec' a section line (cells ignored). Negative numbers print in parentheses. One row per click from k0
    (k0 = 0: all visible). Returns (html, clicks)."""
    h = f'<tr><th class="wl">{TX("פרטים / שנה")}</th>' + ''.join(f'<th>{TX(str(y))}</th>' for y in head) + (f'<th class="wshw">{TX("איך")}</th>' if how else '') + '</tr>'
    body, k = '', k0
    for lab, cells, hw, kind in rows:
        attr = f' class="st {kind}" {_n(k)}' if k else (f' class="{kind}"' if kind else '')
        if kind == 'sec':
            body += f'<tr{attr}><td class="sec" colspan="{len(head) + 1 + (1 if how else 0)}">{TX(lab)}</td></tr>'
        else:
            body += f'<tr{attr}><td class="wl">{TX(lab)}</td>' + ''.join(f'<td>{_acc(c)}</td>' for c in cells) + (f'<td class="wshw">{TX(hw)}</td>' if how else '') + '</tr>'
        if k: k += 1
    return f'<table class="ws {cls}">{h}{body}</table>', (k - k0 if k0 else 0)


# ---------------------------------------------------------------- classify rows, with feedback on the click
def CLASSIFY(items, yes='רלוונטי', no='לא רלוונטי'):
    """[(text, True/False, why)]: each row gets two buttons; a click marks it right or wrong and opens the reason."""
    rows = ''
    for t, ok, why in items:
        if MODE == 'pdf':
            rows += f'<div class="clr"><span class="clt">{TX(t)}</span><b class="cla">{TX(yes if ok else no)}</b><span class="clw">{TX(why)}</span></div>'
        else:
            rows += (f'<div class="clr" data-ok="{1 if ok else 0}"><span class="clt">{TX(t)}</span><span class="clb"><button class="cbt" data-v="1">{TX(yes)}</button>'
                     f'<button class="cbt" data-v="0">{TX(no)}</button></span><span class="clw">{TX(why)}</span></div>')
    return f'<div class="cls4">{rows}</div>'


# ---------------------------------------------------------------- 'what we learned': cards, one per click
def LEARN(sid, title, points, kick=None):
    cards = ''.join(STK(i + 1, f'<span class="ln">{i + 1}</span><div>{TX(p)}</div>', cls='lcard') for i, p in enumerate(points))
    S(sid, title, title, f'<div class="learn4 n{len(points)}">{cards}</div>', kick=kick or f'חלק {CUR[0]} · מה למדנו')


def TWO(right, left, cls=''):
    return f'<div class="two4 {cls}"><div>{right}</div><div>{left}</div></div>'


def FX4(rows, k=0, cap='הנוסחה'):
    """A highlighted general formula (or a few), no arithmetic."""
    return STK(k, f'<b class="ct">{TX(cap)}</b>' + ''.join(EQ(r) for r in rows), cls='card fxs')
