#!/usr/bin/env python3
r"""Flatten standalone-line TeX inputs without inserting paragraph breaks."""
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parent
PATTERN = re.compile(r'^[ \t]*\\input\{([^}]+)\}[ \t]*(?:%[^\n]*)?(?:\n|$)', re.MULTILINE)
def expand(path: Path, stack: tuple[Path, ...] = ()) -> str:
    path = path.resolve()
    if ROOT not in path.parents:
        raise ValueError(f'Path outside project: {path}')
    if path in stack:
        raise ValueError(f'Recursive input: {path}')
    text = path.read_text(encoding='utf-8')
    if len(re.findall(r'\\input\{', text)) != len(PATTERN.findall(text)):
        raise ValueError(f'Unsupported non-standalone input in {path}')
    def replace(match: re.Match[str]) -> str:
        child = ROOT / match.group(1)
        if not child.suffix:
            child = child.with_suffix('.tex')
        body = expand(child, stack + (path,))
        if not body.endswith('\n'):
            body += '\n'
        # Consume the original input line's endline.  Extra empty lines would
        # create \par tokens absent from the modular source, notably around
        # local macro groups.  Keep all blank lines already present in body.
        return (f'% BEGIN {child.relative_to(ROOT)}\n' + body
                + f'% END {child.relative_to(ROOT)}\n')
    return PATTERN.sub(replace, text)
if __name__ == '__main__':
    for source, target in [('main.tex', 'single.tex'), ('report.tex', 'report_single.tex')]:
        (ROOT / target).write_text(expand(ROOT/source), encoding='utf-8')
