#!/usr/bin/env python3
"""Instruction-following: the prompt imposes explicit constraints.

The shared prompt tells the model to (a) write 500-700 words, (b) avoid modern
technology, modern statecraft, specific years and contemporary vocabulary, and
(c) not invent specifics it is unsure of. Constraint (b) means the near-absence
of scientific register is partly compliance rather than spontaneous restraint,
and makes every modern-world term a measurable instruction violation.
"""
import os, sys, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from scipy import stats
import banglautil as B
import lexicons as L

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'analysis', 'out')
LO, HI = 500, 700

def main():
    data = json.load(open(os.path.join(ROOT, 'res.json')))
    feats = pd.read_csv(os.path.join(OUT, 'features.csv'))
    rows = []
    for x in data:
        toks = B.tokens(x['story'])
        words = len([w for w in x['story'].split() if w.strip()])
        rows.append({
            'story_id': x['story_id'], 'model': x['model'], 'culture': x['culture'],
            'words': words, 'tokens': len(toks),
            'in_range': LO <= words <= HI, 'under': words < LO, 'over': words > HI,
            'prompt_tokens': x['prompt_metadata'].get('prompt_tokens'),
            'completion_tokens': x['prompt_metadata'].get('completion_tokens'),
            'v_modern': sum(1 for t in L.MODERN if B.has_word(x['story'], t, toks)),
            'v_year': int(any(ch.isdigit() for ch in x['story'])),
            'v_markdown': int('**' in x['story']),
        })
    c = pd.DataFrame(rows)
    c['story_id'] = c.story_id.astype(int)
    c['any_violation'] = (c.v_modern > 0) | (c.v_year > 0) | (~c.in_range)
    c.to_csv(os.path.join(OUT, 'compliance.csv'), index=False)

    print('=== LENGTH CONSTRAINT: prompt asks for 500-700 words ===')
    g = c.groupby('model').agg(n=('words', 'size'), mean_words=('words', 'mean'),
                               pct_in_range=('in_range', lambda s: 100 * s.mean()),
                               pct_under=('under', lambda s: 100 * s.mean()),
                               pct_over=('over', lambda s: 100 * s.mean())).round(1)
    print(g.to_string())
    print(f'\n  corpus-wide in range: {100*c.in_range.mean():.1f}%')

    print('\n=== CONTENT CONSTRAINTS (explicitly prohibited by the prompt) ===')
    g2 = c.groupby('model').agg(
        pct_modern=('v_modern', lambda s: 100 * (s > 0).mean()),
        pct_digits=('v_year', lambda s: 100 * s.mean()),
        pct_markdown=('v_markdown', lambda s: 100 * s.mean()),
        pct_any=('any_violation', lambda s: 100 * s.mean())).round(1)
    print(g2.to_string())

    m = c.merge(feats[['story_id', 'r_mean', 'r_cult', 'r_ctx', 'r_ling', 'dev_ethics']],
                on='story_id')
    print('\n=== does compliance track expert rating? ===')
    for col, lab in [('in_range', 'length in range'), ('any_violation', 'any violation')]:
        a, b = m[m[col]].r_mean, m[~m[col]].r_mean
        if len(a) > 5 and len(b) > 5:
            _, p = stats.mannwhitneyu(a, b)
            print(f'  {lab:18} yes={a.mean():.3f} (n={len(a)})  no={b.mean():.3f} '
                  f'(n={len(b)})  p={p:.3g}')
    # within-model, to strip the model confound
    print('\n  within-model Spearman(|words - 600|, rating):')
    for mod in sorted(m.model.unique()):
        s = m[m.model == mod]
        rho, p = stats.spearmanr((s.words - 600).abs(), s.r_mean)
        print(f'    {mod[:30]:30} rho={rho:+.3f} p={p:.3g}')

    print('\n=== contextual-fit rating vs modern-term violation ===')
    a, b = m[m.v_modern > 0].r_ctx, m[m.v_modern == 0].r_ctx
    _, p = stats.mannwhitneyu(a, b)
    print(f'  modern term present: {a.mean():.3f} (n={len(a)})   absent: {b.mean():.3f} '
          f'(n={len(b)})   p={p:.3g}')
    print('\nwrote compliance.csv')


if __name__ == '__main__':
    main()
