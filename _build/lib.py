# Shared helpers for the deck and the summary PDF: inline math, text markup, timelines.
import re, html as _h

HEB = re.compile(r'[֐-׿]')


def _braces(s, i):
    """s[i] is '{'. Return (inner, index after the closing brace)."""
    d = 0
    for j in range(i, len(s)):
        if s[j] == '{': d += 1
        elif s[j] == '}':
            d -= 1
            if d == 0: return s[i + 1:j], j + 1
    raise ValueError('unbalanced braces: ' + s)


def _minus(s):
    s = re.sub(r'(?<=\s)-(?=\s)', '−', s)
    return re.sub(r'(^|[\s(=×+])-(?=[\d(a-zA-Z])', r'\1−', s)


def M(s):
    """Math mini language: ^{x} _{x} \\f{num}{den} \\h{Hebrew}. Returns HTML."""
    out, i, buf = [], 0, ''

    def flush():
        nonlocal buf
        if buf: out.append(_minus(buf))
        buf = ''
    while i < len(s):
        c = s[i]
        if c == '^' and s[i + 1:i + 2] == '{':
            flush(); a, i = _braces(s, i + 1); out.append(f'<sup>{M(a)}</sup>')
        elif c == '_' and s[i + 1:i + 2] == '{':
            flush(); a, i = _braces(s, i + 1); out.append(f'<sub>{M(a)}</sub>')
        elif s.startswith('\\f{', i):
            flush(); a, i = _braces(s, i + 2); b, i = _braces(s, i)
            out.append(f'<span class="frac"><span>{M(a)}</span><span>{M(b)}</span></span>')
        elif s.startswith('\\h{', i):
            flush(); a, i = _braces(s, i + 2); out.append(f'<span class="mh" dir="rtl">{a}</span>')
        else:
            buf += c; i += 1
    flush()
    return ''.join(out)


NUM = re.compile(r'(?<![\w.,/])\d[\d,]*(?:\.\d+)?%?')


def _textnum(seg):
    return NUM.sub(lambda m: f'<span class="n">{m.group(0)}</span>', seg)


def TX(s):
    """Prose markup: $math$, [[key|text]] for a glossary term, and LTR isolation of every number."""
    s = re.sub(r'\[\[(\w+)\|([^\]]+)\]\]', r'<span class="term" data-t="\1">\2</span>', s)
    parts = re.split(r'(\$[^$]+\$)', s)
    out = []
    for p in parts:
        if p.startswith('$') and p.endswith('$') and len(p) > 1:
            out.append(f'<span class="m" dir="ltr">{M(p[1:-1])}</span>')
        else:
            out.append(''.join(seg if seg.startswith('<') else _textnum(seg) for seg in re.split(r'(<[^>]+>)', p)))
    return ''.join(out)


def EQ(s, cls=''):
    return f'<div class="eq {cls}" dir="ltr">{M(s)}</div>'


AUTO = [('FVFA', 'fvfa'), ('PVFA', 'pvfa'), ('PMT', 'pmt'), ('PV', 'pv'), ('FV', 'fv')]
SKIP = {'button', 'svg', 'a', 'select', 'label', 'option', 'script', 'style'}


def link_terms(body):
    """First mention per slide of an abbreviation becomes a glossary link (never inside buttons or diagrams)."""
    seen = set(re.findall(r'class="term" data-t="(\w+)"', body))
    toks = re.split(r'(<[^>]+>)', body)
    depth, interm, out = 0, 0, []
    for t in toks:
        if t.startswith('<'):
            m = re.match(r'<(/?)(\w+)', t)
            if m:
                name = m.group(2).lower()
                if name in SKIP: depth += -1 if m.group(1) else 1
                if name == 'span':
                    if 'class="term"' in t: interm = 1
                    elif m.group(1) and interm: interm = 0
            out.append(t); continue
        if depth <= 0 and not interm and t:
            for ab, k in AUTO:
                if k in seen: continue
                rx = re.compile(r'(?<![A-Za-z])' + ab + r'(?![A-Za-z])')
                if rx.search(t):
                    t = rx.sub(f'<span class="term" data-t="{k}">{ab}</span>', t, count=1); seen.add(k)
                    # the abbreviation is now wrapped: stop scanning this segment for the shorter names
                    break
            if 'סר״ת' in t and 'srt' not in seen:
                t = t.replace('סר״ת', '<span class="term" data-t="srt">סר״ת</span>', 1); seen.add('srt')
        out.append(t)
    return ''.join(out)


# ---------------------------------------------------------------- timeline
def _sv(t, fs):
    """SVG text from the small math language: only ^{..} is supported."""
    out, i = '', 0
    t = _minus(t)
    while i < len(t):
        if t.startswith('^{', i):
            a, i = _braces(t, i + 1)
            out += f'<tspan dy="{-fs * .38:.1f}" font-size="{fs * .72:.1f}">{_h.escape(a)}</tspan><tspan dy="{fs * .38:.1f}"> </tspan>'
        else:
            out += _h.escape(t[i]); i += 1
    return out


def _txt(x, y, t, fs, W, anchor='middle', fill='#16213a', weight=500):
    plain = re.sub(r'\^\{[^}]*\}', 'x', str(t))
    w = len(plain) * fs * .56
    if anchor == 'middle':
        if x - w / 2 < 3: x, anchor = 3, 'start'
        elif x + w / 2 > W - 3: x, anchor = W - 3, 'end'
    rtl = ' direction="rtl"' if HEB.search(str(t)) else ''
    if rtl: anchor = {'start': 'end', 'end': 'start'}.get(anchor, anchor)
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{fs}" text-anchor="{anchor}" fill="{fill}" font-weight="{weight}"{rtl}>{_sv(str(t), fs)}</text>'


