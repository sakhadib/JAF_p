#!/usr/bin/env python3
"""Inferential statistics: agreement, religious leakage, and what predicts ratings."""
import os, sys, json, collections, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'analysis', 'out')
DIMS = ['cult', 'ctx', 'narr', 'ling']
LONG = {'cult': 'cultural accuracy', 'ctx': 'contextual fit',
        'narr': 'narrative coherence', 'ling': 'linguistic register'}


def krippendorff_ordinal(matrix):
    """Krippendorff's alpha with the ordinal difference metric.

    Do = sum_u [ sum_{ordered pairs in u} delta^2 / (m_u - 1) ] / n_dot
    De = sum_c sum_k n_c n_k delta^2(c,k) / (n_dot (n_dot - 1))
    alpha = 1 - Do / De
    """
    vals = sorted({v for row in matrix for v in row})
    nd = collections.Counter(v for row in matrix for v in row)
    n_dot = sum(nd.values())

    # cumulative counts for the ordinal metric
    cum = {}
    run = 0
    for v in vals:
        run += nd[v]
        cum[v] = run

    def delta2(a, b):
        if a == b:
            return 0.0
        lo, hi = (a, b) if a < b else (b, a)
        s = cum[hi] - cum[lo] + nd[lo]          # sum of n_g for g in [lo, hi]
        return (s - (nd[lo] + nd[hi]) / 2.0) ** 2

    Do = 0.0
    for row in matrix:
        m = len(row)
        if m < 2:
            continue
        acc = 0.0
        for a, b in itertools.permutations(row, 2):
            acc += delta2(a, b)
        Do += acc / (m - 1)
    Do /= n_dot

    De = 0.0
    for a in vals:
        for b in vals:
            De += nd[a] * nd[b] * delta2(a, b)
    De /= n_dot * (n_dot - 1)
    return 1 - Do / De if De else float('nan')


def icc2k(matrix):
    """ICC(2,k) - two-way random, average of k raters, absolute agreement."""
    X = np.asarray(matrix, float)
    n, k = X.shape
    gm = X.mean()
    MSR = k * ((X.mean(1) - gm) ** 2).sum() / (n - 1)
    MSC = n * ((X.mean(0) - gm) ** 2).sum() / (k - 1)
    resid = X - X.mean(1, keepdims=True) - X.mean(0, keepdims=True) + gm
    MSE = (resid ** 2).sum() / ((n - 1) * (k - 1))
    return (MSR - MSE) / (MSR + (MSC - MSE) / n)


