# Shared slide helpers for every lesson. Executed by each lesson's first content file, after it sets SPLITS_FILE and CONN.
from lib import *
import re

COURSE = 'מימון למנהלות ומנהלים'
import json
SPLITS = json.loads(R(SPLITS_FILE))   # question id -> step indices where a new slide starts (autofit.py)
SL = []            # every slide, in order
CUR = [None]       # current part number


def S(sid, title, h, body, kick=None, cls='', kind='slide'):
    SL.append(dict(id=sid, title=title, h=h, body=link_terms(body), kick=kick, cls=cls, kind=kind, part=CUR[0]))


def ST(n, html, tag='div', cls=''):
    return f'<{tag} class="st {cls}" data-n="{n * 10}">{html}</{tag}>'


def DEF(name, text, demo, n=0, trm=None):
    """One definition with its small numeric demonstration."""
    hd = f'[[{trm}|{name}]]' if trm else name
    inner = f'<b class="dn">{TX(hd)}</b><p>{TX(text)}</p><div class="demo"><b>דוגמה:</b> {TX(demo)}</div>'
    return ST(n, inner, cls='card def') if n else f'<div class="card def">{inner}</div>'


def BAND(kind, text, n=0):
    lab = {'dg': 'דגש', 'trap': 'המלכודת', 'note': 'הערה', 'dg2': 'שני דגשים', 'warn': 'חשוב'}.get(kind, '')
    inner = (f'<b>{lab}:</b> ' if lab else '') + TX(text)
    return ST(n, inner, cls='band ' + kind) if n else f'<div class="band {kind}">{inner}</div>'


def TABLE(head, rows, cls='', rev=0):
    """rev: reveal the rows one by one, starting at step rev (the first row stays visible)."""
    h = ''.join(f'<th>{TX(x)}</th>' for x in head)
    b = ''.join((f'<tr class="st" data-n="{(rev + i - 1) * 10}">' if rev and i else '<tr>') + ''.join(f'<td>{TX(c)}</td>' for c in r) + '</tr>' for i, r in enumerate(rows))
    return f'<table class="tbl2 {cls}"><tr>{h}</tr>{b}</table>'


def mc(qid, q, opts, a, why):
    o = ''
    for i, t in enumerate(opts):
        mark = ' correct' if MODE == 'pdf' and i == a else ''
        o += f'<button class="o{mark}" data-i="{i}">{"אבגדה"[i]}. {TX(t)}</button>'
    return f'<div class="mc" data-a="{a}" id="{qid}"><div class="q">{TX(q)}</div>{o}<div class="w"><b>הסבר:</b> {TX(why)}</div></div>'


def MCS(sid, title, h, items):
    """A slide of multiple choice checks, side by side."""
    shown = items[:1] + [ST(i, x) for i, x in enumerate(items[1:], 1)]   # one question at a time
    S(sid, title, h, f'<div class="mcrow n{len(items)}">' + ''.join(shown) + '</div>', kick=f'חלק {CUR[0]} · בדיקת הבנה')


def opener(n, title, q, learn, mins, note=''):
    CUR[0] = n
    SL.append(dict(id=f'p-{n}', title=f'פתיחת חלק {n}: {title}', h=title, kind='opener', part=n, q=q, learn=learn, mins=mins, note=note, cls='', kick=None, body=''))


def calc(*args, **kw):
    """Calculators were removed at the lecturer's request (2026-11-04): the course solves everything by the formulas."""
    return

def _solitems(items, start=1):
    out, n = [], start
    for it in items:
        if it.startswith('=!'):
            out.append(ST(n, M(it[2:]), cls='eq fit').replace('class="st eq fit"', 'class="st eq fit" dir="ltr"'))
        elif it.startswith('=') and is_formula(it[1:]):
            out.append(ST(n, EQ(it[1:], key=True), cls='fxs'))
        elif it.startswith('='):
            out.append(ST(n, M(it[1:]), cls='eq').replace('class="st eq"', 'class="st eq" dir="ltr"'))
        else:
            out.append(ST(n, TX(it), 'p', 'sp'))
        n += 1
    return ''.join(out), n


TIME = re.compile(r'(?:זמנים|בזמנים) (\d+) עד (\d+)|זמן (מינוס )?(\d+)|בזמנים ((?:\d+, )*\d+ ו-\d+)')


def _times(text):
    """Times named in a step's sentence: 'בזמן 9', 'לזמן מינוס 1', 'בזמנים 1 עד 24', 'בזמנים 2, 5 ו-8'."""
    t = re.sub(r'<[^>]+>|\$[^$]*\$', ' ', text)
    out = []
    for m in TIME.finditer(t):
        if m.group(1): out += [m.group(1), m.group(2)]
        elif m.group(4): out.append(('-' if m.group(3) else '') + m.group(4))
        elif m.group(5): out += re.findall(r'\d+', m.group(5))
    return list(dict.fromkeys(out))


