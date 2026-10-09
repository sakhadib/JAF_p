"""Regression tests for the inter-annotator agreement estimators.

A first implementation of Krippendorff's alpha returned -3.15 on random data
(correct answer: ~0) because Do was normalised by sum(m_u - 1) instead of by
the number of pairable values, an error of exactly 4x at m=4. It still looked
superficially plausible on the real corpus (0.22-0.49), so only the synthetic
boundary cases caught it. These tests pin that behaviour.
"""
import os, sys, collections, itertools
import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

_HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(_HERE, '..', '04_stats.py')).read()
# 04_stats.py is a script, not an importable module name; lift just the two
# estimator functions out of it rather than running its analysis on import.
_ns = {'__file__': os.path.join(_HERE, '..', '04_stats.py'), '__name__': '_stats_frag'}
exec(_src.split('def main')[0], _ns)
krippendorff_ordinal = _ns['krippendorff_ordinal']
icc2k = _ns['icc2k']

RNG = np.random.default_rng(0)


def test_perfect_agreement_is_one():
    m = [[v] * 4 for v in RNG.integers(0, 6, 400)]
    assert krippendorff_ordinal(m) == pytest.approx(1.0, abs=1e-9)
    assert icc2k(m) == pytest.approx(1.0, abs=1e-9)


def test_random_coding_is_near_zero():
    """The case the broken implementation failed: it returned -3.15."""
    m = RNG.integers(0, 6, (500, 4)).tolist()
    assert abs(krippendorff_ordinal(m)) < 0.10


def test_signal_plus_noise_is_high():
    t = RNG.integers(0, 6, 500)
    m = [[int(np.clip(v + RNG.integers(-1, 2), 0, 5)) for _ in range(4)] for v in t]
    assert krippendorff_ordinal(m) > 0.75


def test_restricted_range_lowers_alpha_not_to_negative():
    """Narrow true-score spread depresses alpha but must not send it below 0."""
    t = RNG.integers(2, 4, 500)
    m = [[int(np.clip(v + RNG.integers(-1, 2), 0, 5)) for _ in range(4)] for v in t]
    a = krippendorff_ordinal(m)
    assert 0.0 < a < 0.6


def test_alpha_is_bounded_above_by_one():
    for _ in range(5):
        m = RNG.integers(0, 6, (200, 4)).tolist()
        assert krippendorff_ordinal(m) <= 1.0 + 1e-9


def test_ordinal_metric_penalises_distant_disagreement_more():
    """0 vs 5 must cost more than 2 vs 3, which nominal alpha would not capture."""
    base = [[2, 2, 2, 2]] * 200
    near = base + [[2, 3, 2, 3]] * 50
    far = base + [[0, 5, 0, 5]] * 50
    assert krippendorff_ordinal(far) < krippendorff_ordinal(near)


def test_real_corpus_agreement_is_substantial():
    import json
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
    path = os.path.join(root, 'res.json')
    if not os.path.exists(path):
        pytest.skip('res.json not present')
    data = json.load(open(path))
    for dim in ['cultural_accuracy_authenticity', 'contextual_temporal_appropriateness',
                'narrative_symbolic_coherence', 'linguistic_expressive_appropriateness']:
        m = [[a['scores'][dim] for a in x['annotations']] for x in data]
        a = krippendorff_ordinal(m)
        assert 0.75 < a < 0.95, f'{dim} alpha={a}'
