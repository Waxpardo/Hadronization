# Release metadata status

**Release state: PUBLIC-BLOCKED.** This file records missing owner decisions; it
does not make them.

The publication exporter requires this file, `CITATION.cff`, the figure
acceptance manifest, and the manuscript build record to be present in the
selected export. While the release is blocked, it also requires the visible
`PUBLIC-BLOCKED MANUSCRIPT` marker in both TeX source and extracted PDF text.
Removing a marker or omitting a record is a hard failure, not a status change.

No P1--P8 role can be exported as accepted from a manifest status alone. Each
accepted role requires a checksum-bound
`results/provenance/figure_receipts/P<role>.json` v1 receipt, local selected
evidence for producer, configuration, selector, central inputs, all 30
tune/block cells, numerical sources, unique canonical outputs, exact ROOT and
PYTHIA identities, and clean visual and scientific reviews. No such receipt is
present in this blocked checkout.

## Authorship and contributors

The synchronized manuscript currently displays this draft order:

| draft position | displayed name |
|---:|---|
| 1 | I. Pardo Zambrana |
| 2 | P. Veen |
| 3 | K. Vos |
| 4 | P. Christakoglou |

`CITATION.cff` copies the existing draft order so citation tooling has a
parseable, visibly provisional record. The owner has not approved the author
list, order, affiliations, identifiers, contributor roles, corresponding
author, or acknowledgements. Owner approval must precede release.

The candidate closure publishes no personal email address. We omit ORCID and
affiliation fields instead of inferring them.

## Citation and release identity

The repository has no DOI, archived release identifier, release version, or
public data accession. The CFF message states this draft status. A release must
replace the provisional message only after the owner approves the citation and
an archive binds it to an exact source commit.

## License

The owner has not selected software, documentation, data, or figure licences.
This task adds no `LICENSE` file. In the absence of an explicit licence, this
repository grants no general reuse permission. Owner selection and
documentation of the applicable licences remain a release blocker.

## Third-party material

The candidate PUBLIC closure includes bibliographic metadata and project-owned
source and evidence. It excludes the ignored historical paper directory, local
literature files, the third-party writing standard PDF, and generated scratch
collections. Publication still requires the owner to confirm rights for every
accepted future figure and any journal style files added later.
