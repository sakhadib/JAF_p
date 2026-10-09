"""Tests for Bangla tokenisation and whole-token matching.

The motivating bug: naive substring search reported গ্রহ ("planet") in 105
stories, but nearly all were গ্রহণ ("to accept"); বাস ("bus") appeared to hit
503 stories as a substring of বসবাস ("to dwell"). Whole-token matching with a
light suffix stripper fixes this, and these tests pin it.
"""
import os, sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import banglautil as B


def test_tokens_splits_on_punctuation_and_keeps_bangla_only():
    assert B.tokens('গ্রামের মানুষ—জল, বন।') == ['গ্রামের', 'মানুষ', 'জল', 'বন']
    assert B.tokens('village 2024 গ্রাম') == ['গ্রাম']


def test_has_word_rejects_substring_matches():
    """The core false-positive cases from the first pass."""
    assert not B.has_word('তিনি উপহার গ্রহণ করলেন', 'গ্রহ')
    assert not B.has_word('তারা সেখানে বসবাস করত', 'বাস')
    assert not B.has_word('একটি জিনিস পড়ে ছিল', 'জিন')


def test_has_word_accepts_exact_and_lightly_inflected_forms():
    assert B.has_word('আকাশে গ্রহ দেখা যায়', 'গ্রহ')
    assert B.has_word('গ্রামের মানুষ', 'গ্রাম')
    assert B.has_word('মন্দিরে পূজা হলো', 'মন্দির')


def test_sentences_splits_on_danda():
    s = B.sentences('এক গ্রাম ছিল। নদী বইত। শেষ!')
    assert len(s) == 3 and s[0] == 'এক গ্রাম ছিল'


def test_stem_keeps_minimum_length():
    assert len(B.stem('জল')) >= 2
    assert B.stem('গ্রামের') == 'গ্রাম'


def test_content_tokens_drop_function_words():
    out = B.content_tokens('এই সেই এবং গ্রামের মানুষ')
    assert 'এই' not in out and 'এবং' not in out
    assert 'গ্রামের' in out and 'মানুষ' in out
