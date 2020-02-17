#!/usr/bin/env python
import argparse
from more_itertools import peekable
import TexSoup

CHUNK_AT_COMMANDS = [
    'chapter',
    'section',
    'subsection',
    'subsubsection',
]


# STEP 1: CHUNKING
################################################################################

def split_into_chunks(stream):
    """
    Accepts a list of Union[TexNode,TokenWithPosition] from `doc.expr.all` and
    returns a list of chunks based on `CHUNK_AT_COMMANDS` as split points.
    """
    chunks = []
    chunk = dict(kind='start', title='start', label=None, body='')
    stream2 = peekable(stream)
    for t in stream2:
        if isinstance(t, TexSoup.TexCmd) and t.name in CHUNK_AT_COMMANDS:
            chunks.append(chunk)                # Save the current chunk
            chunk = dict(                       # Start a new chunk
                kind=t.name,
                title=t.args[0].value,
                label=None,
                body=str(t)
            )
            # Look ahead to check if there is a \label command
            peeks = stream2[0:2]
            for peek in peeks:
                if isinstance(peek, TexSoup.TexCmd) and peek.name == 'label':
                    chunk['label'] = peek.args[0].value
        else:
            chunk['body'] += str(t)
    chunks.append(chunk)                        # Save the last chunk
    return chunks


# STEP 2: MATCHING
################################################################################

def test_match(leftchunk, rightchunk):
    if leftchunk['label'] == rightchunk['label'] and leftchunk['label']:
        return ('label', leftchunk['label'], rightchunk['label'])
    elif leftchunk['kind'] == rightchunk['kind']:
        return ('headinglevel', leftchunk['title'], rightchunk['title'])
    else:
        return (None, None, None)

MAX_MATCH_SKEW = 5

def find_chunk_matches(leftchunks, rightchunks):
    """
    Process the streams of chunks from the two documents and return a list of
    matches of the form:
        {
            matchkind = 'label' || 'fuzzydisplaymath' || 'headinglevel'
            leftmatch = 'str',
            rightmatch = 'str',
            leftchunks = [],
            rightchunks = [],
        }
    """
    matches = []
    match = dict(
        matchkind='beforestart',
        leftmatch=None,
        rightmatch=None,
        leftchunks=[],
        rightchunks=[],
    )
    while leftchunks and rightchunks:
        if leftchunks and not rightchunks:
            match['leftchunks'].extend(leftchunks)
            break
        if not leftchunks and rightchunks:
            match['rightchunks'].extend(rightchunks)
            break

        # Try to find a match for the next leftchunk...
        leftchunk = leftchunks[0]
        matchkind = None
        for j, rc in enumerate(rightchunks[0:MAX_MATCH_SKEW]):
            matchkind, leftmatch, rightmatch = test_match(leftchunk, rc)
            if matchkind:
                print('found match', matchkind, leftmatch, rightmatch)
                match['rightchunks'].extend(rightchunks[0:j])
                matches.append(match)
                match = dict(
                    matchkind=matchkind,
                    leftmatch=leftmatch,
                    rightmatch=rightmatch,
                    leftchunks=[leftchunk],
                    rightchunks=[rightchunks[j]],
                )
                leftchunks = leftchunks[1:]
                rightchunks = rightchunks[j+1:]
                break

        if matchkind is None:
            # Okay that didn't work :(
            # Now let's try to find a match for next rightchunk...
            rightchunk = rightchunks[0]
            print('left-first strategy failed...')
            print('trying right for', rightchunk['kind'], rightchunk['title'])

    matches.append(match)
    return matches



# STEP 3: OUTPUT
################################################################################

FRENCH_PAR_TEMPLATE = """
		\\begin{otherlanguage}{french}
%s
		\\end{otherlanguage}
"""

ENGLISH_PAR_TEMPLATE = """
%s
"""

def wrap_par_text(text, language):
    if language == 'english':
        return ENGLISH_PAR_TEMPLATE % text
    elif language == 'french':
        return FRENCH_PAR_TEMPLATE % text
    else:
        raise ValueError('Unrecognized langauge ' + language)

LEFT_COLUMN_TEMPLATE = """
	\\begin{leftcolumn*}
%s
	\\end{leftcolumn*}
"""

RIGHT_COLUMN_TEMPLATE = """
	\\begin{rightcolumn}
%s
	\\end{rightcolumn}
"""

def wrap_left_column(text):
    return LEFT_COLUMN_TEMPLATE % text

def wrap_right_column(text):
    return RIGHT_COLUMN_TEMPLATE % text


PARCOL_TEMPLATE = """
\\begin{paracol}{2}
%s

%s
\\end{paracol}
"""

def wrap_parcol(left_col, right_col):
    return PARCOL_TEMPLATE % (left_col, right_col)


def mkparcol(matches, outpath):
    print('writing bilingual output file ', outpath)
    outf = open(outpath, 'w')
    
    for match in matches:
        if not match['leftchunks'] and not match['rightchunks']:
            continue
        left_lines = [chunk['body'] for chunk in match['leftchunks']]
        left_text = ''.join(left_lines) if left_lines else ''
        left_text = left_text.replace('\\textwidth', '\\columnwidth')
        fr_text = wrap_par_text(left_text, 'french')
        left_col = wrap_left_column(fr_text)

        right_lines = [chunk['body'] for chunk in match['rightchunks']]
        right_text = ''.join(right_lines) if right_lines else ''
        right_text = right_text.replace('\\textwidth', '\\columnwidth')
        en_text = wrap_par_text(right_text, 'english')
        right_col = wrap_right_column(en_text)

        outf.write(wrap_parcol(left_col, right_col))

    outf.close()



# CLI
################################################################################

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tex file parser')
    parser.add_argument('--left', required=True, help='Path to tex source file (left column)')
    parser.add_argument('--right', required=True, help='Path to tex source file (right column)')
    parser.add_argument('--outpath', default='parcols.tex', help='Output tex file.')
    args = parser.parse_args()
    print('Running mkparalleltext.py with args=', args)

    lefttext = open(args.left).read()
    leftdoc = TexSoup.TexSoup(lefttext)
    leftchunks = split_into_chunks(leftdoc.expr.all)
    for chunk in leftchunks:
        print(chunk['kind'], chunk['title'], chunk['label'])
    print('---')

    righttext = open(args.right).read()
    rightdoc = TexSoup.TexSoup(righttext)
    rightchunks = split_into_chunks(rightdoc.expr.all)

    for chunk in rightchunks:
        print(chunk['kind'], chunk['title'], chunk['label'])
    print('---')

    matches = find_chunk_matches(leftchunks, rightchunks)
    
    for m in matches:
        print(m['matchkind'], m['leftmatch'], len(m['leftchunks']), '<-->', m['rightmatch'], len(m['rightchunks']))

    print('---')
    mkparcol(matches, args.outpath)