def main():
    df = pd.read_csv(os.path.join(OUT, 'features.csv'))
    data = json.load(open(os.path.join(ROOT, 'res.json')))
    full = {'cult': 'cultural_accuracy_authenticity', 'ctx': 'contextual_temporal_appropriateness',
            'narr': 'narrative_symbolic_coherence', 'ling': 'linguistic_expressive_appropriateness'}
    log = []

    # ---------- 1. agreement ----------
    print('=== INTER-ANNOTATOR AGREEMENT (4 experts x 599 items) ===')
    arows = []
    for d in DIMS:
        M = [[a['scores'][full[d]] for a in x['annotations']] for x in data]
        alpha = krippendorff_ordinal(M)
        icc = icc2k(M)
        exact = np.mean([len(set(r)) == 1 for r in M])
        print(f'  {LONG[d]:22} alpha={alpha:.3f}  ICC(2,k)={icc:.3f}  exact4way={100*exact:.1f}%')
        arows.append({'dimension': LONG[d], 'krippendorff_alpha_ordinal': alpha,
                      'icc_2k': icc, 'pct_exact_4way': 100 * exact})
    pd.DataFrame(arows).to_csv(os.path.join(OUT, 'agreement.csv'), index=False)

    # ---------- 2. religious leakage ----------
    print('\n=== RELIGIOUS REGISTER MATCH ===')
    df['nonbengali'] = df.culture != 'Bengali'
    nb = df[df.nonbengali]
    print(f'  non-Bengali stories with >=1 strictly-Hindu marker : '
          f'{100*(nb.hindu_leak>0).mean():.1f}%  (n={len(nb)})')
    print(f'  Bengali stories with >=1 strictly-Hindu marker     : '
          f'{100*(df[~df.nonbengali].rel_hindu_strict>0).mean():.1f}%')
    g = df.groupby('culture').agg(
        n=('story_id', 'size'),
        pct_offtradition=('rel_offtradition', lambda s: 100 * (s > 0).mean()),
        pct_expected=('rel_expected', lambda s: 100 * (s > 0).mean()),
        hindu_leak_pct=('hindu_leak', lambda s: 100 * (s > 0).mean()),
        rating=('r_mean', 'mean'), cult_rating=('r_cult', 'mean')).round(2)
    g = g.sort_values('hindu_leak_pct', ascending=False)
    print(g.to_string())
    g.to_csv(os.path.join(OUT, 'religious_leakage.csv'))

    # does off-tradition leakage depress the cultural-accuracy score?
    sub = df[df.nonbengali]
    a = sub[sub.hindu_leak > 0].r_cult
    b = sub[sub.hindu_leak == 0].r_cult
    t, p = stats.mannwhitneyu(a, b)
    d_eff = (a.mean() - b.mean()) / np.sqrt((a.var() + b.var()) / 2)
    print(f'\n  cultural-accuracy | Hindu leak present  = {a.mean():.3f} (n={len(a)})')
    print(f'  cultural-accuracy | no Hindu leak       = {b.mean():.3f} (n={len(b)})')
    print(f'  Mann-Whitney U p={p:.4g}   Cohen d={d_eff:+.3f}')
    log.append({'test': 'hindu_leak_vs_cultural_accuracy', 'p': p, 'cohen_d': d_eff,
                'mean_with': a.mean(), 'mean_without': b.mean()})

    # expected-tradition markers present -> higher score?
    a2 = sub[sub.rel_expected > 0].r_cult
    b2 = sub[sub.rel_expected == 0].r_cult
    t2, p2 = stats.mannwhitneyu(a2, b2)
    d2 = (a2.mean() - b2.mean()) / np.sqrt((a2.var() + b2.var()) / 2)
    print(f'\n  cultural-accuracy | correct-tradition marker present = {a2.mean():.3f} (n={len(a2)})')
    print(f'  cultural-accuracy | absent                            = {b2.mean():.3f} (n={len(b2)})')
    print(f'  Mann-Whitney U p={p2:.4g}   Cohen d={d2:+.3f}')
    log.append({'test': 'expected_tradition_vs_cultural_accuracy', 'p': p2, 'cohen_d': d2,
                'mean_with': a2.mean(), 'mean_without': b2.mean()})

    # ---------- 3. scientific intrusion (the big-bang hypothesis) ----------
    print('\n=== SCIENTIFIC / MODERN REGISTER INTRUSION ===')
    for col in ['sci_cosmology', 'sci_evolution', 'sci_matter', 'sci_meta', 'sci_any',
                'modern', 'dev_ethics']:
        print(f'  {col:16} stories with >=1 term: {100*(df[col]>0).mean():5.2f}%   '
              f'mean terms/story {df[col].mean():.3f}')
    orig = df[df.story_type == 'Origin Story']
    print(f'\n  Origin Stories specifically (n={len(orig)}): '
          f'sci_any>0 in {100*(orig.sci_any>0).mean():.1f}%, '
          f'cosmology>0 in {100*(orig.sci_cosmology>0).mean():.1f}%')
    rest = df[df.story_type != 'Origin Story']
    tt, pp = stats.mannwhitneyu(orig.sci_any, rest.sci_any)
    print(f'  Origin vs other story types, sci_any: p={pp:.3f} '
          f'(origin {orig.sci_any.mean():.3f} vs other {rest.sci_any.mean():.3f})')
    log.append({'test': 'origin_vs_other_sci_any', 'p': pp,
                'mean_with': orig.sci_any.mean(), 'mean_without': rest.sci_any.mean()})

    # ---------- 4. what predicts expert ratings ----------
    print('\n=== FEATURE -> RATING CORRELATIONS (Spearman, n=599) ===')
    feats = ['n_tokens', 'mattr50', 'rep_4gram', 'mean_sent_len', 'has_bold', 'emdash_per1k',
             'sadhu_per1k', 'oral_frame', 'moral_coda', 'rel_expected', 'hindu_leak',
             'rel_offtradition', 'sci_any', 'modern', 'dev_ethics', 'prompt_echo',
             'hapax_rate', 'n_paras', 'latin_tokens']
    crows = []
    print(f'  {"feature":18}' + ''.join(f'{LONG[d][:9]:>11}' for d in DIMS))
    for f in feats:
        line = f'  {f:18}'
        rec = {'feature': f}
        for d in DIMS:
            rho, p = stats.spearmanr(df[f], df[f'r_{d}'])
            star = '***' if p < .001 else '**' if p < .01 else '*' if p < .05 else ''
            line += f'{rho:>8.2f}{star:<3}'
            rec[f'rho_{d}'] = rho
            rec[f'p_{d}'] = p
        print(line)
        crows.append(rec)
    pd.DataFrame(crows).to_csv(os.path.join(OUT, 'feature_rating_corr.csv'), index=False)

    # ---------- 5. regression controlling for model and length ----------
    print('\n=== OLS: cultural accuracy ~ features + model fixed effects ===')
    df['log_tokens'] = np.log(df.n_tokens.clip(lower=1))
    m = smf.ols('r_cult ~ rel_expected + hindu_leak + rel_offtradition + log_tokens + '
                'mattr50 + oral_frame + sadhu_per1k + dev_ethics + C(model)', data=df).fit()
    print(m.summary().tables[1])
    with open(os.path.join(OUT, 'ols_cultural_accuracy.txt'), 'w') as fh:
        fh.write(str(m.summary()))

    print('\n=== OLS: linguistic register ~ features + model fixed effects ===')
    m2 = smf.ols('r_ling ~ log_tokens + mattr50 + sadhu_per1k + oral_frame + has_bold + '
                 'emdash_per1k + rep_4gram + C(model)', data=df).fit()
    print(m2.summary().tables[1])
    with open(os.path.join(OUT, 'ols_linguistic.txt'), 'w') as fh:
        fh.write(str(m2.summary()))

    # ---------- 6. variance decomposition ----------
    print('\n=== VARIANCE EXPLAINED (one-way R^2 on mean rating) ===')
    vrows = []
    for fac in ['model', 'culture', 'story_type', 'region']:
        r2 = smf.ols(f'r_mean ~ C({fac})', data=df).fit().rsquared
        print(f'  {fac:12} R^2 = {r2:.4f}')
        vrows.append({'factor': fac, 'r2_on_mean_rating': r2})
    both = smf.ols('r_mean ~ C(model) + C(culture) + C(story_type)', data=df).fit()
    print(f'  model+culture+type combined R^2 = {both.rsquared:.4f}')
    vrows.append({'factor': 'model+culture+story_type', 'r2_on_mean_rating': both.rsquared})
    pd.DataFrame(vrows).to_csv(os.path.join(OUT, 'variance_decomposition.csv'), index=False)


    # ---------- 7. WITHIN-MODEL association ----------
    # Features are strongly nested in model identity, so model fixed effects
    # absorb them. Group-mean-centring each feature within its model asks the
    # sharper question: among stories from the SAME model, does the feature
    # still track the rating?
    print('\n=== WITHIN-MODEL (group-mean-centred) Spearman ===')
    wrows = []
    wfeats = [f for f in feats if df[f].nunique() > 5]
    print(f'  {"feature":18}' + ''.join(f'{LONG[d][:9]:>11}' for d in DIMS))
    for f in wfeats:
        cx = df[f] - df.groupby('model')[f].transform('mean')
        line = f'  {f:18}'
        rec = {'feature': f}
        for d in DIMS:
            cy = df[f'r_{d}'] - df.groupby('model')[f'r_{d}'].transform('mean')
            if cx.std() == 0:
                rho, p = float('nan'), 1.0
            else:
                rho, p = stats.spearmanr(cx, cy)
            star = '***' if p < .001 else '**' if p < .01 else '*' if p < .05 else ''
            line += f'{rho:>8.2f}{star:<3}'
            rec[f'rho_{d}'] = rho
            rec[f'p_{d}'] = p
        print(line)
        wrows.append(rec)
    pd.DataFrame(wrows).to_csv(os.path.join(OUT, 'within_model_corr.csv'), index=False)

    # ---------- 8. is length the whole story? ----------
    print('\n=== LENGTH AS CONFOUND ===')
    for m_ in sorted(df.model.unique()):
        s = df[df.model == m_]
        rho, p = stats.spearmanr(s.n_tokens, s.r_mean)
        print(f'  {m_[:30]:30} within-model rho(len, rating) = {rho:+.3f} (p={p:.3g})')
    print(f'  single-paragraph stories: {100*(df.n_paras==1).mean():.1f}% '
          f'(paragraph structure is absent corpus-wide)')

    pd.DataFrame(log).to_csv(os.path.join(OUT, 'hypothesis_tests.csv'), index=False)
    print('\nwrote agreement.csv religious_leakage.csv feature_rating_corr.csv '
          'variance_decomposition.csv hypothesis_tests.csv ols_*.txt')


if __name__ == '__main__':
    main()
