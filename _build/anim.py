# Animated building blocks for lesson decks: growing bar charts, a branching flowchart, and tables that fill cell by cell.
# Executed after core.py. Every animated piece is a reveal step (.st with data-n), so a click shows it and the CSS animates it.


def BARS(groups, W=1120, H=300, vmax=None, vmin=0, hline=None, title=None):
    """groups: list of dicts: lab (x label), segs [(value, color, text inside or '')], top (label above), n (reveal step, 0 = at once).
    Stacked segments grow bottom up, one after the other. hline: (value, label, step) dashed reference line."""
    vals = [sum(v for v, _, _ in g['segs']) for g in groups]
    vmax = vmax or max(vals) * 1.12
    top, base, left, right = 34 if title else 18, H - 42, 20, W - 20
    k = len(groups)
    slot = (right - left) / k
    bw = min(78, slot * 0.62)
    sy = lambda v: (base - top) * (v - vmin) / (vmax - vmin)
    out = [f'<svg class="ch" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">']
    if title:
        out.append(f'<text x="{W / 2}" y="20" text-anchor="middle" font-size="19" font-weight="800" fill="#1b2d55" direction="rtl">{title}</text>')
    out.append(f'<line x1="{left}" y1="{base}" x2="{right}" y2="{base}" stroke="#1b2d55" stroke-width="2.5"/>')
    for i, g in enumerate(groups):
        x = left + slot * i + (slot - bw) / 2
        n = g.get('n', 0)
        out.append(f'<g class="st" data-n="{n * 10}">' if n else '<g class="auto">')
        y = base
        for j, (v, col, txt) in enumerate(g['segs']):
            h = sy(v) if j == 0 else (base - top) * v / (vmax - vmin)
            d = f'{j * 0.45:.2f}s'
            out.append(f'<rect class="gb" style="--d:{d}" x="{x:.1f}" y="{y - h:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="5" fill="{col}"/>')
            if txt and h > 24:
                out.append(f'<text class="vl" style="--d:{d}" x="{x + bw / 2:.1f}" y="{y - h / 2 + 6:.1f}" text-anchor="middle" font-size="15" font-weight="700" fill="#fff">{txt}</text>')
            y -= h
        if g.get('top'):
            out.append(f'<text class="vl" style="--d:{0.45 * (len(g["segs"]) - 1):.2f}s" x="{x + bw / 2:.1f}" y="{y - 8:.1f}" text-anchor="middle" font-size="16" font-weight="800" fill="#1b2d55">{g["top"]}</text>')
        out.append('</g>')
        out.append(f'<text x="{x + bw / 2:.1f}" y="{base + 26}" text-anchor="middle" font-size="16" fill="#5d6a86">{g["lab"]}</text>')
    if hline:
        v, lab, n = hline
        y = base - sy(v)
        out.append(f'<g class="st" data-n="{n * 10}"><line class="hl" x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#ff6a4d" stroke-width="2.5" stroke-dasharray="8 6"/>'
                   f'<text x="{left + 4}" y="{y - 8:.1f}" text-anchor="end" font-size="16" font-weight="800" fill="#c4421f" direction="rtl">{lab}</text></g>')
    out.append('</svg>')
    return ''.join(out)


def KEY(items):
    """A colour key under a chart: [(colour, text)]."""
    return '<div class="ckey">' + ''.join(f'<span><i style="background:{c}"></i>{TX(t)}</span>' for c, t in items) + '</div>'


def FLOW(q, branches, n0=1):
    """A question box that splits into branches. branches: [(title, words, formula, example)]. Each branch drops in on its own click."""
    html = f'<div class="fc"><div class="fcq st" data-n="{n0 * 10}">{TX(q)}</div><div class="fcr n{len(branches)}">'
    for i, (t, w, f, ex) in enumerate(branches):
        html += (f'<div class="fcb st" data-n="{(n0 + i + 1) * 10}"><i class="fca"></i><div class="fcbox"><b>{TX(t)}</b><span>{TX(w)}</span>'
                 f'<div class="eq" dir="ltr">{M(f)}</div><div class="fcex">{TX(ex)}</div></div></div>')
    return html + '</div></div>'


def CT(head, rows, cls=''):
    """A table that fills cell by cell. A cell is text, or (text, step, how): the value appears on its step, with a short 'how' line."""
    h = ''.join(f'<th>{TX(x)}</th>' for x in head)
    body = ''
    for r in rows:
        body += '<tr>'
        for c in r:
            if isinstance(c, tuple):
                t, n, how = (c + ('',))[:3]
                body += f'<td class="st cf" data-n="{n * 10}"><b>{TX(t)}</b>' + (f'<small class="how">{TX(how)}</small>' if how else '') + '</td>'
            else:
                body += f'<td>{TX(c)}</td>'
        body += '</tr>'
    return f'<table class="tbl2 ctb {cls}"><tr>{h}</tr>{body}</table>'


def SUMUP(sid, title, points):
    """Interim summary at the end of a part: the few things to keep."""
    S(sid, title, title, '<ol class="steps sumup">' + ''.join(ST(i + 1, '<span>' + TX(p) + '</span>', 'li') for i, p in enumerate(points)) + '</ol>',
      kick=f'חלק {CUR[0]} · סיכום ביניים')
