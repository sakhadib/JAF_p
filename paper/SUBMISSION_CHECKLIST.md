# Submission checklist — six facts only the authors can supply

The paper is otherwise complete and compiles clean. Six slots are marked with
`\authorfill{}` and render in red; search the `.tex` for `authorfill`. These are
facts about how the corpus and annotation were actually produced. They cannot be
inferred from `res.json` and must not be guessed — the Responsible NLP checklist
requires them, and ARR desk-rejects submissions that systematically omit them.

Delete the `\newcommand{\authorfill}` line once all six are filled; the paper
will then compile with no red text.

---

### 1. Generation parameters — §3, "Models" (line ~208)
Checklist C1–C4. Needed: temperature, top-p, max tokens, access route (direct
API vs. a router — the model slugs look like OpenRouter identifiers), the dates
of generation, and the exact provider snapshot per model.

> Template: "Stories were generated between DATE and DATE via PROVIDER at
> temperature T and top-p P, with a MAX-token cap. Model snapshots were SLUG."

The artifact already records `prompt_tokens` and `completion_tokens` per
generation, so you need only add the sampling settings.

### 2. Annotation protocol — §3, "Annotation" (line ~217)
Checklist D1. Needed: the full rubric with level descriptors. What distinguishes
a 3 from a 4 on cultural accuracy? Reviewers will ask, because the whole paper
rests on these four scales. Also: were annotators shown the target culture and
the prompt, or only the story? Were they blind to which model produced it?
(If they were not blind to model, say so — it is a confound worth declaring.)

### 3. Annotator relationship to the twelve communities — Limitations (line ~669)
**The highest-risk item.** Four raters cannot be insiders to twelve
communities. State plainly, per community, whether any annotator is a community
insider, a regional specialist, or neither.

> Template: "Of the four annotators, N are native speakers of Bangla with
> academic training in RELEVANT FIELD. ANNOTATOR is an insider to COMMUNITY. For
> the remaining K communities no annotator is a community member, and
> authenticity judgments for those communities rest on scholarly familiarity
> rather than lived experience."

A disclosed gap is a limitation. A concealed one is a reason to reject.

### 4. Recruitment, compensation, consent, IRB — Ethics (line ~703)
Checklist D2–D5. Needed: how annotators were recruited, what they were paid and
why that is fair for the local context, how consent was obtained, and whether an
ethics board approved or exempted the protocol. Also: were any of the twelve
communities consulted on the rubric or the outputs? If not, say so.

### 5. Licensing and release terms — Ethics (line ~710)
Checklist B2–B4. Needed: the licence for corpus and code, and the redistribution
terms for each provider's outputs (these differ, and some restrict
redistribution of generations). Also confirm the generated text was checked for
personally identifying information — relevant here because the stories contain
invented personal names that could coincide with real individuals.

### 6. AI-assistance disclosure — Ethics (line ~721)
Checklist E1. Disclose any AI assistance in corpus construction, analysis code,
or writing, per the ACL authorship policy. This is a disclosure requirement, not
a penalty.

---

## Before submitting

- [ ] All six slots filled; `\authorfill` definition deleted
- [ ] Compile with **XeLaTeX**, not pdfLaTeX (`kalpurush.ttf` + `fontspec`):
      `xelatex acl_latex && bibtex acl_latex && xelatex acl_latex && xelatex acl_latex`
- [ ] Check the Bangla renders with correct conjuncts (ভান্তে, ব্রাহ্মণ,
      মণ্ডপ) — if they appear as broken glyph sequences, the `Script=Bengali`
      option or HarfBuzz renderer is not active
- [ ] Numbered content ≤ 8 pages; Limitations and Ethics do not count
- [ ] `\usepackage[review]{acl}` for submission; switch to `final` on acceptance
- [ ] No acknowledgements in the review version (they break anonymity)
- [ ] Verify the anonymised repository link is live and contains no author
      identifiers in commit history
