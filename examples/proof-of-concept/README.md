Proof of concept
================
POC section in FR (left column) and EN (right column). 

### Files

  - `11_solving_equationsEN.tex`: manually annotated vEN
  - `11_solving_equationsFR.tex`: manually annotated vFR
  - `11_solving_equations_FR_en.tex`: output of `mkparcol.py`
  - `11_solving_equations_main.tex`: main file to compile
  - `minireference_FR.hdr.tex` headers from the book
  - `mkparcol.py` generator based on manual annotatoins


Notes:
 - Earlier tried version where equations were "shared" (displayed in the middle),
   but it was too difficult to read since reader's eyes would have to jump around.
   Equations can still be used to find parallel structure, but prefer two columns
   for everything.


### TODOs (Sept 15 2019)

  - Parse latex
  - Automartically find matchin PAR and SHARED
