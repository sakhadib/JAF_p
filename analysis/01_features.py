#!/usr/bin/env python3
"""Extract per-story features from res.json into analysis/out/features.csv.

Every feature is computed on Bangla-script word tokens (see banglautil), not
on raw substrings, so that e.g. গ্রহ does not fire inside গ্রহণ.
"""
import json, re, os, sys, collections, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
import banglautil as B
import lexicons as L

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(ROOT, 'analysis', 'out')
os.makedirs(OUT, exist_ok=True)

DIMS = ['cultural_accuracy_authenticity', 'contextual_temporal_appropriateness',
        'narrative_symbolic_coherence', 'linguistic_expressive_appropriateness']
SHORT = {DIMS[0]: 'cult', DIMS[1]: 'ctx', DIMS[2]: 'narr', DIMS[3]: 'ling'}


def mattr(toks, w=50):
    """Moving-average type-token ratio: length-robust lexical diversity."""
    if len(toks) < w:
        return len(set(toks)) / len(toks) if toks else 0.0
    vals = [len(set(toks[i:i + w])) / w for i in range(len(toks) - w + 1)]
    return sum(vals) / len(vals)


def repeated_ngram_rate(toks, n=4):
    """Share of n-gram tokens that are not the first occurrence of their n-gram."""
    if len(toks) < n:
        return 0.0
    grams = [tuple(toks[i:i + n]) for i in range(len(toks) - n + 1)]
    c = collections.Counter(grams)
    return sum(v - 1 for v in c.values()) / len(grams)


def lex_hits(text, toks, lex):
    """Number of distinct lexicon terms present as whole tokens."""
    return sum(1 for t in lex if B.has_word(text, t, toks))


def lex_count(text, toks, lex):
    """Total token occurrences matching the lexicon."""
    return sum(B.count_word(text, t, toks) for t in lex)


def main():
    data = json.load(open(os.path.join(ROOT, 'res.json')))
    rows = []
    for x in data:
        story = x['story']
        toks = B.tokens(story)
        ctoks = [w for w in toks if w not in B.STOP and len(w) > 1]
        sents = B.sentences(story)
        n = len(toks) or 1

        r = {
            'story_id': x['story_id'],
            'model': x['model'],
            'culture': x['culture'],
            'prompt_id': x['prompt_metadata']['prompt_id'],
            'region': x['prompt_metadata']['region'],
            'story_type': x['prompt_metadata']['story_type'],
        }

        # --- length & diversity ---
        r['n_chars'] = len(story)
        r['n_tokens'] = len(toks)
        r['n_types'] = len(set(toks))
        r['n_sents'] = len(sents)
        r['mean_sent_len'] = len(toks) / max(len(sents), 1)
        r['ttr'] = len(set(toks)) / n
        r['mattr50'] = mattr(toks, 50)
        r['hapax_rate'] = sum(1 for v in collections.Counter(toks).values() if v == 1) / n
        r['rep_4gram'] = repeated_ngram_rate(toks, 4)
        r['content_ratio'] = len(ctoks) / n

        # --- surface / formatting tells ---
        r['has_bold'] = int('**' in story)
        r['n_bold'] = len(re.findall(r'\*\*(.{1,80}?)\*\*', story))
        r['emdash_per1k'] = 1000 * story.count('—') / n
        r['latin_tokens'] = len(B.LATIN_RE.findall(story))
        r['n_paras'] = len([p for p in story.split('\n') if p.strip()])
        r['quote_per1k'] = 1000 * (story.count('“') + story.count('‘')) / n

        # --- register ---
        r['sadhu_per1k'] = 1000 * lex_count(story, toks, L.SADHU) / n
        r['oral_frame'] = lex_hits(story, toks, L.ORAL_FRAME)
        r['moral_coda'] = int(any(m in story[-400:] for m in L.MORAL_CODA))

        # --- religious register ---
        for nm, lex in [('hindu_strict', L.HINDU_STRICT), ('hindu_generic', L.HINDU_GENERIC),
                        ('muslim', L.MUSLIM), ('buddhist', L.BUDDHIST),
                        ('christian', L.CHRISTIAN), ('animist', L.ANIMIST)]:
            r[f'rel_{nm}'] = lex_hits(story, toks, lex)

        expected = L.CULTURE_RELIGION[x['culture']]
        emap = {'HINDU': r['rel_hindu_strict'], 'MUSLIM': r['rel_muslim'],
                'BUDDHIST': r['rel_buddhist'], 'CHRISTIAN': r['rel_christian'],
                'ANIMIST': r['rel_animist']}
        r['rel_expected'] = sum(emap[e] for e in expected)
        r['rel_offtradition'] = sum(v for k, v in emap.items() if k not in expected)
        # Hindu leakage specifically into cultures where Hinduism is not expected.
        r['hindu_leak'] = r['rel_hindu_strict'] if 'HINDU' not in expected else 0

        # --- scientific / modern intrusion ---
        r['sci_cosmology'] = lex_hits(story, toks, L.SCI_COSMOLOGY)
        r['sci_evolution'] = lex_hits(story, toks, L.SCI_EVOLUTION)
        r['sci_matter'] = lex_hits(story, toks, L.SCI_MATTER)
        r['sci_meta'] = lex_hits(story, toks, L.SCI_META)
        r['sci_any'] = lex_hits(story, toks, L.SCI_ALL)
        r['modern'] = lex_hits(story, toks, L.MODERN)
        r['dev_ethics'] = lex_hits(story, toks, L.DEV_ETHICS)

        # --- prompt echo: content-word overlap with the scenario text ---
        scen = set(B.content_tokens(x['prompt_metadata']['scenario']))
        r['prompt_echo'] = len(scen & set(ctoks)) / max(len(scen), 1)

        # --- opening formula (first 5 tokens, for templating analysis) ---
        r['opening5'] = ' '.join(toks[:5])

        # --- ratings ---
        for d in DIMS:
            vals = [a['scores'][d] for a in x['annotations']]
            r[f'r_{SHORT[d]}'] = statistics.mean(vals)
            r[f'sd_{SHORT[d]}'] = statistics.pstdev(vals)
            r[f'range_{SHORT[d]}'] = max(vals) - min(vals)
        r['r_mean'] = statistics.mean(r[f'r_{SHORT[d]}'] for d in DIMS)
        rows.append(r)

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, 'features.csv'), index=False)
    print(f'wrote features.csv  {df.shape[0]} rows x {df.shape[1]} cols')
    return df


if __name__ == '__main__':
    main()
