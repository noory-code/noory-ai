"""Cairn error types."""


class CairnError(Exception):
    """Base class for all Cairn errors."""


class FormatError(CairnError):
    """A decision file did not match its required format.

    Raised by the parser in :mod:`cairn.formats`. Cairn fails fast on a malformed
    decision file rather than guessing intent.
    """
