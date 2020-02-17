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



# STEP 3: OUTPUT
################################################################################






# CLI
################################################################################

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tex file parser')
    parser.add_argument('filepath', help='Path to tex source file')
    args = parser.parse_args()
    print(args.filepath)

    tex_text = open(args.filepath).read()
    doc = TexSoup.TexSoup(tex_text)
    chunks = split_into_chunks(doc.expr.all)
    for chunk in chunks:
        print(chunk['kind'], chunk['title'], chunk['label'])
        print(chunk['body'])
        print('---')
