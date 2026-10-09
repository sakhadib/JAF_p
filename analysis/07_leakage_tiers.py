#!/usr/bin/env python3
"""Robustness check on the religious-leakage claim.

Not every "Hindu" marker is equally diagnostic. Bangla has no neutral everyday
vocabulary for several ritual concepts, so a model writing about a Santal naeke
in Bangla may gloss the role as পুরোহিত ("priest") and the rite as পূজা
("worship") without importing Hinduism. Deity names cannot be glosses. We
therefore tier the lexicon and report all three tiers, because the headline
20.8% figure is dominated by the weakest tier.
"""
import os, sys, json, collections, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from scipy import stats
import banglautil as B

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'analysis', 'out')

# Tier 1: named Hindu deities. Cannot be a gloss for an indigenous figure.
DEITY = ['লক্ষ্মী', 'দুর্গা', 'কালী', 'শিব', 'বিষ্ণু', 'কৃষ্ণ', 'সরস্বতী', 'গণেশ', 'হনুমান']
# Tier 2: institutions and material culture specific to Hindu practice.
INSTITUTIONAL = ['ব্রাহ্মণ', 'মন্দির', 'সিঁদুর', 'তুলসী', 'যজ্ঞ', 'শঙ্খ', 'তিলক', 'পুরাণ']
# Tier 3: ritual common nouns that double as generic Bangla vocabulary.
GLOSSABLE = ['পুরোহিত', 'পূজা', 'প্রসাদ', 'আরতি', 'ব্রত', 'হোম']

# Communities where Hinduism is NOT an expected tradition.
NON_HINDU = {'Chakma', 'Marma', 'Rakhine', 'Mro', 'Santal',
             'Oraon (Kurukh)', 'Garo (Mandi)', 'Khasi'}
DIM = 'cultural_accuracy_authenticity'


def main():
    data = json.load(open(os.path.join(ROOT, 'res.json')))
    sub = [x for x in data if x['culture'] in NON_HINDU]
    rows, tiers = [], [('deity', DEITY), ('institutional', INSTITUTIONAL),
                       ('glossable', GLOSSABLE)]
    print(f'Stories for communities where Hinduism is not expected: n={len(sub)}\n')
    print(f'{"tier":16}{"% stories":>11}{"cult.acc with":>15}{"without":>10}{"p":>9}')
    for name, lex in tiers:
        with_, without = [], []
        for x in sub:
            t = B.tokens(x['story'])
            m = statistics.mean(a['scores'][DIM] for a in x['annotations'])
            (with_ if any(B.has_word(x['story'], w, t) for w in lex) else without).append(m)
        pct = 100 * len(with_) / len(sub)
        p = stats.mannwhitneyu(with_, without).pvalue if len(with_) > 5 else float('nan')
        print(f'{name:16}{pct:10.1f}%{statistics.mean(with_):15.3f}'
              f'{statistics.mean(without):10.3f}{p:9.3f}')
        rows.append({'tier': name, 'n_terms': len(lex), 'pct_stories': pct,
                     'n_with': len(with_), 'cult_acc_with': statistics.mean(with_),
                     'cult_acc_without': statistics.mean(without), 'p': p})

    # Christian-majority communities: the clearest case, since the expected
    # tradition is entirely absent rather than merely under-represented.
    print('\nChristian-majority communities (Garo, Khasi):')
    CHRIST = ['গির্জা', 'যীশু', 'খ্রিস্ট', 'পাদ্রি', 'বাইবেল', 'ধর্মযাজক', 'বড়দিন']
    cs = [x for x in data if x['culture'] in ('Garo (Mandi)', 'Khasi')]
    n_chr = sum(1 for x in cs if any(B.has_word(x['story'], w) for w in CHRIST))
    n_hin = sum(1 for x in cs if any(B.has_word(x['story'], w)
                                     for w in DEITY + INSTITUTIONAL))
    print(f'  n={len(cs)}  Christian markers: {n_chr} ({100*n_chr/len(cs):.1f}%)  '
          f'Hindu tier-1+2: {n_hin} ({100*n_hin/len(cs):.1f}%)')
    rows.append({'tier': 'christian_in_christian_communities', 'n_terms': len(CHRIST),
                 'pct_stories': 100 * n_chr / len(cs), 'n_with': n_chr,
                 'cult_acc_with': float('nan'), 'cult_acc_without': float('nan'),
                 'p': float('nan')})
    pd.DataFrame(rows).to_csv(os.path.join(OUT, 'leakage_tiers.csv'), index=False)
    print('\nwrote leakage_tiers.csv')


if __name__ == '__main__':
    main()