def _st(s):
    return f' class="st" data-n="{s * 10}"' if s else ''


def TL(ticks, flows=None, moves=None, brace=None, marks=None, W=560, fs=17, fh=46):
    """Timeline as inline SVG, time running left to right.
    ticks: labels in order ('...' draws dots). flows: {tick: label or ''}. moves: dicts a, b, t (caption), s (reveal step).
    brace: (from, to, label, step). marks: {tick: label}, a dotted line up to a bold label."""
    flows, moves, brace, marks = flows or {}, moves or [], brace or [], marks or {}
    n = len(ticks)
    left, right = 28, W - 40
    dx = (right - left) / max(n - 1, 1)
    X = {str(l): left + i * dx for i, l in enumerate(ticks)}
    y = 6
    has_lab = any(v for v in flows.values()) or marks
    by = None
    if brace:
        by = y + fs + 2
        y = by + 16
    ly = y + fs if has_lab else y
    if has_lab: y = ly + 5
    ay = y                        # arrow tips
    y0 = ay + fh                  # axis
    p = []
    p.append(f'<line x1="6" y1="{y0}" x2="{W - 12}" y2="{y0}" stroke="#1b2d55" stroke-width="2.6"/><polygon points="{W - 4},{y0} {W - 17},{y0 - 6} {W - 17},{y0 + 6}" fill="#1b2d55"/>')
    for l in ticks:
        x = X[str(l)]
        if str(l) in ('...', '···'):
            p.append(_txt(x, y0 - 14, '···', fs + 5, W, fill='#8a93aa', weight=700))
            p.append(_txt(x, y0 + fs + 6, '···', fs, W, fill='#8a93aa', weight=700))
            continue
        p.append(f'<line x1="{x:.1f}" y1="{y0 - 6}" x2="{x:.1f}" y2="{y0 + 6}" stroke="#1b2d55" stroke-width="2.2"/>')
        p.append(_txt(x, y0 + fs + 6, str(l), fs, W, weight=600))
    for k, lab in flows.items():
        x = X[str(k)]
        p.append(f'<line x1="{x:.1f}" y1="{y0}" x2="{x:.1f}" y2="{ay + 8}" stroke="#ff6a4d" stroke-width="3"/><polygon points="{x:.1f},{ay} {x - 5.5:.1f},{ay + 11} {x + 5.5:.1f},{ay + 11}" fill="#ff6a4d"/>')
        if lab: p.append(_txt(x, ly, lab, fs - 1, W, fill='#b8391f', weight=700))
    for k, lab in marks.items():
        x = X[str(k)]
        p.append(f'<line x1="{x:.1f}" y1="{y0}" x2="{x:.1f}" y2="{ly + 5}" stroke="#16213a" stroke-width="1.6" stroke-dasharray="2 4"/>')
        p.append(_txt(x, ly, lab, fs, W, weight=800))
    for b in brace:
        a, c, lab = b[0], b[1], b[2]
        s = b[3] if len(b) > 3 else 0
        xa, xc = X[str(a)], X[str(c)]
        yb = by + 2
        p.append(f'<g{_st(s)}><path d="M{xa:.1f} {yb + 10} V{yb + 2} H{xc:.1f} V{yb + 10}" fill="none" stroke="#5d6a86" stroke-width="1.8"/>{_txt((xa + xc) / 2, by - 2, lab, fs - 1, W, fill="#2a3858", weight=600)}</g>')
    ym = y0 + fs + 24
    for m in moves:
        xa, xb = X[str(m['a'])], X[str(m['b'])]
        fwd = xb >= xa
        if xa == xb:
            col = m.get('c') or '#0f9d90'
            g = (f'<line x1="{xa:.1f}" y1="{y0 + fs + 9}" x2="{xa:.1f}" y2="{ym}" stroke="#8a93aa" stroke-width="1.4" stroke-dasharray="2 4"/><circle cx="{xa:.1f}" cy="{ym}" r="5.5" fill="{col}"/>')
            if m.get('t'): g += _txt(xa, ym + fs + 5, m['t'], fs - 1, W, fill=col, weight=700)
            p.append(f'<g{_st(m.get("s", 0))}>{g}</g>')
            ym += fs + 26
            continue
        col = m.get('c') or ('#0f9d90' if fwd else '#6d4df2')
        sgn = 1 if fwd else -1
        g = (f'<line x1="{xa:.1f}" y1="{y0 + fs + 9}" x2="{xa:.1f}" y2="{ym}" stroke="#8a93aa" stroke-width="1.4" stroke-dasharray="2 4"/>'
             f'<line x1="{xb:.1f}" y1="{y0 + fs + 9}" x2="{xb:.1f}" y2="{ym}" stroke="#8a93aa" stroke-width="1.4" stroke-dasharray="2 4"/>'
             f'<circle cx="{xa:.1f}" cy="{ym}" r="4.5" fill="{col}"/>'
             f'<line x1="{xa:.1f}" y1="{ym}" x2="{xb - sgn * 9:.1f}" y2="{ym}" stroke="{col}" stroke-width="2.6" stroke-dasharray="7 5"/>'
             f'<polygon points="{xb:.1f},{ym} {xb - sgn * 11:.1f},{ym - 6} {xb - sgn * 11:.1f},{ym + 6}" fill="{col}"/>')
        if m.get('t'):
            g += _txt((xa + xb) / 2, ym + fs + 5, m['t'], fs - 1, W, fill=col, weight=700)
        p.append(f'<g{_st(m.get("s", 0))}>{g}</g>')
        ym += fs + 26
    H = ym - 8 if moves else y0 + fs + 16
    return f'<svg class="tl" dir="ltr" viewBox="0 0 {W} {H:.0f}" role="img">' + ''.join(p) + '</svg>'
