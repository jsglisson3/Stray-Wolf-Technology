"""Swaps straight quotes for typographer's quotes in visible text (not in tags, scripts or styles).
Run after editing pages: python3 tools/typeset.py   (tools/build.py runs it automatically)."""
import re, pathlib
root = pathlib.Path(__file__).resolve().parent.parent / 'docs'
TOKEN = re.compile(r'(<script\b.*?</script>|<style\b.*?</style>|<title\b.*?</title>|<!--.*?-->|<[^>]+>)', re.S | re.I)

def fix_text(t):
    t = re.sub(r"(\w)'(\w)", "\\1\u2019\\2", t)          # don't, it's, owner's
    t = re.sub(r"(\s|^|\()'", "\\1\u2018", t)            # opening single quote
    t = t.replace("'", "\u2019")                         # anything left closes
    t = re.sub(r'(\s|^|\()"', '\\1\u201c', t)            # opening double quote
    t = t.replace('"', '\u201d')
    return t

NOWRAP = re.compile(r'\b(plain-English|e-commerce|15-minute|Dallas–Fort Worth)\b')

def run(path):
    s = path.read_text(encoding='utf-8')
    parts = TOKEN.split(s)
    out = []
    for i, p in enumerate(parts):
        if i % 2 == 1:
            out.append(p)
            continue
        p = fix_text(p)
        # keep short hyphenated phrases on one line (skip if already wrapped)
        if not (i > 0 and parts[i - 1] == '<span class="nb">'):
            p = NOWRAP.sub(r'<span class="nb">\1</span>', p)
        out.append(p)
    new = ''.join(out)
    if new != s:
        path.write_text(new, encoding='utf-8')
        return True
    return False

if __name__ == '__main__':
    for f in sorted(root.glob('*.html')):
        print(('typeset ' if run(f) else 'ok      ') + f.name)
