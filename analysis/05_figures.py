#!/usr/bin/env python3
"""Figures for the JAF analysis. Charts use English labels (matplotlib does not
shape Bangla); Bangla text is rendered only in the word clouds, which go
through PIL/raqm and therefore shape conjuncts correctly."""
import os, sys, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import banglautil as B

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'analysis', 'out')
FIG = os.path.join(ROOT, 'analysis', 'figures')
FONT = os.path.join(ROOT, 'analysis', 'fonts', 'NotoSansBengali-400.ttf')
os.makedirs(FIG, exist_ok=True)

plt.rcParams.update({'figure.dpi': 150, 'savefig.dpi': 150, 'font.size': 9,
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.grid': True, 'grid.alpha': .25, 'grid.linewidth': .6,
                     'savefig.bbox': 'tight', 'figure.facecolor': 'white'})
INK, MUT = '#1b1b1f', '#6b7280'
PAL = ['#2f6f9f', '#c2705a', '#5c9e78', '#9a7bb0', '#c9a227']
SHORT = {'google_gemini-3-flash-preview': 'gemini-3-flash',
         'mistralai_mistral-large-2512': 'mistral-large',
         'openai_gpt-5-mini': 'gpt-5-mini', 'openai_gpt-5.1': 'gpt-5.1',
         'qwen_qwen3-8b': 'qwen3-8b'}
DIMS = ['cult', 'ctx', 'narr', 'ling']
DLAB = ['Cultural\naccuracy', 'Contextual\nfit', 'Narrative\ncoherence', 'Linguistic\nregister']


def fig1_model_dims(df):
    fig, ax = plt.subplots(figsize=(7, 3.4))
    models = df.groupby('model').r_mean.mean().sort_values(ascending=False).index
    w = 0.16
    xs = np.arange(4)
    for i, m in enumerate(models):
        v = [df[df.model == m][f'r_{d}'].mean() for d in DIMS]
        ax.bar(xs + i * w - 2 * w, v, w, label=SHORT[m], color=PAL[i], edgecolor='white', lw=.6)
    ax.axhline(2.5, color=MUT, ls='--', lw=.9)
    ax.text(3.46, 2.56, 'scale midpoint', color=MUT, fontsize=7, ha='right')
    ax.set_xticks(xs); ax.set_xticklabels(DLAB)
    ax.set_ylabel('Mean expert rating (0–5)'); ax.set_ylim(0, 5)
    ax.set_title('Every model sits below the midpoint on every dimension', loc='left', fontweight='bold')
    ax.legend(frameon=False, ncol=5, fontsize=7.5, loc='upper center', bbox_to_anchor=(.5, -.18))
    fig.savefig(f'{FIG}/fig1_model_by_dimension.png'); plt.close(fig)


def fig2_distribution(data):
    full = {'cult': 'cultural_accuracy_authenticity', 'ctx': 'contextual_temporal_appropriateness',
            'narr': 'narrative_symbolic_coherence', 'ling': 'linguistic_expressive_appropriateness'}
    fig, axes = plt.subplots(1, 4, figsize=(9, 2.5), sharey=True)
    for ax, d, lab in zip(axes, DIMS, DLAB):
        vals = [a['scores'][full[d]] for x in data for a in x['annotations']]
        c = collections.Counter(vals)
        ax.bar(list(range(6)), [100 * c[i] / len(vals) for i in range(6)],
               color='#2f6f9f', edgecolor='white', lw=.6)
        ax.set_title(lab.replace('\n', ' '), fontsize=8.5)
        ax.set_xticks(range(6)); ax.set_xlabel('score')
    axes[0].set_ylabel('% of 9,584 judgments')
    fig.suptitle('Ratings concentrate at 1–3; the top of the scale is almost unused',
                 x=.07, ha='left', fontweight='bold', fontsize=10)
    fig.savefig(f'{FIG}/fig2_score_distribution.png'); plt.close(fig)


def fig3_identifiability(df):
    pm = pd.read_csv(f'{OUT}/identifiability_by_model.csv')
    pm['lab'] = pm.model.map(SHORT)
    pm = pm.sort_values('masked_acc')
    fig, ax = plt.subplots(figsize=(6.4, 3.3))
    ax.scatter(pm.masked_acc, pm.mean_rating, s=90, color='#2f6f9f', zorder=3)
    for _, r in pm.iterrows():
        ax.annotate(r.lab, (r.masked_acc, r.mean_rating), textcoords='offset points',
                    xytext=(8, 4), fontsize=8)
    ax.axvline(1 / 12, color='#c2705a', ls='--', lw=1)
    ax.text(1 / 12 + .01, 1.72, 'chance (1/12)', color='#c2705a', fontsize=7.5)
    ax.set_xlabel('Culture identifiable from text (CV accuracy, ethnonyms masked)')
    ax.set_ylabel('Mean expert rating')
    ax.set_title('Lexical culture-marking and judged authenticity come apart',
                 loc='left', fontweight='bold')
    ax.set_xlim(0, .8)
    fig.savefig(f'{FIG}/fig3_identifiability_vs_rating.png'); plt.close(fig)


