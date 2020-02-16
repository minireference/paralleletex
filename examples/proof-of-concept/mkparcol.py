#!/usr/bin/env python3
import re




LEFT_SOURCE_FILE = '11_solving_equationsFR.tex'
LEFT_LANGUAGE = 'french'

RIGHT_SOURCE_FILE = '11_solving_equationsEN.tex'
RIGHT_LANGUAGE = 'english'

PARCOL_OUT_FILE = '11_solving_equations_FR_en.tex'

CHOOSE_SHARED = 'left'

PAR_RE = re.compile('[.*]?\%\%[ ]?PAR(?P<par_id>[\d]{2,4})')
SHARED_RE = re.compile('[.*]?\%\%[ ]?SHARED(?P<shared_id>[\d]{2,4})')
END_OF_FILE_STR = '__END_OF_FILE__'


def parse_line(line):
    if END_OF_FILE_STR in line:
        return {'kind': 'endoffile'}
    par_m = PAR_RE.search(line)
    if par_m:
        return {
            'kind': 'newpar',
            'par_id':par_m.groupdict()['par_id']
        }

    shared_m = SHARED_RE.search(line)
    if shared_m:
        return {
            'kind': 'newshared',
            'shared_id': shared_m.groupdict()['shared_id']
        }

    return {
        'kind': 'regularline',
        'line': line,
    }


def parse_tex_source(filepath):
    """
    Split the source text file on the %%SHARED  and %%PAR markers in the source.

    Return a dictionary of the form:
    {
        'sequence': ['SHARED001', 'PAR001', ...],
        'chunks': {
            'SHARED001': [(str)],   # lines of the shaed chunk SHARED001
            'PAR001': [(str)],      # lines of the chunk PAR001
            ...
        }
    }
    """
    with open(filepath) as source_file:
        lines = source_file.readlines()
        lines.append('__END_OF_FILE__')

    # setup return dict
    data = {
        'sequence': [],
        'chunks': {}
    }

    cur_id = None
    cur_lines = None
    cur_state = 'filestart'
    for line in lines:
        
        line_dict = parse_line(line)
        # print('state:', cur_id, cur_lines, cur_state)
        # print('parsing', line_dict)
        kind = line_dict['kind']

        if cur_state == 'filestart' and line_dict['kind'] == 'regularline':
            print('skipping start of file line', line)
            continue

        # close cur when encountering new chunk or end-of-file
        if cur_state in ['inpar', 'inshared'] and kind in ['newpar', 'newshared', 'endoffile']:
            data['sequence'].append(cur_id)
            data['chunks'][cur_id] = cur_lines

        # state machine logic:
        if line_dict['kind'] == 'regularline':
            cur_lines.append(line)    

        elif line_dict['kind'] == 'newpar':
            # stuar new cur
            cur_id = 'PAR'+line_dict['par_id']
            cur_lines = []
            cur_state = 'inpar'
    
        elif line_dict['kind'] == 'newshared':
            # stuar new cur
            cur_id = 'SHARED'+line_dict['shared_id']
            cur_lines = []
            cur_state = 'inshared'

        elif line_dict['kind'] == 'endoffile':
            print('Reached end of file')

        else:
            print('ERROR: unexpected line', line)

    print_parsed(filepath, data)
    return data
    


def print_parsed(filepath, data):
    print('Parsed version of', filepath)
    print('sequence:', data['sequence'])
    unused_seq_ids = set(data['chunks'].keys()) - set(data['sequence'])
    if unused_seq_ids:
        print('WARNING: unused sequence ids = ', unused_seq_ids)
    for seq_id in data['sequence']:
        print(seq_id)
        lines = data['chunks'][seq_id]
        print(''.join(lines))


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

SHARED_TEMPLATE = """
\\vspace{0.2cm}
%s
\\vspace{0.3cm}
"""

def wrap_left_column(text):
    return LEFT_COLUMN_TEMPLATE % text

def wrap_right_column(text):
    return RIGHT_COLUMN_TEMPLATE % text

def wrap_shared(text):
    return SHARED_TEMPLATE % text

PARCOL_TEMPLATE = """
\\begin{paracol}{2}
%s

%s
\\end{paracol}
"""


def wrap_parcol(left_col, right_col):
    return PARCOL_TEMPLATE % (left_col, right_col)

def mkparcol():
    left_data = parse_tex_source(LEFT_SOURCE_FILE)    
    right_data = parse_tex_source(RIGHT_SOURCE_FILE)
    print('writing bilingual output file ', PARCOL_OUT_FILE)
    outf = open(PARCOL_OUT_FILE, 'w')
    
    for seq_id in left_data['sequence']:
        if 'SHARED' in seq_id:
            left_lines = left_data['chunks'][seq_id]
            text = ''.join(left_lines)
            text = wrap_shared(text)
            outf.write(text)

        elif 'PAR' in seq_id:
            left_lines = left_data['chunks'][seq_id]
            left_text = ''.join(left_lines)
            fr_text = wrap_par_text(left_text, 'french')
            left_col = wrap_left_column(fr_text)
            
            right_lines = right_data['chunks'][seq_id]
            right_text = ''.join(right_lines)
            en_text = wrap_par_text(right_text, 'english')
            right_col = wrap_right_column(en_text)
            
            outf.write(wrap_parcol(left_col, right_col))

    outf.close()


if __name__ == '__main__':
    mkparcol()
