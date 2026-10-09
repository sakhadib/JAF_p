#!/usr/bin/env python3
"""Distinctive vocabulary per model and per culture.

Uses the log-odds ratio with an informative Dirichlet prior (Monroe, Colaresi
& Quinn 2008), which is the standard fix for raw-frequency and plain log-odds
methods over-selecting rare words. The corpus itself supplies the prior.
"""
import json, os, sys, collections, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
import banglautil as B

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'analysis', 'out')


def fightin_words(counts_a, counts_b, prior, a0=100.0):
    """z-scored log-odds-ratio with informative Dirichlet prior."""
    vocab = set(counts_a) | set(counts_b)
    tot_prior = sum(prior.values())
    na, nb = sum(counts_a.values()), sum(counts_b.values())
    out = {}
    for w in vocab:
        aw = a0 * prior.get(w, 0) / tot_prior
        if aw <= 0:
            continue
        ya, yb = counts_a.get(w, 0), counts_b.get(w, 0)
        if ya + yb < 5:
            continue
        la = math.log((ya + aw) / (na + a0 - ya - aw))
        lb = math.log((yb + aw) / (nb + a0 - yb - aw))
        var = 1.0 / (ya + aw) + 1.0 / (yb + aw)
        out[w] = (la - lb) / math.sqrt(var)
    return out


def main():
    data = json.load(open(os.path.join(ROOT, 'res.json')))
    toks = {x['story_id']: B.content_tokens(x['story']) for x in data}
    overall = collections.Counter()
    for t in toks.values():
        overall.update(t)

    rows = []
    for key in ['model', 'culture']:
        groups = collections.defaultdict(collections.Counter)
        for x in data:
            val = x[key] if key == 'model' else x['culture']
            groups[val].update(toks[x['story_id']])
        for g, cnt in groups.items():
            rest = collections.Counter()
            for g2, c2 in groups.items():
                if g2 != g:
                    rest.update(c2)
            z = fightin_words(cnt, rest, overall)
            top = sorted(z.items(), key=lambda kv: -kv[1])[:25]
            for rank, (w, s) in enumerate(top, 1):
                rows.append({'axis': key, 'group': g, 'rank': rank, 'word': w,
                             'z': round(s, 2), 'count_in_group': cnt[w]})
            print(f'\n[{key}] {g}')
            print('   ' + '  '.join(w for w, _ in top[:14]))

    pd.DataFrame(rows).to_csv(os.path.join(OUT, 'distinctive_words.csv'), index=False)
    print(f'\nwrote distinctive_words.csv ({len(rows)} rows)')

    # Opening-formula templating: how many distinct story openings per model?
    print('\n=== OPENING-FORMULA DIVERSITY (first 5 tokens) ===')
    orows = []
    bym = collections.defaultdict(list)
    for x in data:
        bym[x['model']].append(' '.join(B.tokens(x['story'])[:5]))
    for m, ops in sorted(bym.items()):
        u = len(set(ops))
        c = collections.Counter(ops).most_common(1)[0]
        print(f'  {m[:30]:30} {u:4}/{len(ops)} unique ({100*u/len(ops):5.1f}%)  top: "{c[0][:40]}" x{c[1]}')
        orows.append({'model': m, 'n': len(ops), 'unique_openings': u,
                      'pct_unique': 100 * u / len(ops), 'top_opening': c[0], 'top_count': c[1]})
    pd.DataFrame(orows).to_csv(os.path.join(OUT, 'opening_diversity.csv'), index=False)

    # Cross-story vocabulary reuse within a model: self-similarity of the lexicon.
    print('\n=== LEXICAL SELF-REPETITION ACROSS STORIES (same model) ===')
    srows = []
    for m in sorted(bym):
        ids = [x['story_id'] for x in data if x['model'] == m]
        sets = [set(toks[i]) for i in ids]
        sims = []
        for i in range(len(sets)):
            for j in range(i + 1, len(sets)):
                inter = len(sets[i] & sets[j])
                union = len(sets[i] | sets[j])
                if union:
                    sims.append(inter / union)
        print(f'  {m[:30]:30} mean pairwise Jaccard = {np.mean(sims):.4f}')
        srows.append({'model': m, 'mean_jaccard': float(np.mean(sims))})
    pd.DataFrame(srows).to_csv(os.path.join(OUT, 'lexical_selfsim.csv'), index=False)


if __name__ == '__main__':
    main()
