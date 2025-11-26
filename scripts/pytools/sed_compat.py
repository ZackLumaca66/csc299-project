#!/usr/bin/env python3
"""Minimal sed-like s/// replacement tool used by project scripts.

Supports:
- Multiple -e expressions: -e 's/old/new/g'
- In-place editing with -i (files passed as args)
- Reads stdin and writes to stdout when no files provided
- Simple flags: g (global), i (ignore case)

This is intentionally small and only implements the features used
by the repository's helper scripts.
"""
import argparse
import re
import sys


def parse_substitution(expr: str):
    # Expect forms like s/old/new/flags or s|old|new|flags
    if not expr or not expr.startswith('s'):
        raise SystemExit(f"Invalid expression: {expr}")
    delim = expr[1]
    parts = expr.split(delim)
    # parts: ['s', 'old', 'new', 'flags'] (flags optional)
    if len(parts) < 3:
        raise SystemExit(f"Invalid s/// expression: {expr}")
    old = parts[1]
    new = parts[2]
    flags = parts[3] if len(parts) > 3 else ''
    # Interpret escaped \n in replacement as newline
    new = new.replace('\\n', '\n')
    re_flags = 0
    if 'i' in flags:
        re_flags |= re.IGNORECASE
    # Use re.sub semantics; if 'g' not present, do a single replace
    global_flag = 'g' in flags
    return old, new, re_flags, global_flag


def apply_substitutions(text: str, subs):
    for old, new, re_flags, global_flag in subs:
        try:
            pattern = re.compile(old, re_flags)
        except re.error:
            # Fallback: escape pattern
            pattern = re.compile(re.escape(old), re_flags)
        if global_flag:
            text = pattern.sub(new, text)
        else:
            text = pattern.sub(new, text, count=1)
    return text


def main(argv=None):
    parser = argparse.ArgumentParser(description='sed_compat: minimal sed s/// tool')
    parser.add_argument('-e', action='append', dest='exprs', default=[], help='substitution expression (s/old/new/flags)')
    parser.add_argument('-i', action='store_true', dest='inplace', help='edit files in-place')
    parser.add_argument('files', nargs='*', help='files to edit (optional)')
    args = parser.parse_args(argv)

    if not args.exprs:
        # If no expressions, passthrough
        if args.files:
            for fname in args.files:
                with open(fname, 'r', encoding='utf-8') as fh:
                    sys.stdout.write(fh.read())
        else:
            sys.stdout.write(sys.stdin.read())
        return

    subs = [parse_substitution(e) for e in args.exprs]

    if args.files:
        for fname in args.files:
            with open(fname, 'r', encoding='utf-8') as fh:
                content = fh.read()
            new_content = apply_substitutions(content, subs)
            if args.inplace:
                with open(fname, 'w', encoding='utf-8') as fh:
                    fh.write(new_content)
            else:
                sys.stdout.write(new_content)
    else:
        # read stdin
        content = sys.stdin.read()
        out = apply_substitutions(content, subs)
        sys.stdout.write(out)


if __name__ == '__main__':
    main()
