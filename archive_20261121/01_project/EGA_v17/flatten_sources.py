#!/usr/bin/env python3
r"""Flatten TeX \input files only; fail on unexpected include paths."""
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parent
PATTERN = re.compile(r'\\input\{([^}]+)\}')
def expand(path: Path, stack: tuple[Path, ...] = ()) -> str:
    path = path.resolve()
    if ROOT not in path.parents:
        raise ValueError(f'Path outside project: {path}')
    if path in stack:
        raise ValueError(f'Recursive input: {path}')
    text = path.read_text(encoding='utf-8')
    def replace(match: re.Match[str]) -> str:
        child = ROOT / match.group(1)
        if not child.suffix:
            child = child.with_suffix('.tex')
        return (f'\n% BEGIN {child.relative_to(ROOT)}\n'
                + expand(child, stack + (path,))
                + f'\n% END {child.relative_to(ROOT)}\n')
    return PATTERN.sub(replace, text)
if __name__ == '__main__':
    for source, target in [('main.tex', 'single.tex'), ('report.tex', 'report_single.tex')]:
        (ROOT / target).write_text(expand(ROOT/source), encoding='utf-8')
