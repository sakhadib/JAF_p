# analysis/

Quantitative analysis of `res.json` beyond the expert ratings. Findings are in
[FINDINGS.md](FINDINGS.md); figures in `figures/`, tables in `out/`.

| file | what it does |
|---|---|
| `banglautil.py` | Bangla tokenisation, light stemmer, stopwords, whole-token matching |
| `lexicons.py` | curated term lists (religious traditions, scientific register, sadhu-bhasha, oral framing) |
| `01_features.py` | 56 per-story features → `out/features.csv` |
| `02_identifiability.py` | can a classifier recover the target culture / the model? |
| `03_distinctive.py` | log-odds distinctive vocabulary, opening-formula diversity |
| `04_stats.py` | agreement, religious leakage, OLS, variance decomposition |
| `05_figures.py` | all figures and Bangla word clouds |
| `06_compliance.py` | adherence to the prompt's own length and content constraints |
| `07_leakage_tiers.py` | robustness check tiering religious markers by diagnostic strength |
| `tests/` | pins the agreement estimators and the tokeniser |

```bash
for f in analysis/0*.py; do python3 "$f"; done
python3 -m pytest analysis/tests -q
```

Dependencies beyond the scientific stack: `wordcloud`, `statsmodels`, `pytest`.

**Text matching.** Bangla needs whole-token matching, not substring search: a
naive search reports গ্রহ ("planet") in 105 stories, of which ~104 are গ্রহণ
("to accept"). `banglautil.has_word` matches a token only if it is the term or
the term plus a recognised inflectional suffix.

**Fonts.** Word clouds need `fonts/NotoSansBengali-400.ttf` (SIL OFL, vendored)
and a PIL built with raqm — check `PIL.features.check('raqm')`. Without
shaping, Bengali conjuncts render broken. Matplotlib does not shape Bangla, so
chart labels are intentionally English.
