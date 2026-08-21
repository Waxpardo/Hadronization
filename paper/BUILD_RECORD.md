# Manuscript build record

**Release state:** `PUBLIC-BLOCKED`

**Build date:** 2026-08-21

**Figure acceptance:** 0 accepted outputs out of P1--P8

## Source closure

The synchronized source package consists of:

- `hfBalancingModelPaper.tex`;
- `Introduction.tex`;
- `Observables.tex`;
- `Model.tex`;
- `Results.tex`;
- `Summary.tex`;
- `references.bib`;
- `CLAIM_EVIDENCE.md`; and
- this build record.

The TeX recorder reported only those six TeX sources, the reconciled
bibliography generated through BibTeX, and standard TeX Live files. There are
no `includegraphics` dependencies, custom journal styles, historical-paper
files, data ROOT files, or internal explanatory SVGs in the build closure.

Git records the package at the requested lowercase `paper/` path. The
case-insensitive macOS work volume displays the physical parent with the
pre-existing `Paper/` spelling. The new top-level package is separate from,
and does not consume, the ignored historical
`Paper/Heavy_flavour_hadronisation_model_paper/` tree.

## Clean build

The latest hygiene build ran in a newly created disposable directory that was
removed on completion. The build copied the seven TeX/BibTeX input files there
before running exactly:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error hfBalancingModelPaper.tex
```

Toolchain:

- latexmk 4.88;

- pdfTeX 3.141592653-2.6-1.40.29 (TeX Live 2026);

- BibTeX 0.99e (TeX Live 2026); and

- the standard `article`, `fontenc`, `inputenc`, `lmodern`, `geometry`,
  `amsmath`, `booktabs`, `float`, `microtype`, `tabularx`, `xcolor`, `url`, and
  `hyperref` packages.

The final LaTeX log and BibTeX log contain no warnings, undefined citations,
undefined references, multiply defined labels, underfull boxes, or overfull
boxes.

## Latest disposable build

The synchronized sources were rebuilt in a disposable directory on 2026-08-21:

- SHA-256: `bcd693641512ab9134258e6c4a8737a910089f9da05a2293742a0cbe880c89ee`;
- size: 311,664 bytes;
- format: PDF 1.7, A4;
- pages: 8; and
- producer: pdfTeX 1.40.29.

The deterministic build completed with zero final LaTeX/BibTeX warnings,
undefined citations, or undefined references. `pdftotext` verified the visible
PUBLIC-BLOCKED marker. No PDF was retained or promoted, and no new page-by-page
visual review is claimed. The earlier seven-page visual review does not cover
this eight-page synchronized build.

As of the 2026-08-21 exporter remediation, a candidate artifact build also
checks this visible state in both the TeX source and extracted PDF text. The
figure manifest, this build record, public release metadata, and `CITATION.cff`
are mandatory export records. The standalone disposable TeX check above is not
a publication export. No publication artifact was retained because PYTHIA is
absent and the available ROOT 6.38.04 differs from the required 6.30.01.

## Unresolved release blockers

The paper remains PUBLIC-BLOCKED. The current blockers include:

- The authorized external central and ten-block products are unavailable in
  this checkout.

- Final scientific figure bytes and receipt sidecars are absent.

- The tune-dependent generator-hang selection risk is unbounded.

- The class-resolved S4 result is incomplete.

- The old current-validation render is not a current accepted output.

- The integrated-yield pair-count closure log is absent.

- Existing external pair-job sidecars have not been revalidated after the
  source-level v3 handshake repair.

- The corrected selector-bound harvest configurations have not been rerun on
  the external selected files, and historical renders are not current
  reproductions.

- Figure receipts, accepted bytes, and final numerical/visual reviews are
  absent; licensing, redistribution, and publication identity decisions are
  also unresolved.

In addition, `CITATION.cff` is explicitly provisional: the author order,
affiliations, persistent identifiers, acknowledgements, license, archive/DOI,
and release identity require owner approval. The PDF is a synchronized review
draft, not a release-ready article.
