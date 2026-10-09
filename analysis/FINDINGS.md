# JAF corpus analysis — findings

Analysis of `res.json`: 599 LLM-generated Bangla folk stories, 12 Bangladeshi
cultures × 10 story types × 5 models, each rated by 4 experts on 4 dimensions
(9,584 individual judgments).

All text measures are computed on Bangla-script **word tokens**, not raw
substrings. This matters: a naive substring search reports গ্রহ ("planet") in
105 stories, but 104 of those are the unrelated গ্রহণ ("to accept"), and বাস
("bus") appears to hit 503 stories because it is a substring of বসবাস ("to
dwell"). Every count below uses whole-token matching with a light suffix
stripper (`banglautil.py`).

---

## 1. The annotation is sound — and the first agreement estimate was wrong

| Dimension | Krippendorff α (ordinal) | ICC(2,k) | 4-way exact |
|---|---|---|---|
| Cultural accuracy | 0.862 | 0.956 | 74.1% |
| Contextual fit | 0.871 | 0.960 | 75.1% |
| Narrative coherence | 0.848 | 0.946 | 77.0% |
| Linguistic register | 0.805 | 0.941 | 68.1% |

A first implementation of α returned 0.22–0.49, which sat implausibly against
ICC > 0.94. Validating the estimator on synthetic data exposed the bug — it
returned −3.15 on random data, where the correct answer is ≈0, an error of
exactly 4× in the Do normalisation. The corrected estimator returns 1.00 on
perfect agreement, −0.04 on random, 0.83 on wide-spread-plus-noise. **Anyone
re-running this should keep `tests/test_agreement.py`, which pins those four
cases.** The headline for the paper: α ≈ 0.81–0.87, well above the 0.80
convention, on all four dimensions.

Linguistic register is the noisiest dimension (α = 0.805, 68% exact) as well as
the lowest-scoring — experts agree least about exactly the thing models do worst.

## 2. Model identity is nearly the only thing that matters

One-way R² on mean rating:

| Factor | R² |
|---|---|
| **model** | **0.395** |
| culture | 0.017 |
| region | 0.015 |
| story_type | 0.003 |
| model + culture + story_type | 0.414 |

Which model wrote the story explains **24× more rating variance than which
culture it was about**, and ~130× more than the story type. Adding culture and
story type to a model-only regression buys 0.019 of R².

This is the strongest single result in the corpus. Cultural difficulty is not
what separates good output from bad; model capability is. The twelve cultures
span 1.95–2.21 in mean rating — a range narrower than the gap between any two
adjacent models.

## 3. A stylometric fingerprint, and the length illusion

A TF-IDF + logistic-regression classifier recovers **which model generated a
story with 100.0% cross-validated accuracy** (5-way, chance 20%). Not 95% —
perfect. These models are trivially separable in Bangla:

| | gemini-3-flash | mistral-large | gpt-5-mini | gpt-5.1 | qwen3-8b |
|---|---|---|---|---|---|
| mean tokens | 593 | 478 | 596 | **987** | **332** |
| MATTR-50 | 0.909 | 0.870 | 0.924 | 0.917 | **0.804** |
| `**bold**` present | 0.8% | **100%** | 0% | 2.5% | **97.5%** |
| em-dash per 1k tok | 4.0 | 10.4 | **35.5** | 19.6 | 1.3 |
| oral framing devices | **0.84** | 0.38 | 0.46 | 0.69 | **0.04** |
| explicit moral coda | 26.7% | 27.5% | 20.8% | **7.5%** | 14.3% |
| repeated 4-grams | 0.000 | 0.007 | 0.000 | 0.001 | **0.042** |

Mistral emits a bolded markdown title on **every single story**; qwen on 97.5%.
That is prompt leakage into the artifact — these are supposed to be oral folk
tales. 79% of qwen stories contain a repeated 4-gram.

**The length trap.** Story length correlates with mean rating at ρ = 0.36
(p < .001) pooled, the strongest single feature correlation in the data. It
is entirely an artifact of between-model differences. Within each model the
correlation vanishes: −0.006, −0.018, +0.058, −0.017, +0.176 (none significant
at .05). gpt-5.1 is both the longest and the best, but longer gpt-5.1 stories
are not better gpt-5.1 stories. Any model-level comparison in the paper must
control for length, and any claim that verbosity causes quality is unsupported.

This generalises: after group-mean-centring within model, **almost no surface
feature predicts any rating**. Of 19 features × 4 dimensions, the only robust
survivors are Latin-script token count → linguistic register (ρ = 0.15,
p < .001) and → narrative coherence (ρ = 0.11, p < .01). Untransliterated
indigenous terms (*Wangala*, *Singbonga*, *Apokpa*, *ngari*) are rare — 125
tokens corpus-wide — but experts reward them.

## 4. Cultural flattening, measured

If models genuinely differentiate twelve cultures, a classifier should separate
them. 12-way CV accuracy on raw text is 0.601. After masking the ethnonyms and
giveaway place names (চাকমা, গারো, রাঙামাটি, …) it drops to **0.466** — a
quarter of the apparent cultural signal was the model simply naming the group.

Per model, after masking (chance = 0.083):

| Model | culture identifiable | mean rating |
|---|---|---|
| gemini-3-flash | **0.708** | 1.94 |
| gpt-5.1 | 0.617 | **2.79** |
| mistral-large | 0.383 | 1.75 |
| gpt-5-mini | 0.225 | 1.97 |
| qwen3-8b | **0.067** | 1.85 |

**qwen3-8b falls below chance.** Its 119 stories carry essentially zero
information about which of twelve cultures they were supposed to depict. It
writes one story — opening "বাংলাদেশের একটি ছোট গ্রামে…" — and swaps the label.

The deeper point is the **dissociation**: gemini is the most culturally
differentiated model lexically yet rates below gpt-5.1 by 0.85. Differentiation
is not authenticity. Gemini reliably varies its vocabulary across cultures while
reaching for the *wrong* markers — it is internally consistent and externally
wrong, which a classifier rewards and an expert penalises. Any automatic
culture-separability metric would rank gemini first; all four experts rank it
fourth. This is a direct argument for why expert evaluation was necessary.

Confusions are geographically coherent rather than random — Chakma↔Tripura (19),
Mro↔Tripura (16), Oraon↔Santal (12), Chakma↔Marma (12) are all
Chittagong-Hill-Tracts or northwestern-plains neighbours. The models are not
confused arbitrarily; they blur real adjacencies.

## 5. Expected religious register is missing

The robust result here is an **absence**, not a contamination. Across the 100
stories for the two Christian-majority communities (Garo, Khasi), **zero**
contain any Christian marker. Correct-tradition markers of any kind appear in
only 6% of Garo and 6% of Khasi stories, against 48% for Marma and 64% for
Manipuri. Presence of a correct-tradition marker is associated with higher
cultural accuracy (2.578 vs 2.410, Mann-Whitney p = 0.026, d = +0.21).

**The Hindu-leakage claim needs tiering, and weakens considerably under it.**
Taken at face value, 20.8% of non-Bengali stories contain a strictly Hindu
marker. But Bangla has no religiously neutral everyday vocabulary for several
ritual concepts: a model writing about a Santal নায়কে *naeke* in Bangla may
gloss the role as পুরোহিত *purohit* "priest" and the rite as পূজা *puja*
"worship" without importing Hinduism — and the corpus contains exactly that
glossing, e.g. নায়কে (পুরোহিত). Deity names cannot be glosses. Over the 399
stories for communities where Hinduism is not expected:

| tier | % stories | cult. acc. with vs without | p |
|---|---|---|---|
| named deities (লক্ষ্মী, দুর্গা) | 4.3% | 2.47 vs 2.44 | 0.86 |
| institutional (ব্রাহ্মণ, মন্দির, সিঁদুর) | 11.0% | 2.44 vs 2.45 | 0.85 |
| glossable nouns (পুরোহিত, পূজা) | 18.3% | 2.31 vs 2.48 | 0.09 |

The headline 20.8% is carried by the weakest tier. Unambiguous leakage — a
named Hindu deity in a Buddhist, animist or Christian community's story —
is 4.3%, and none of the three tiers significantly predicts cultural accuracy.
**Do not claim Hindu leakage drives the low ratings.** What survives is an
asymmetry of presence: in Garo and Khasi stories the two hard tiers reach 8%
while Christian markers of any kind are at 0%. Clear cases exist (a qwen3-8b
Garo story has villagers performing দুর্গার পূজা before a tree, rated 1.81)
but they are the exception.

লক্ষ্মী still ranks among the most distinctively *Santal* words in the corpus,
which is the pattern showing up in the distinctiveness analysis.

## 6. The "big bang" hypothesis is false — and the near-miss is more interesting

The hypothesis that models import scientific/cosmological framing into origin
stories is **not supported**:

| register | % of 599 stories |
|---|---|
| cosmology (মহাবিশ্ব, ছায়াপথ, নক্ষত্র, কক্ষপথ…) | 0.83% |
| evolution / geology | 0.33% |
| matter / biology | 0.33% |
| science meta (বিজ্ঞান, গবেষণা, তত্ত্ব…) | 1.17% |
| **any scientific term** | **2.67%** |
| modern world (স্কুল, বিদ্যুৎ, পুলিশ…) | 5.84% |
| development / environmental ethics | 11.85% |

Origin Stories specifically show no elevation: sci_any in 3.4% of origin stories
vs 2.6% elsewhere (p = 0.72).

Manual inspection of all four cosmology hits confirms they are poetic, not
rationalist — the Manipuri origin story uses মহাবিশ্ব in "the creator of the
universe, Tengbanba Mapu," which is correct Meitei cosmology, not physics. **No
story in the corpus explains an origin scientifically.** Models are not
rationalising folklore; they stay firmly inside folk register and fail a
different way — by generic pastiche.

The one register that *does* intrude is contemporary development/environmental
ethics (11.9% overall), and it is sharply model-specific: **gpt-5-mini 24.2% and
gemini 21.7%, versus gpt-5.1 3.3% and mistral 2.5%**. These are the stories that
end by moralising about পরিবেশ সংরক্ষণ (environmental conservation) and
সচেতনতা (awareness). It tracks the explicit-moral-coda rate, and gpt-5.1 — the
best-rated model — moralises least (7.5% coda vs 20–28% for the rest). The NGO
register, not the science register, is the anachronism worth writing up.

## 7. Other corpus facts worth a methods footnote

- **100% of stories are a single paragraph.** No model produced paragraph
  breaks. Either generation or post-processing stripped them; this should be
  stated, since it removes a dimension of narrative structure from evaluation.
- Opening-formula diversity is high for most models (gpt-5-mini and qwen 100%
  unique first-5-tokens) but gemini repeats "অনেক অনেক কাল আগের কথা" 7 times.
- Sadhu-bhasha (literary archaic) forms are nearly absent everywhere
  (≤ 0.12 per 1k tokens), so models all write cholit-bhasha as prompted.
- Latin-script tokens total only 125 across the corpus; the Manipuri set has the
  most (0.84/story), mostly ritual terms like *Lai Haraoba* and *Apokpa*.
- Prompt echo (content-word overlap with the scenario text) ranges 0.16–0.31 by
  model and predicts nothing.

---

## What this adds to the paper

Three claims the expert ratings alone could not support:

1. **Model ≫ culture.** R² = 0.395 vs 0.017. The benchmark is measuring model
   capability, not differential cultural difficulty.
2. **Automatic culture-separability is not authenticity.** Perfect
   dissociation available in this data (gemini: most separable, fourth-rated).
   This is the empirical case for why the expert annotation was worth its cost,
   and a direct response to Pranida et al. (2025), whose finding that LLM
   stories match natives on cultural fidelity does not replicate when the
   culture axis widens from 2 to 12.
3. **The failure mode is omission, not rationalism.** 0% Christian markers
   across 100 stories for two Christian-majority communities, correct-tradition
   markers in only 6% of each, and a measurable NGO-ethics register — while
   scientific intrusion is 2.7% and flat across story types. Hindu leakage is
   real but weaker than it first appears (4.3% on the hard tier) and does not
   predict ratings.

Suggested next steps: (a) an ablation giving models a short cultural brief, to
test whether leakage is a knowledge gap or a retrieval gap — Chowdhury et al.
(2025) found context injection largely fixes Bengali cultural *knowledge*, so
the comparison is informative; (b) a length-matched re-rating to confirm the
gpt-5.1 advantage survives truncation; (c) per-expert rubric calibration on
linguistic register, the one dimension where α dips.

## Reproducing

```bash
python3 analysis/01_features.py        # -> out/features.csv  (599 x 56)
python3 analysis/02_identifiability.py # -> out/identifiability*.csv, confusion
python3 analysis/03_distinctive.py     # -> out/distinctive_words.csv, openings
python3 analysis/04_stats.py           # -> agreement, leakage, OLS, variance
python3 analysis/05_figures.py         # -> analysis/figures/*.png
python3 -m pytest analysis/tests -q    # pins the agreement estimators
```

Bangla word clouds need a Bengali font with complex-script shaping; the repo
ships `analysis/fonts/NotoSansBengali-*.ttf` (SIL OFL) and PIL must report
`features.check('raqm') == True`, or conjuncts render broken. Matplotlib does
not shape Bangla, so all chart labels are deliberately in English.
