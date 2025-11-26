#!/usr/bin/env python3
"""
A tiny sed-compatible replacer for simple s/pat/repl/flags expressions.

Usage:
  sed_compat.py -e 's/old/new/g' [-e 's|a|b|'] [file]

If no file is provided reads from stdin and writes to stdout. With -i it edits files in-place.
This implements a minimal subset: multiple -e expressions applied in order, only 's' command supported,
supports delimiters / or | and flags 'g' (global) and 'i' (ignorecase).
"""
from __future__ import annotations
import sys, re, argparse, io

def parse_expr(expr: str):
    if not expr.startswith('s'):
        raise ValueError('Only s/// expressions supported')
    delim = expr[1]
    parts = expr[2:].split(delim)
    if len(parts) < 2:
        raise ValueError(f'Bad expression: {expr}')
    pattern = parts[0]
    repl = parts[1]
    flags = parts[2] if len(parts) > 2 else ''
    re_flags = 0
    if 'i' in flags:
        re_flags |= re.IGNORECASE
    return pattern, repl, 'g' in flags, re_flags

def apply_expressions(text: str, exprs):
    out = text
    for pat, repl, global_flag, re_flags in exprs:
        if global_flag:
            out = re.sub(pat, repl, out, flags=re_flags)
        else:
            out = re.sub(pat, repl, out, count=1, flags=re_flags)
    return out

def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('-e', action='append', dest='exprs', default=[], help='expression like s/old/new/g')
    p.add_argument('-i', action='store_true', dest='inplace', help='edit files in place')
    p.add_argument('file', nargs='*')
    args = p.parse_args(argv)

    exprs = []
    for e in args.exprs:
        exprs.append(parse_expr(e))

    if not args.file:
        data = sys.stdin.read()
        out = apply_expressions(data, exprs)
        sys.stdout.write(out)
        return 0

    for fname in args.file:
        try:
            with open(fname, 'r', encoding='utf-8') as fh:
                data = fh.read()
        except Exception as exc:
            print(f'Error reading {fname}: {exc}', file=sys.stderr)
            return 2
        out = apply_expressions(data, exprs)
        if args.inplace:
            with open(fname, 'w', encoding='utf-8') as fh:
                fh.write(out)
        else:
            sys.stdout.write(out)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
