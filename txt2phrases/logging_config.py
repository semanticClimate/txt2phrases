# logging_config.py
"""
Central logging configuration for the txt2phrases CLI.

Library code (pdf2txt, html2txt, keyword, classify_specific, merge,
pygetpaper) never attaches handlers or sets levels itself - each module
just does `logger = logging.getLogger(__name__)` and emits records. Only
the CLI entry point (cli.main()) calls configure_logging(), which attaches
a single StreamHandler to the "txt2phrases" logger and sets its level
based on the -v/--verbose and -q/--quiet flags.

Default (no flags): INFO - matches the console output the tool has always
produced (status/"Saved ..." messages visible by default).
--quiet: WARNING and above only (suppresses routine status messages).
--verbose: DEBUG and above (more detail, for troubleshooting).
If both are given, --quiet wins.
"""
import logging
import sys

LOGGER_NAME = "txt2phrases"


def configure_logging(verbosity=0, quiet=False):
    """
    (Re)configure the "txt2phrases" logger. Safe to call more than once
    (e.g. once per CLI invocation in a test suite) - it always clears any
    previously attached handler first and attaches a fresh one bound to
    the *current* sys.stdout, rather than reusing whatever sys.stdout was
    at import time.

    Parameters
    ----------
    verbosity : int
        0 (default) -> INFO. >=1 (-v) -> DEBUG.
    quiet : bool
        If True -> WARNING only, overriding `verbosity`.

    Returns
    -------
    logging.Logger
        The configured "txt2phrases" logger.
    """
    if quiet:
        level = logging.WARNING
    elif verbosity >= 1:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)
    logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    # Leave propagate at its default (True): harmless in normal use (the
    # root logger has no handler by default, so nothing double-prints),
    # and it's what lets pytest's `caplog` fixture capture these records
    # in tests without needing configure_logging() to have been called.

    return logger
