# Lesson 1 deck. Run: python3 build_deck.py  ->  ../lectures/lecture-1/presentation.html
import os, re, json, sys
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
R = lambda f: open(os.path.join(H, f), encoding='utf8').read()
MODE = 'deck'
for f in ('content_a.py', 'content_b.py', 'content_c.py'):
    exec(R(f))

SEC = '2026ג'


def render(s, total):
    k = s['kind']
    if k == 'title':
        return (f'<section class="slide dark s1 on" id="s-title" data-title="פתיחה">'
                '<div class="orb" style="width:320px;height:320px;background:radial-gradient(circle at 30% 30%,#58e0cf,#0f9d90 60%,transparent 72%);left:-90px;top:-70px"></div>'
                '<div class="orb" style="width:180px;height:180px;background:radial-gradient(circle at 30% 30%,#ffd37a,#e8960c 60%,transparent 72%);left:230px;bottom:90px;animation-delay:-3s"></div>'
                '<div style="position:absolute;right:70px;top:84px;width:880px">'
                f'<div class="kick" style="color:#ffb199"><span>{COURSE} · קורס 13005 · מפגש 1</span></div>'
                '<h1><span>ערך הזמן</span> <span style="color:#7fe3d6">של הכסף</span></h1>'
                '<p class="sub" style="margin-top:20px;font-size:27px;color:#c8d4f2">' + TX('יחידה 2: ערך עתידי, ערך נוכחי, סכום יחיד וסדרות סכומים.') + '</p>'
                '<p class="sub" style="margin-top:6px;font-size:22px;color:#c8d4f2">' + TX('כל החישובים מוצגים בנוסחאות מתמטיות. איננו עובדים עם לוחות היוון.') + '</p>'
                '<div class="chipbar" style="margin-top:24px">' + ''.join(f'<span class="chip">{TX(c)}</span>' for c in ['25 שאלות פתורות', '8 שאלות תרגול', f'{NCALC} מחשבונים', '6 שאלות לבית', '12 שאלות רב ברירה']) + '</div></div>'
                f'<div style="position:absolute;right:70px;bottom:58px;font-size:22px;color:#c8d4f2"><b style="color:#fff">מנחה: ד״ר שי צבאן</b> · סמסטר {SEC}</div></section>')
    if k == 'end':
        return ('<section class="slide dark s1" id="s-end" data-title="סיום"><div style="position:relative;max-width:980px;margin-top:110px">'
                '<div class="kick" style="color:#ffb199">סוף מפגש 1</div>'
                '<h1 style="font-size:60px">במפגש הבא: <span style="color:#7fe3d6">סוגיית הריבית</span></h1>'
                '<p class="sub" style="font-size:25px;margin-top:20px;color:#c8d4f2;max-width:940px">' + TX('ריבית נקובה מול אפקטיבית, המרות בין תקופות, וריבית ריאלית מול נומינלית.') + '</p>'
                '<p class="sub" style="font-size:22px;margin-top:26px;color:#c8d4f2">שאלות ותיקונים: <span dir="ltr">Shay.tsaban@gmail.com</span></p></div></section>')
    if k == 'opener':
        n = s['part']
        home = n >= 9
        when = f'לעבודה עצמית · כ-{s["mins"]} דקות' if home else f'כ-{s["mins"]} דקות'
        note = f'<div class="pd-note">{TX(s["note"])}</div>' if s.get('note') else ''
        return (f'<section class="slide dark pd" id="{s["id"]}" data-title="{s["title"]}" style="--pc:#7fe3d6"><div class="pd-num{" w" if n >= 10 else ""}">{n}</div><div class="pd-in">'
                f'<div class="kick" style="color:#ffb199"><span>חלק <span class="n">{n}</span> מתוך <span class="n">{total}</span> · {TX(when)}</span></div><div class="pd-h">{s["h"]}</div><div class="pd-q">{TX(s["q"])}</div>{note}'
                f'<div class="pd-cols"><div class="pd-box"><b>מה נעשה בחלק הזה</b><ul>{"".join("<li>" + TX(x) + "</li>" for x in s["learn"])}</ul></div></div></div></section>')
    kick = f'<div class="kick"><span>{TX(s["kick"])}</span></div>' if s.get('kick') else ''
    return f'<section class="slide {s["cls"]}" id="{s["id"]}" data-title="{re.sub("<[^>]+>", "", s["title"])}">{kick}<h2>{TX(s["h"])}</h2>{s["body"]}</section>'


NCALC = sum(1 for s in SL if s['id'].startswith('c-'))
slides_html = '\n'.join(render(s, TOTAL_PARTS) for s in SL)

fonts = R('shell/fonts.css')
base = R('shell/base.css')
tail = R('shell/tail.html')
gj = json.dumps(G, ensure_ascii=False)
js = f'const COURSE={json.dumps(COURSE, ensure_ascii=False)};\nconst G={gj};\n' + R('deck.js') + '\n' + R('calcs.js')
title = f'{COURSE} | שיעור 1 | ערך הזמן של הכסף'
html = (f'<!doctype html>\n<html lang="he" dir="rtl">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n<title>{title}</title>\n<style>\n'
        + fonts + base + R('deck.css') + '</style>\n</head>\n<body>\n<div class="stage" id="stage">\n' + slides_html + '\n' + tail
        + '<script>\n(function(){\n' + js + '\n})();\n</script>\n</body>\n</html>\n')

for bad in ('—', '־'):
    assert bad not in html, 'forbidden character ' + bad
out = os.path.join(H, '..', 'lectures', 'lecture-1')
os.makedirs(out, exist_ok=True)
open(os.path.join(out, 'presentation.html'), 'w', encoding='utf8').write(html)

# every class used in the markup or in the scripts needs a CSS rule
css = fonts + base + R('deck.css')
used = set()
for m in re.finditer(r'class="([^"]+)"', slides_html + tail + R('deck.js') + R('calcs.js')):
    for c in m.group(1).split():
        if re.fullmatch(r'[\w-]+', c): used.add(c)
missing = sorted(c for c in used if not re.search(r'\.' + re.escape(c) + r'(?![\w-])', css))
print('slides', html.count('<section class="slide'), 'calcs', NCALC, 'bytes', len(html))
print('classes without a rule:', missing)
