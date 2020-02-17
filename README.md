# paralleletex
Tools for generating two-column format bilingual texts for language learning.

TODO:

  - [ ] implement exact match on labels
  - [ ] implement fuzzy match on displaymath contents
    ```python
    dm = list(doc.find_all('displaymath'))[0]
    list(dm.contents)[0].strip()
    ```

### Install

    virtualenv -p python3.7 venv
    source venv/bin/activate
    pip install -r requirements.txt


### Extracting source

  - Use `latexpand` to get the entire document as a single file (in case)
  - Delete the header and footer to leave only tex source of the document env
    (after \begin{document} and before \end{document})


### Run

    ./mkparalleltext.py --left=thesection.tex --right=lasection.tex --out=bilingual.tex
    pdflatex bilingual.tex


### Examples


    ./mkparalleltext.py \
        --left    examples/sections/11_solving_equations_FR.tex \
        --right   examples/sections/11_solving_equations_EN.tex \
        --outpath examples/sections/11_solving_equations_parcols.tex

    ./mkparalleltext.py \
        --left    examples/sections/12_numbers_FR.tex \
        --right   examples/sections/12_numbers_EN.tex \
        --outpath examples/sections/12_numbers_parcols.tex

    ./mkparalleltext.py \
        --left    examples/sections/13_number_representations_FR.tex \
        --right   examples/sections/13_number_representations_EN.tex \
        --outpath examples/sections/13_number_representations_parcols.tex


    ./mkparalleltext.py \
        --left=   examples/sections/14_variables_FR.tex \
        --right   examples/sections/14_variables_EN.tex \
        --outpath examples/sections/14_variables_parcols.tex


13_number_representations_FR.tex