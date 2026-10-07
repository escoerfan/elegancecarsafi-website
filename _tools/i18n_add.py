#!/usr/bin/env python3
"""Fügt Übersetzungen in js/lang/<code>.js ein (vor dem schließenden '};').

Aufruf:  python3 _tools/i18n_add.py neue-texte.json "Abschnittsname"
JSON-Format: {"en": {"Deutscher Text": "English text", ...}, "pl": {...}, ...}
Vorhandene Schlüssel werden überschrieben, nicht doppelt angelegt.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def add(code, entries, section):
    path = os.path.join(ROOT, 'js', 'lang', code + '.js')
    src = open(path, encoding='utf-8').read()
    new = {}
    for key, val in entries.items():
        line_re = re.compile(r'^(\s*)' + re.escape(json.dumps(key, ensure_ascii=False)) + r':\s*".*?",?\s*$', re.M)
        enc_val = json.dumps(val, ensure_ascii=False)
        m = line_re.search(src)
        if m:                                   # vorhandenen Eintrag ersetzen
            comma = ',' if m.group(0).rstrip().endswith(',') else ''
            src = src[:m.start()] + m.group(1) + json.dumps(key, ensure_ascii=False) + ': ' + enc_val + comma + src[m.end():]
        else:
            new[key] = enc_val
    if new:
        end = src.rindex('};')
        head = src[:end].rstrip()
        if not head.endswith(',') and not head.endswith('{'):
            head += ','
        block = '\n\n  /* ---- ' + section + ' ---- */\n' + ',\n'.join(
            '  ' + json.dumps(k, ensure_ascii=False) + ': ' + v for k, v in new.items())
        src = head + block + '\n' + src[end:]
    open(path, 'w', encoding='utf-8').write(src)
    return len(new), len(entries) - len(new)


if __name__ == '__main__':
    data = json.load(open(sys.argv[1], encoding='utf-8'))
    section = sys.argv[2] if len(sys.argv) > 2 else 'Ergänzungen'
    for code, entries in data.items():
        n, r = add(code, entries, section)
        print('%s: %d neu, %d ersetzt' % (code, n, r))