def fig4_confusion():
    cm = pd.read_csv(f'{OUT}/culture_confusion_masked.csv', index_col=0)
    norm = cm.div(cm.sum(1), axis=0)
    fig, ax = plt.subplots(figsize=(6.2, 5.4))
    im = ax.imshow(norm.values, cmap='Blues', vmin=0, vmax=.8)
    ax.set_xticks(range(len(cm))); ax.set_yticks(range(len(cm)))
    ax.set_xticklabels(cm.columns, rotation=55, ha='right', fontsize=7.5)
    ax.set_yticklabels(cm.index, fontsize=7.5)
    ax.set_xlabel('predicted'); ax.set_ylabel('true culture')
    ax.grid(False)
    for i in range(len(cm)):
        for j in range(len(cm)):
            v = norm.values[i, j]
            if v > .04:
                ax.text(j, i, f'{v:.2f}'[1:], ha='center', va='center', fontsize=6.2,
                        color='white' if v > .45 else INK)
    ax.set_title('Confusions follow real geography, not noise', loc='left', fontweight='bold')
    fig.colorbar(im, shrink=.7, label='row-normalised')
    fig.savefig(f'{FIG}/fig4_culture_confusion.png'); plt.close(fig)


def fig5_religion():
    g = pd.read_csv(f'{OUT}/religious_leakage.csv', index_col=0).sort_values('hindu_leak_pct')
    fig, ax = plt.subplots(figsize=(6.6, 3.8))
    y = np.arange(len(g))
    ax.barh(y - .2, g.pct_expected, .4, label='correct tradition present', color='#5c9e78')
    ax.barh(y + .2, g.hindu_leak_pct, .4, label='off-tradition Hindu markers', color='#c2705a')
    ax.set_yticks(y); ax.set_yticklabels(g.index, fontsize=8)
    ax.set_xlabel('% of stories')
    ax.set_title('Religious register often does not match the target community',
                 loc='left', fontweight='bold')
    ax.legend(frameon=False, fontsize=7.5, loc='lower right')
    fig.savefig(f'{FIG}/fig5_religious_leakage.png'); plt.close(fig)


def fig6_variance(df):
    v = pd.read_csv(f'{OUT}/variance_decomposition.csv')
    v = v[v.factor != 'model+culture+story_type'].sort_values('r2_on_mean_rating')
    fig, ax = plt.subplots(figsize=(5.6, 2.5))
    ax.barh(v.factor, v.r2_on_mean_rating, color=['#c7cdd4'] * (len(v) - 1) + ['#2f6f9f'])
    for i, (f, r) in enumerate(zip(v.factor, v.r2_on_mean_rating)):
        ax.text(r + .008, i, f'{r:.3f}', va='center', fontsize=8)
    ax.set_xlabel('$R^2$ on mean expert rating'); ax.set_xlim(0, .46)
    ax.set_title('Which model wrote it explains 24× more than which culture',
                 loc='left', fontweight='bold')
    fig.savefig(f'{FIG}/fig6_variance_explained.png'); plt.close(fig)


def fig7_length_confound(df):
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.2))
    ax = axes[0]
    for i, m in enumerate(sorted(df.model.unique())):
        s = df[df.model == m]
        ax.scatter(s.n_tokens, s.r_mean, s=7, alpha=.45, color=PAL[i], label=SHORT[m])
    ax.set_xlabel('story length (Bangla tokens)'); ax.set_ylabel('mean rating')
    ax.set_title('Pooled: ρ = 0.36', loc='left', fontsize=9, fontweight='bold')
    ax.legend(frameon=False, fontsize=6.5, markerscale=1.6)
    ax = axes[1]
    for i, m in enumerate(sorted(df.model.unique())):
        s = df[df.model == m]
        ax.scatter(s.n_tokens - s.n_tokens.mean(), s.r_mean - s.r_mean.mean(),
                   s=7, alpha=.45, color=PAL[i])
    ax.axhline(0, color=MUT, lw=.8); ax.axvline(0, color=MUT, lw=.8)
    ax.set_xlabel('length, centred within model'); ax.set_ylabel('rating, centred within model')
    ax.set_title('Within model: ρ ≈ 0', loc='left', fontsize=9, fontweight='bold')
    fig.suptitle('Length predicts rating only between models, never inside one',
                 x=.075, ha='left', fontweight='bold', fontsize=10.5)
    fig.savefig(f'{FIG}/fig7_length_confound.png'); plt.close(fig)


