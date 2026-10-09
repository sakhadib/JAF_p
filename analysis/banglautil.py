"""Shared Bangla text utilities for the JAF analysis."""
import re, unicodedata

BN = r'ঀ-৿'
TOKEN_RE = re.compile(f'[{BN}]+')
LATIN_RE = re.compile(r"[A-Za-z][A-Za-z\-']*")
SENT_RE  = re.compile(r'[।!?\n]+')

# Bangla inflectional suffixes, longest-first, for light stemming.
SUFFIXES = [
 'দেরকে','গুলোকে','গুলিকে','টিকে','টাকে','দিগের','েদের','গুলোর','গুলির','গুলো','গুলি',
 'দের','েরা','রা','কে','তে','য়ে','ের','রে','ে','র','টি','টা','খানা','খানি',
 'ছিলেন','ছিলাম','ছিলে','ছিল','েছেন','েছে','েছি','লেন','লাম','বেন','বে','ল','ন','ি','ে',
]

def tokens(text):
    """Bangla-script word tokens, lowercase-irrelevant."""
    return TOKEN_RE.findall(text)

def sentences(text):
    return [s.strip() for s in SENT_RE.split(text) if s.strip()]

def stem(w):
    """Very light suffix stripper. Keeps >=3 chars."""
    for s in SUFFIXES:
        if w.endswith(s) and len(w) - len(s) >= 3:
            return w[:-len(s)]
    return w

# Function words / high-frequency grammatical items to exclude from content analysis.
STOP = set("""
এই সেই ওই যে যা যার যাকে যারা তা তার তাকে তারা তাদের এর ের তিনি সে আমি আমার আমরা আমাদের
তুমি তোমার তোমরা তোমাদের আপনি আপনার আপনারা আপনাদের আমায় তাহার ইহা উহা
এবং আর ও কিন্তু তবে তবু যদি তাহলে কারণ যেন যাতে অথবা কিংবা নাকি বরং যদিও
না নি নাই নয় নেই নহে হ্যাঁ হ্যা
করে করা করি করেন করল করলে করলেন করত করতে করেছে করেছেন কর
হয় হল হলো হয়ে হয়েছে হয়েছিল হতে হবে হইয়া হইল ছিল ছিলেন ছিলাম থাকে থাকা থেকে থাকত
বলে বলল বললেন বলা বলি বলতে বলেন
দিয়ে নিয়ে কাছে মধ্যে ভিতর ভেতর উপর নিচে পরে আগে সঙ্গে সাথে জন্য দ্বারা ছাড়া পর্যন্ত
খুব বেশ অনেক কিছু সব সকল প্রতি একটি একটা এক দুই তিন কোন কোনো কেউ কেহ যেমন তেমন
তখন এখন যখন কখন সেখানে এখানে যেখানে কোথায় কেন কীভাবে কিভাবে কি কী
এমন তেমনি সেটা এটা ওটা এসব ওসব তাই তবুও শুধু মাত্র আবার আরও আরো যেই
গিয়ে এসে ওঠে উঠল পড়ে গেল গেলেন এল এলেন রইল থাকল দেখে শুনে
দিন রাত সময় কথা মতো মত ভাবে রকম দিকে বার নিজের নিজে
""".split())

def content_tokens(text, do_stem=False):
    out = []
    for w in tokens(text):
        if len(w) < 2 or w in STOP:
            continue
        out.append(stem(w) if do_stem else w)
    return out

SUFFIX_SET = set(SUFFIXES)


def has_word(text, term, tok_cache=None):
    """Whole-token match, so গ্রহ does not fire inside গ্রহণ.

    A token counts as the term if it IS the term, or if it is the term plus a
    recognised inflectional suffix. Testing the remainder against the suffix
    set is more reliable than comparing stems: the stemmer is greedy and strips
    the longest match first, so stem('মন্দিরে') removes 'রে' and yields
    'মন্দি', which would never match 'মন্দির'.
    """
    toks = tok_cache if tok_cache is not None else tokens(text)
    if ' ' in term:
        return term in text
    for t in toks:
        if t == term:
            return True
        if len(t) > len(term) and t.startswith(term):
            if t[len(term):] in SUFFIX_SET:
                return True
    return False


def count_word(text, term, tok_cache=None):
    """Total occurrences of a term under the same matching rule."""
    if ' ' in term:
        return text.count(term)
    toks = tok_cache if tok_cache is not None else tokens(text)
    n = 0
    for t in toks:
        if t == term or (len(t) > len(term) and t.startswith(term)
                         and t[len(term):] in SUFFIX_SET):
            n += 1
    return n
