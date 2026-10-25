# Makefile for AegisMed Research Paper (ACM CHIL / MICCAI draft)

TARGET = main
SRC = main.tex references.bib

all: $(TARGET).pdf

$(TARGET).pdf: $(SRC)
	@if command -v tectonic >/dev/null 2>&1; then \
		echo "Compiling with tectonic..."; \
		tectonic -X compile $(TARGET).tex; \
	elif command -v pdflatex >/dev/null 2>&1; then \
		echo "Compiling with pdflatex/bibtex..."; \
		pdflatex $(TARGET); \
		bibtex $(TARGET); \
		pdflatex $(TARGET); \
		pdflatex $(TARGET); \
	else \
		echo "Error: Neither tectonic nor pdflatex found on PATH."; \
		exit 1; \
	fi
	@echo "Build successful: $(TARGET).pdf"

clean:
	rm -f *.aux *.bbl *.blg *.log *.out *.toc *.synctex.gz *.bcf *.run.xml

.PHONY: all clean