def fig8_sci(df):
    cols = ['sci_cosmology', 'sci_evolution', 'sci_matter', 'sci_meta', 'modern', 'dev_ethics']
    lab = ['cosmology', 'evolution/\ngeology', 'matter/\nbiology', 'science\nmeta',
           'modern\nworld', 'development/\nenvironment']
    fig, ax = plt.subplots(figsize=(6.4, 2.9))
    vals = [100 * (df[c] > 0).mean() for c in cols]
    ax.bar(lab, vals, color=['#c7cdd4'] * 4 + ['#9a7bb0', '#c2705a'], edgecolor='white')
    for i, v in enumerate(vals):
        ax.text(i, v + .3, f'{v:.1f}%', ha='center', fontsize=8)
    ax.set_ylabel('% of 599 stories'); ax.set_ylim(0, 15)
    ax.set_title('No "big bang" intrusion: scientific register is essentially absent',
                 loc='left', fontweight='bold')
    fig.savefig(f'{FIG}/fig8_scientific_intrusion.png'); plt.close(fig)


def wordclouds(data):
    """Bangla word clouds. PIL+raqm shapes conjuncts correctly."""
    def make(freq, path, color):
        wc = WordCloud(font_path=FONT, width=760, height=420, background_color='white',
                       max_words=70, colormap=color, prefer_horizontal=.95,
                       relative_scaling=.4, margin=3).generate_from_frequencies(freq)
        wc.to_file(path)

    bym = collections.defaultdict(collections.Counter)
    byc = collections.defaultdict(collections.Counter)
    for x in data:
        t = B.content_tokens(x['story'])
        bym[x['model']].update(t)
        byc[x['culture']].update(t)

    fig, axes = plt.subplots(2, 3, figsize=(12, 5.2))
    for ax, (m, c) in zip(axes.flat, sorted(bym.items())):
        p = f'{FIG}/wc_model_{SHORT[m]}.png'
        make(c, p, 'viridis')
        ax.imshow(plt.imread(p)); ax.axis('off'); ax.set_title(SHORT[m], fontsize=9.5)
    axes.flat[-1].axis('off')
    fig.suptitle('Most-used content words by model', x=.5, fontweight='bold')
    fig.savefig(f'{FIG}/fig9_wordclouds_by_model.png'); plt.close(fig)

    fig, axes = plt.subplots(4, 3, figsize=(12, 9))
    for ax, (cu, c) in zip(axes.flat, sorted(byc.items())):
        p = f'{FIG}/wc_culture_{cu.split()[0].replace("(", "")}.png'
        make(c, p, 'cividis')
        ax.imshow(plt.imread(p)); ax.axis('off'); ax.set_title(cu, fontsize=9.5)
    fig.suptitle('Most-used content words by target culture', x=.5, fontweight='bold')
    fig.savefig(f'{FIG}/fig10_wordclouds_by_culture.png'); plt.close(fig)

    # distinctive-word clouds: log-odds z instead of raw frequency
    dw = pd.read_csv(f'{OUT}/distinctive_words.csv')
    sub = dw[dw.axis == 'culture']
    fig, axes = plt.subplots(4, 3, figsize=(12, 9))
    for ax, cu in zip(axes.flat, sorted(sub.group.unique())):
        s = sub[sub.group == cu]
        make(dict(zip(s.word, s.z)), f'{FIG}/wcd_{cu.split()[0]}.png', 'plasma')
        ax.imshow(plt.imread(f'{FIG}/wcd_{cu.split()[0]}.png')); ax.axis('off')
        ax.set_title(cu, fontsize=9.5)
    fig.suptitle('Distinctive vocabulary by culture (log-odds with informative prior)',
                 x=.5, fontweight='bold')
    fig.savefig(f'{FIG}/fig11_distinctive_by_culture.png'); plt.close(fig)


def main():
    df = pd.read_csv(f'{OUT}/features.csv')
    data = json.load(open(os.path.join(ROOT, 'res.json')))
    fig1_model_dims(df); fig2_distribution(data); fig3_identifiability(df)
    fig4_confusion(); fig5_religion(); fig6_variance(df)
    fig7_length_confound(df); fig8_sci(df); wordclouds(data)
    print('figures written to analysis/figures/:')
    for f in sorted(os.listdir(FIG)):
        print('  ', f)


if __name__ == '__main__':
    main()