def _sync(sid, sol, tl, cuts):
    """Insert the linking sentences, then render one timeline per slide of the question: each step marks
    its own times with a ring, each move appears on the step that explains it, and a continuation slide
    starts with the earlier moves already drawn."""
    sol2, at = [], {}
    for i, it in enumerate(sol):
        if (sid, i) in CONN: sol2.append(CONN[(sid, i)])
        at[i] = len(sol2); sol2.append(it)
    bounds = [0] + list(cuts) + [len(sol2)]
    if not isinstance(tl, TLS):
        return sol2, bounds, [tl] + [None] * len(cuts)
    ticks = [str(x) for x in tl.args[0]]
    step = lambda old: at[old - 1] + 1 if old and old - 1 in at else old
    moves = [dict(m, s=step(m.get('s', 0))) for m in tl.kw.get('moves') or []]
    rings = []
    for k, it in enumerate(sol2):
        if it.startswith('='): continue
        named = [x for x in _times(it) if x in ticks][:4]
        rings += [dict(a=x, s=k + 1) for x in named]
        for m in moves:                       # a move without a step appears where its destination is first named
            if not m['s'] and str(m['b']) in named: m['s'] = k + 1
    out = []
    for j in range(len(bounds) - 1):
        lo, hi = bounds[j], bounds[j + 1]
        mv = [dict(m, s=0 if m['s'] <= lo and j else (m['s'] - lo if m['s'] else 0)) for m in moves if m['s'] <= hi]
        if j == 0: mv = [dict(m, s=m['s']) for m in moves if m['s'] <= hi]
        rg = [dict(r, s=r['s'] - lo) for r in rings if lo < r['s'] <= hi]
        if j == 0:
            out.append(tl.redo(moves=mv, rings=rg))
        elif rg or any(m['s'] for m in mv):     # a continuation slide repeats the timeline only when it marks something new on it
            out.append(tl.redo(moves=mv, rings=rg, W=1120, fs=16, fh=24))
        else:
            out.append(None)
    return sol2, bounds, out


def Q(sid, tag, title, stem, sol, ans, note=None, tl=None, split=None, wide=False, kick=None, stemfs=''):
    """A worked question. sol: prose, or '=' + math for a display equation. note: list of (kind, text).
    Where the solution breaks into further slides comes from splits.json (written by autofit.py)."""
    note = note or []
    k = kick or f'חלק {CUR[0]} · {tag}'
    stem_html = ''.join(f'<p>{TX(x)}</p>' for x in stem)
    head = f'{tag}: {title}'
    title_s = f'{tag}: {title}'
    cuts = SPLITS.get(sid, []) if MODE == 'deck' else []
    sol, bounds, tls = _sync(sid, sol, tl, cuts)
    if MODE == 'pdf':
        s1, n = _solitems(sol)
        b = (f'<div class="qstem">{stem_html}</div>' if stem else '') + (f'<div class="tlw">{tls[0]}</div>' if tl else '') + f'<div class="sol">{s1}</div><div class="band ans"><b>תשובה:</b> {TX(ans)}</div>' + ''.join(BAND(a, t) for a, t in note)
        S(sid, title_s, head, b, kind='q')
        return
    last = len(bounds) - 2
    for j in range(last + 1):
        part, n = _solitems(sol[bounds[j]:bounds[j + 1]])
        end = (ST(n, f'<b>תשובה:</b> {TX(ans)}', cls='band ans') + ''.join(BAND(a, t, n + 1 + i) for i, (a, t) in enumerate(note))) if j == last else ''
        t = tls[j]
        if j == 0 and wide:
            body = (f'<div class="card qstem wide {stemfs}">{stem_html}</div>' if stem else '') + (f'<div class="card tlw">{t}</div>' if t else '') + f'<div class="solw">{part}{end}</div>'
        elif j == 0:
            body = (f'<div class="qg"><div class="qr">' + (f'<div class="card qstem {stemfs}">{stem_html}</div>' if stem else '') + (f'<div class="card tlw">{t}</div>' if t else '') + '</div>'
                    f'<div class="solw">{part}{end}</div></div>')
        else:
            body = (f'<div class="card tlw cont">{t}</div>' if t else '') + f'<div class="solw two">{part}{end}</div>'
        suf = '' if j == 0 else ' (המשך)'
        S(sid + ('' if j == 0 else 'bcdefg'[j - 1]), title_s + suf, head + suf, body, kick=k, cls='qslide')


PNUM = [0]


def PQ(pid, title, stem, opts, a, why, sol, ans, note, tl=None, split=None, wide=False):
    """Practice question: a multiple choice slide, then its full solution."""
    PNUM[0] += 1
    tag = f'תרגול {PNUM[0]}'
    S('s-' + pid, f'{tag}: {title}', f'{tag}: {title}', f'<div class="mcwide">{mc("m" + pid, " ".join(stem), opts, a, why)}</div>', kick=f'חלק {CUR[0]} · שאלת תרגול')
    Q(pid, f'פתרון {tag}', title, [], sol, ans, note, tl=tl, split=split, wide=wide, kick=f'חלק {CUR[0]} · פתרון מלא')


def PQO(pid, title, stem, sol, ans, note, tl=None, split=None, wide=False):
    """Open practice question with several requirements, solved on the same slide."""
    PNUM[0] += 1
    Q(pid, f'תרגול {PNUM[0]}', title, stem, sol, ans, note, tl=tl, split=split, wide=wide, kick=f'חלק {CUR[0]} · שאלת תרגול')


def CAP(t):
    return f'<p class="cap">{TX(t)}</p>'


