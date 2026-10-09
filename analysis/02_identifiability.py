#!/usr/bin/env python3
"""Can a classifier tell which culture a story was *supposed* to depict?

If models genuinely differentiate twelve cultures, a bag-of-words classifier
should separate them easily. If models write one generic Bengali folk tale and
swap the ethnonym, accuracy collapses once the giveaway ethnonyms are masked.
That gap is the operational measure of cultural flattening.
"""
import json, os, sys, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_predict, StratifiedKFold
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
import banglautil as B

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'analysis', 'out')

# Ethnonyms and place names that name the target culture outright. Masking them
# forces the classifier to rely on cultural *substance* rather than the label.
ETHNONYM = {
 'Bengali': ['বাঙালি','বাঙ্গালি','বাংলা','বাঙালী'],
 'Chakma': ['চাকমা','চাঙমা','রাঙামাটি','কাপ্তাই'],
 'Marma': ['মারমা','মার্মা','বান্দরবান'],
 'Santal': ['সাঁওতাল','সাঁওতালি','সান্তাল'],
 'Garo (Mandi)': ['গারো','মান্দি','আচিক','ওয়ানগালা','ওয়াংগালা'],
 'Khasi': ['খাসি','খাসিয়া','পুঞ্জি','পুঞ্জী'],
 'Manipuri (Meitei)': ['মণিপুরি','মৈতৈ','মণিপুর','মেইতেই'],
 'Mro': ['ম্রো','মুরং','চিম্বুক'],
 'Tripura': ['ত্রিপুরা','ত্রিপুরী','ককবরক','টিপরা'],
 'Hajong': ['হাজং'],
 'Rakhine': ['রাখাইন','রাখাইনদের','মগ'],
 'Oraon (Kurukh)': ['ওঁরাও','ওরাও','কুরুখ','উরাঁও'],
}
ALL_ETHNONYMS = sorted({w for v in ETHNONYM.values() for w in v}, key=len, reverse=True)


def mask(text):
    for w in ALL_ETHNONYMS:
        text = text.replace(w, 'ETHNONYM')
    return text


def analyzer(t):
    return [w for w in B.tokens(t)]


def run(texts, labels, name, groups=None):
    vec = TfidfVectorizer(analyzer=analyzer, min_df=2, sublinear_tf=True)
    X = vec.fit_transform(texts)
    y = np.array(labels)
    clf = LogisticRegression(max_iter=3000, C=5.0)
    cv = StratifiedKFold(5, shuffle=True, random_state=0)
    pred = cross_val_predict(clf, X, y, cv=cv)
    acc = accuracy_score(y, pred)
    f1 = f1_score(y, pred, average='macro')
    print(f'  {name:28} acc={acc:.3f}  macroF1={f1:.3f}  (chance={1/len(set(y)):.3f})')
    return acc, f1, y, pred


def main():
    data = json.load(open(os.path.join(ROOT, 'res.json')))
    feats = pd.read_csv(os.path.join(OUT, 'features.csv'))
    texts = [x['story'] for x in data]
    cultures = [x['culture'] for x in data]
    models = [x['model'] for x in data]
    masked = [mask(t) for t in texts]

    results = []
    print('\n=== CULTURE IDENTIFIABILITY (12-way, 5-fold CV) ===')
    a1, f1a, y, p1 = run(texts, cultures, 'raw text')
    a2, f1b, _, p2 = run(masked, cultures, 'ethnonyms masked')
    results += [{'task': 'culture_12way', 'condition': 'raw', 'acc': a1, 'macro_f1': f1a},
                {'task': 'culture_12way', 'condition': 'masked', 'acc': a2, 'macro_f1': f1b}]

    print('\n=== PER-MODEL culture identifiability (masked) ===')
    permodel = []
    for m in sorted(set(models)):
        idx = [i for i, mm in enumerate(models) if mm == m]
        a, f, _, _ = run([masked[i] for i in idx], [cultures[i] for i in idx], m[:26])
        permodel.append({'model': m, 'masked_acc': a, 'masked_f1': f,
                         'mean_rating': feats[feats.model == m].r_mean.mean()})
        results.append({'task': 'culture_by_model', 'condition': m, 'acc': a, 'macro_f1': f})

    print('\n=== MODEL IDENTIFIABILITY (5-way: whose output is this?) ===')
    a3, f3, _, _ = run(texts, models, 'model from text')
    results.append({'task': 'model_5way', 'condition': 'raw', 'acc': a3, 'macro_f1': f3})

    pd.DataFrame(results).to_csv(os.path.join(OUT, 'identifiability.csv'), index=False)
    pm = pd.DataFrame(permodel)
    pm.to_csv(os.path.join(OUT, 'identifiability_by_model.csv'), index=False)
    print('\n', pm.round(3).to_string(index=False))

    # confusion matrix on masked text, for the figure
    labs = sorted(set(cultures))
    cm = confusion_matrix(y, p2, labels=labs)
    pd.DataFrame(cm, index=labs, columns=labs).to_csv(os.path.join(OUT, 'culture_confusion_masked.csv'))

    # which culture pairs get confused most
    print('\n=== most-confused culture pairs (masked) ===')
    pairs = []
    for i, a in enumerate(labs):
        for j, b in enumerate(labs):
            if i < j:
                pairs.append((cm[i, j] + cm[j, i], a, b))
    for n, a, b in sorted(pairs, reverse=True)[:10]:
        print(f'   {n:3}  {a} <-> {b}')


if __name__ == '__main__':
    main()
