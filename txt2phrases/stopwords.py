# stopwords.py
"""
Default and user-supplied stopword handling for keyphrase extraction.

Filters out journal names, publisher/licence boilerplate, and similar
non-content noise that the keyphrase extraction model sometimes picks up
from PDF headers, footers, and citation blocks.
"""

# Exact-match terms (case-insensitive). A keyphrase is dropped only if it
# matches one of these *exactly* after stripping/casefolding - conservative
# on purpose, to avoid dropping legitimate content keyphrases that happen to
# share a word with a journal name (e.g. "public health policy" should NOT
# be dropped just because "Public Health" is a journal name fragment).
DEFAULT_STOPWORDS = {
    "bmc psychology",
    "bmc public health",
    "bmc medicine",
    "bmc health services research",
    "plos one",
    "plos medicine",
    "scientific reports",
    "nature communications",
    "frontiers in psychology",
    "creative commons",
    "creative commons licence",
    "creative commons license",
    "creative commons attribution",
    "creative commons attribution license",
    "creative commons attribution licence",
    "all rights reserved",
    "open access",
    "world health organization",
    "world health organisation",
    "who",
    "springer nature",
    "elsevier",
    "wiley",
    "et al",
    "supplementary material",
    "supporting information",
    "conflict of interest",
    "author contributions",
    "funding statement",
}

# Prefix patterns (case-insensitive, matched against the start of the
# keyphrase). Journal names are often extracted with a trailing volume/issue
# fragment that varies run to run, so exact-match alone misses many
# variants (e.g. "Journal of Climate Anxiety Studies" vs. "Journal of
# Environmental Psychology"). A prefix match catches the family regardless
# of what follows.
DEFAULT_STOPWORD_PREFIXES = (
    "journal of ",
    "frontiers in ",
    "proceedings of ",
    "transactions on ",
    "annals of ",
    "creative commons ",
)


def _normalize(term):
    return term.strip().casefold()


def load_stopwords(custom_path=None, use_defaults=True):
    """
    Build the (exact_set, prefix_tuple) stopword configuration to filter
    extracted keyphrases with.

    Parameters
    ----------
    custom_path : str | Path | None
        Optional path to a text file of additional stopwords, one per line.
        Blank lines and lines starting with '#' are ignored. Entries are
        treated as exact-match terms (case-insensitive).
    use_defaults : bool
        If True (default), the built-in DEFAULT_STOPWORDS /
        DEFAULT_STOPWORD_PREFIXES are included. If False, only terms from
        `custom_path` (if given) are used.

    Returns
    -------
    (set[str], tuple[str, ...])
        Normalized exact-match stopwords and prefix patterns.
    """
    exact = set(DEFAULT_STOPWORDS) if use_defaults else set()
    prefixes = tuple(DEFAULT_STOPWORD_PREFIXES) if use_defaults else tuple()

    if custom_path:
        with open(custom_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                exact.add(_normalize(line))

    return exact, prefixes


def is_stopword(keyword, exact_stopwords, prefix_stopwords):
    """
    Check whether `keyword` should be filtered out as boilerplate/noise.
    """
    normalized = _normalize(keyword)
    if not normalized:
        return True
    if normalized in exact_stopwords:
        return True
    return any(normalized.startswith(prefix) for prefix in prefix_stopwords)


def filter_stopwords(counts, exact_stopwords, prefix_stopwords):
    """
    Filter a {keyword: count} mapping (e.g. a collections.Counter),
    dropping entries that match the stopword configuration.

    Returns a new dict/Counter-compatible mapping of the same type as
    `counts` with stopword entries removed; input is not mutated.
    """
    filtered = type(counts)()
    for keyword, count in counts.items():
        if not is_stopword(keyword, exact_stopwords, prefix_stopwords):
            filtered[keyword] = count
    return filtered
