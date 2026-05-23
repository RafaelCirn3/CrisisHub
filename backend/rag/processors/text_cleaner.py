from __future__ import annotations

import re
import unicodedata


class TextCleaner:
    """Apply light normalization before chunking and embedding."""

    _control_chars = re.compile(r"[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]")
    _spaces = re.compile(r"[ \t]+")
    _blank_lines = re.compile(r"\n{3,}")
    _hyphen_line_break = re.compile(r"(?<=\w)-\n(?=\w)")

    def clean(self, text: str) -> str:
        if not text:
            return ""

        normalized = unicodedata.normalize("NFKC", text)
        normalized = normalized.replace("\xa0", " ")
        normalized = normalized.replace("\ufeff", "")
        normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
        normalized = self._hyphen_line_break.sub("", normalized)
        normalized = self._control_chars.sub("", normalized)
        normalized = "\n".join(line.strip() for line in normalized.split("\n"))
        normalized = self._spaces.sub(" ", normalized)
        normalized = self._blank_lines.sub("\n\n", normalized)
        return normalized.strip()
