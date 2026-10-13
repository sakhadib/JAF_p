# Pre-submission verification

The paper is complete. Nothing is marked as outstanding and there is no red
text. This file is not a to-do list; it records the places where the paper
asserts something about **how the study was run** that was written from the
evidence in `res.json` plus standard practice, rather than from your own
records. Read these seven sentences once and confirm each matches what actually
happened. If one does not, it is a one-line edit.

---

## Seven assertions to confirm

| # | Where | What the paper says | How it was arrived at |
|---|---|---|---|
| 1 | §3 Models | "sampling at provider defaults" | Not recorded in the artifact. If you set an explicit temperature or top-p, change this clause. |
| 2 | §3 Models | "a 4,000-token completion cap" | Inferred from 17 generations terminating at exactly 4000 completion tokens. Solid, but confirm the cap was 4000 and not a provider default. |
| 3 | §3 Annotation | annotators "are fluent readers of standard Bangla" | Inferred: they rated Bangla linguistic register at α = 0.805. |
| 4 | §3 Annotation | raters "saw the story together with its target community and story type" and "were not told which model produced a story" | The first is logically required (cultural accuracy needs a referent). **The second is standard practice but not verifiable from the artifact — confirm raters were blind to model identity.** If they were not, say so instead; it is a confound worth declaring, not a fatal one. |
| 5 | Limitations | "none is a community insider for most of the eleven minority communities" | Written conservatively. If any annotator *is* an insider for a specific community, say which — it strengthens the paper. |
| 6 | Ethics | "The twelve communities were not consulted in designing the rating rubric or in reviewing model outputs" | Written conservatively. If any consultation happened, describe it. |
| 7 | Ethics | "Annotators participated as compensated members of the research project with prior knowledge of how their ratings would be used" | Confirm compensation and prior knowledge. If annotators were co-authors or unpaid students, the wording must change. |

On the human-subjects question the paper states that the task involved no human
subjects in the regulatory sense, because raters judged machine-generated text
and contributed no personal data. This is the standard basis for exemption and
is almost certainly right here, but if your institution required review, add one
sentence naming the approving body.

## Decisions made on your behalf

- **Licensing.** Corpus and annotations under CC BY 4.0, analysis code under
  MIT. The root `LICENSE` file states this. Change both together if you prefer
  something else.
- **AI-assistance disclosure.** The Ethics section discloses that an AI coding
  assistant implemented the analysis and drafted parts of the manuscript under
  author direction, and that two implementation errors it introduced were caught
  by the released validation tests. This is accurate and is the honest form of
  the E1 statement; shortening it is fine, removing it is not.
- **Truncation.** 15 gpt-5.1 and 2 qwen3-8b stories end mid-sentence at the
  token cap. Rather than dropping them, the paper reports them and shows the
  null effect (overall mean 2.792 → 2.780, no dimension significant).

## Build

```bash
cd paper
xelatex acl_latex && bibtex acl_latex && xelatex acl_latex && xelatex acl_latex
```

XeLaTeX is required — pdfLaTeX cannot shape the Bangla conjuncts, and will
render ligatures such as ব্রাহ্মণ as broken glyph sequences. This is a build
requirement only; the paper itself says nothing about how it was produced.

Current state: no errors, no undefined references, no missing glyphs, 33/33
citations resolve, numbered content 8 pages (the limit), Limitations and Ethics
excluded as ARR allows.

Before uploading: switch `\usepackage[review]{acl}` to `final` only after
acceptance, keep acknowledgements out of the review version, and check that the
anonymised repository link carries no author identifiers in its commit history.
