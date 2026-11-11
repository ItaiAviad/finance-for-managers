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
    lab = {'dg': 'דגש', 'trap': 'המלכודת', 'note': 'הערה', 'dg2': 'שני דגשים', 'warn': 'חשוב', 'tip': 'טיפ'}.get(kind, '')
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

NOTE_RE = re.compile(r'⟦([^⟧]*)⟧')
NUM_RE = r'[−-]?[\d,]+(?:\.\d+)?%?'


def _split_eq(e):
    """Split a display equation at its top-level relation signs: [(sign, text)], the first sign empty."""
    parts, depth, cur, sign = [], 0, '', ''
    i = 0
    e = e.strip()
    if e[:1] in '=≈' and e[1:2] == ' ':        # a continuation line: it opens with its relation sign
        parts.append(('', '')); sign = e[0]; i = 2
    while i < len(e):
        c = e[i]
        if c == '{': depth += 1
        elif c == '}': depth -= 1
        if depth == 0 and c in '=≈' and e[i - 1:i] == ' ' and e[i + 1:i + 2] == ' ':
            parts.append((sign, cur.strip())); cur, sign = '', c; i += 1; continue
        cur += c; i += 1
    parts.append((sign, cur.strip()))
    return parts


def _time_of(lhs):
    m = re.findall(r'_\{([^}]*)\}', lhs)
    if not m: return ''
    t = m[-1].split(',')[-1].strip()
    if re.fullmatch(r'-?\d+', t):
        return 'בזמן מינוס ' + t[1:] if t.startswith('-') else 'בזמן ' + t
    return ''


def _auto_note(body, k, n, lhs):
    """A short note under one piece of an equation: what this piece is."""
    b = body.strip()
    if k == 0 and lhs:
        if re.fullmatch(NUM_RE, lhs.replace(' ', '')):
            return 'המשוואה'
        if re.fullmatch(r'\\f\{' + NUM_RE + r'\}\{' + NUM_RE + r'( × ' + NUM_RE + r')?\}', b):
            return 'מחלקים'
        return 'מציבים את הנתונים' if re.search(r'\d', b) else ''
    if k == n - 1 and re.fullmatch(NUM_RE, b.replace(' ', '')):
        t = _time_of(lhs)
        return 'התוצאה' + (', ' + t if t else '')
    if re.search(r'\d\.\d{5,}', b) and re.fullmatch(r'[^+]*', b):
        return 'המקדם כמספר'
    if re.fullmatch(NUM_RE + r'( [×÷] ' + NUM_RE + r')+', b):
        return 'מכפילים'
    if re.fullmatch(NUM_RE + r'( [+−-] ' + NUM_RE + r')+', b):
        return 'כל רכיב בנפרד'
    if '^' in b:
        return 'מחשבים את החזקה'
    if '\\f' in b:
        return 'מחשבים את השבר'
    return ''


def eq_pieces(e, prev=''):
    """The pieces of a display equation, each with its note: [(math, note)]. A note can be forced with ⟦...⟧ at the piece's end."""
    parts = _split_eq(e)
    if len(parts) == 1:
        t = parts[0][1]
        m = NOTE_RE.search(t)
        return [(NOTE_RE.sub('', t).strip(), m.group(1) if m else '')]
    lhs = parts[0][1]
    if lhs == '':
        segs = [(f'{sg} {t}', t) for sg, t in parts[1:]]
        lhs = prev
    else:
        segs = [(f'{lhs} {parts[1][0]} {parts[1][1]}', parts[1][1])] + [(f'{sg} {t}', t) for sg, t in parts[2:]]
    out = []
    for k, (seg, body) in enumerate(segs):
        m = NOTE_RE.search(seg)
        note = m.group(1) if m else _auto_note(NOTE_RE.sub('', body), k if parts[0][1] else k + 1, len(segs) + (0 if parts[0][1] else 1), lhs)
        out.append((NOTE_RE.sub('', seg).strip(), note))
    return out


def seg_count(it):
    """How many clicks a solution item takes: one for prose and general formulas, one per piece for a worked equation."""
    if it.startswith('=') and not it.startswith('=!') and not is_formula(it[1:]):
        return len(eq_pieces(it[1:]))
    if it.startswith('=!'):
        return len(eq_pieces(it[2:]))
    return 1


def _seq(e, n, cls='eq', prev=''):
    """A worked equation built piece by piece: each piece appears on its own click, with a short note under it."""
    html = ''
    for k, (m, note) in enumerate(eq_pieces(e, prev)):
        nt = f'<span class="nt">{TX(note)}</span>' if note else ''
        html += f'<span class="sg st" data-n="{(n + k) * 10}"><span class="sm">{M(m)}</span>{nt}</span>'
    return f'<div class="{cls} seq" dir="ltr">{html}</div>'


def _solitems(items, start=1):
    out, n, prev = [], start, ''
    for it in items:
        if it.startswith('='):
            p0 = _split_eq(it[2:] if it.startswith('=!') else it[1:])[0][1]
            if p0 and not is_formula(it[1:]): prev = p0
        if it.startswith('=!'):
            out.append(_seq(it[2:], n, 'eq fit', prev))
        elif it.startswith('=') and is_formula(it[1:]):
            out.append(ST(n, EQ(it[1:], key=True), cls='fxs'))
        elif it.startswith('='):
            out.append(_seq(it[1:], n, 'eq', prev))
        else:
            out.append(ST(n, TX(it), 'p', 'sp'))
        n += seg_count(it)
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
        cum = lambda r: sum(seg_count(x) for x in sol2[lo:lo + r]) if r > 0 else 0   # item number -> the click that completes it
        mv = [dict(m, s=cum(m['s']) if m['s'] else 0) for m in mv]
        rg = [dict(r, s=cum(r['s'])) for r in rg]
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




exec(R('anim.py'))
exec(R('memes.py'))
