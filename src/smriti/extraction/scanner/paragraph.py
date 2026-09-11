"""
scanner/paragraph.py — Paragraph accumulation logic.
"""


def accumulate_paragraph(
    lines: list[str],
    start_char: int,
    current_char_pos: int,
) -> tuple[str, int, int]:
    """
    Accumulate a paragraph block from a list of lines.

    Returns:
        (paragraph_text, char_start, char_end)
    """
    para_text = "\n".join(lines).strip()
    char_start = start_char
    char_end = current_char_pos
    return para_text, char_start, char_end
