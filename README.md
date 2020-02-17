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


