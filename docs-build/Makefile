# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
PAPER         =

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d ../docs/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .

.PHONY: help clean html web pickle htmlhelp latex changes linkcheck

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  html      to make standalone HTML files"
	@echo "  pickle    to make pickle files"
	@echo "  json      to make JSON files"
	@echo "  htmlhelp  to make HTML files and a HTML help project"
	@echo "  latex     to make LaTeX files, you can set PAPER=a4 or PAPER=letter"
	@echo "  changes   to make an overview over all changed/added/deprecated items"
	@echo "  linkcheck to check all external links for integrity"

clean:
	-rm -rf ../docs/*

html:
	mkdir -p ../docs/html ../docs/doctrees
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) ../docs/html
	@echo
	@echo "Build finished. The HTML pages are in ../docs/html."

pickle:
	mkdir -p ../docs/pickle ../docs/doctrees
	$(SPHINXBUILD) -b pickle $(ALLSPHINXOPTS) ../docs/pickle
	@echo
	@echo "Build finished; now you can process the pickle files."

web: pickle

json:
	mkdir -p ../docs/json ../docs/doctrees
	$(SPHINXBUILD) -b json $(ALLSPHINXOPTS) ../docs/json
	@echo
	@echo "Build finished; now you can process the JSON files."

htmlhelp:
	mkdir -p ../docs/htmlhelp ../docs/doctrees
	$(SPHINXBUILD) -b htmlhelp $(ALLSPHINXOPTS) ../docs/htmlhelp
	@echo
	@echo "Build finished; now you can run HTML Help Workshop with the" \
	      ".hhp project file in ../docs/htmlhelp."

latex:
	mkdir -p ../docs/latex ../docs/doctrees
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS) ../docs/latex
	@echo
	@echo "Build finished; the LaTeX files are in ../docs/latex."
	@echo "Run \`make all-pdf' or \`make all-ps' in that directory to" \
	      "run these through (pdf)latex."

changes:
	mkdir -p ../docs/changes ../docs/doctrees
	$(SPHINXBUILD) -b changes $(ALLSPHINXOPTS) ../docs/changes
	@echo
	@echo "The overview file is in ../docs/changes."

linkcheck:
	mkdir -p ../docs/linkcheck ../docs/doctrees
	$(SPHINXBUILD) -b linkcheck $(ALLSPHINXOPTS) ../docs/linkcheck
	@echo
	@echo "Link check complete; look for any errors in the above output " \
	      "or in ../docs/linkcheck/output.txt."
