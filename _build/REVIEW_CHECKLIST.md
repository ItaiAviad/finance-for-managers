# Slide review checklist, from Dr. Tsaban's comments (2026-11-04 to 2026-11-11)

Apply every item to EVERY slide of both decks, not only to the slides he pointed at.

## Layout and continuity
1. One idea, one screen. Do not jump to a continuation slide when there is room on the current one. The worked-question layout (`qflow`) flows the question, the timeline and the steps through two columns; trim the prose around a solution so it fits, and only split when it truly cannot fit.
2. Use the slide's whole area (his term: "real estate"). No half-empty slides, no lone card in a corner.
3. A question shown on one slide and solved on the next: the solution slide quotes the full question text (and the answer options for multiple choice).
4. Continuity: a reader must never need to go back a slide to know the data, the formula or the payment being used.

## Gradual, click by click
5. Mathematical development appears piece by piece: one expression per click, with a short note on its meaning, then the next expression. Never a whole finished line at once. (The engine does this for every `=` line in a `Q()`; equations written directly with `ST(n, M(...))` inside `S()` slides must be split into steps by hand.)
6. Diagrams build in sync with the steps: the axis, each flow, each move. A jump back (the series formula landing one period before the first flow) is an arrow that is drawn on the click that explains it.
7. Before a hint-free solution panel starts, the slide says "לחצו כדי לחשוף את הפתרון, שלב אחר שלב" (the engine adds this in worked questions).

## Formulas beside every calculation
8. Never show a calculation without the general formula that leads to it, on the same slide, above or beside it. This includes calculations inside notes, bands, formula-box demos and multiple-choice explanations. Example: "בלי צמיחה: $\f{100}{0.10} = 1,000$" needs "ערך נוכחי של זרם אינסופי קבוע: $PV = \f{PMT}{r}$".
9. Every calculation has a named left side: `PV = ...`, `FV_{3} = ...`, `PMT = ...`, `r_{k} = ...`. Never a bare `\f{100}{0.10 - 0.05} = 2,000`. Define any new letter in words first (Hebrew, then the letter, then the English word when there is one).
10. Write the rate as `(1 + 7%)` at least in the first step of each question, and only then `1.07`. Students do not all read 1.07 as one plus the rate.

## Content quality
11. Every example, illustration and check is a full story question (who, how much, rate, period, explicit ask).
12. The example comes before the rule; a formula box appears only after the exercise that applies it.
13. Interim summaries: short "מה למדנו" stops inside long parts, not only at the part's end.
14. Memes must be immediately clear: a concrete contrast with real numbers from the lesson, readable in two seconds. Replace any meme whose joke is not obvious.
15. Check questions: one per slide, the question beside its solution; the solution unfolds click by click with its formula and, where timing matters, a timeline (`MCS(..., tls={index: TL(...)})`).
16. Amortization tables (שפיצר, קרן שווה) built cell by cell: ABOVE the table, always show the data (loan, rate, number of payments) and the periodic payment with how it was computed (formula, substitution, result), so the table can be followed without going back.
17. Index-linked bonds (lesson 2): order the data slowly and clearly; add worked questions parallel to assignment question 3 (real coupon and real cash flow, nominal cash flow year by year, price by the nominal and by the real route and why they agree, price after the coupon at the end of year 2 in real and nominal terms, the difference explained) and question 1.10 (semiannual coupon, yield given per month, sale just before a coupon), but not only those; each solved slowly, full formulas, click by click, with improved gradual diagrams.

## Accuracy
18. Hebrew: native idiom, no em dash, no maqaf (the build refuses both), sober academic register, no filler.
19. Numbers: every `=` chain must pass `check_equations.py` (0 mismatches). Answers, options and notes must agree with the solution.
20. Bidi: never list numbers separated by commas inside a Hebrew sentence or cell ("4,333.33, 4,000.00" reverses); use "מ-X עד Y" or " · ". Use " · " between references. The renumbering pass only catches singular "שאלה N" with the source number.
21. Visual check of every slide with all steps shown: nothing overlaps, nothing is cut, no tiny text, notes under equation pieces do not collide.

## Tools (run from `_build/`, add `LESSON=2` for lesson 2)
- `python3 build_deck.py` · `python3 autofit.py` (writes splits.json / splits2.json; rerun after any change in length) · `python3 test_deck.py` (overflow, wide equations, small text, MC) · `python3 check_equations.py` · `python3 shots.py <dir> [slide ids]` then `python3 sheets.py <dir>` for contact sheets · `python3 build_summary.py` (PDF).
- Source: lesson 1 `content_a.py`, `rules_x.py`, `practice_x.py`, `steps_x.py`, `content_b.py`, `content_c.py`; lesson 2 `l2_content.py`. Shared engine (do not edit without the lead): `core.py`, `anim.py`, `memes.py`, `lib.py`, `deck.css`, `deck.js`, build scripts.
