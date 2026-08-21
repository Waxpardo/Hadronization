#!/usr/bin/env python3
"""Project a v3 merged directory's species closure and group it by category.

WHAT THIS IS. The first extraction layer over v3 merged output: it reads
`hFlavourClosureSpecies` (the 202-bin species axis) out of every pair file in a
merged directory, groups the ordinals by the category column of
`AnalysisScripts/species_ordinals_v2.json`, and emits the per-species and
per-category tables the paper's decomposition needs.

WHY IT CARRIES ITS OWN SELF-CHECK, and why that check is the point. The species
table's `category` column and the analysis's 6-bin `heavyStateCategory` axis are
computed independently -- the column by
`Hadronization::ClassifyHeavyStateDetailed` at table-generation time, the axis by
the analysis macro at fill time. So summing the 202 species bins into 6 category
groups MUST reproduce `hFlavourClosure`'s own 6-bin projection, bin for bin. If
it does not, one of the two is wrong and no decomposition built on either can be
trusted. This is the same cross-check pattern the gate and the commensurability
run use, moved into the extraction layer.

FAIL-CLOSED, on two conditions:

  - **Digest.** Every pair file carries `species_ordinal_digest` as a TObjString.
    It must equal the artifact's `table_digest_fnv1a64`. A mismatch means the
    file was written against a different ordinal table and its axis indices mean
    something else.
  - **Unknown ordinals.** The table is the complete admissible set and the axis
    has no overflow bin by design (`unmapped_policy:
    fail_closed_no_overflow_bin`) -- an overflow bin is how 152 species became
    invisible in the first place. A filled bin outside 0..201 is a hard error.

SEMs ARE NOT COMPUTED HERE, deliberately. The block SEMs the paper needs come
from the spread across the ten deterministic blocks per tune. One merged
directory is one number per bin, and a "SEM" from it would be fabricated. The
wiring is stubbed (`--blocks`) and errors out until ten block directories exist.

Usage:
  extraction/extract_species_decomposition.py MERGED_DIR [--out DIR] [--root ROOTBIN]
  extraction/extract_species_decomposition.py MERGED_DIR --blocks B1 B2 ... B10
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ARTIFACT = REPO / "AnalysisScripts/species_ordinals_v2.json"
REGISTRY = REPO / "config/heavy_flavour_pair_registry_v1.json"

PROJECT_MACRO = r"""
void proj(const char* dir, const char* outCsv){
  TSystemDirectory d("d", dir);
  TList* files = d.GetListOfFiles();
  if(!files){ printf("PROJ_ERROR no listing\n"); return; }
  FILE* out = fopen(outCsv, "w");
  fprintf(out, "pair,kind,bin,content\n");
  TIter next(files); TSystemFile* fo; long np=0;
  while((fo=(TSystemFile*)next())){
    TString nm = fo->GetName();
    if(fo->IsDirectory() || !nm.EndsWith(".root")) continue;
    TFile* f = TFile::Open(TString::Format("%s/%s", dir, nm.Data()));
    if(!f || f->IsZombie()) { printf("PROJ_ERROR open %s\n", nm.Data()); continue; }
    TObjString* dg = (TObjString*)f->Get("species_ordinal_digest");
    fprintf(out, "%s,digest,0,%s\n", nm.Data(), dg ? dg->GetString().Data() : "MISSING");
    THnSparse* hs = (THnSparse*)f->Get("hFlavourClosureSpecies");
    THnSparse* hc = (THnSparse*)f->Get("hFlavourClosure");
    if(hs){
      int last = hs->GetNdimensions()-1;
      TH1D* p = hs->Projection(last);
      for(int b=1;b<=p->GetNbinsX();++b){
        double v=p->GetBinContent(b);
        if(v!=0.0) fprintf(out, "%s,species,%d,%.17g\n", nm.Data(), b-1, v);
      }
      delete p;
    } else fprintf(out, "%s,species,-1,MISSING\n", nm.Data());
    if(hc){
      int last = hc->GetNdimensions()-1;
      TH1D* p = hc->Projection(last);
      for(int b=1;b<=p->GetNbinsX();++b)
        fprintf(out, "%s,category,%d,%.17g\n", nm.Data(), b-1, p->GetBinContent(b));
      delete p;
    } else fprintf(out, "%s,category,-1,MISSING\n", nm.Data());
    f->Close(); ++np;
  }
  fclose(out);
  printf("PROJ_DONE pairs=%ld\n", np);
}
"""


def load_table(artifact: Path) -> tuple[dict[int, int], dict[int, str], str]:
    payload = json.loads(artifact.read_text())
    ordinal_to_category: dict[int, int] = {}
    # Index -> name for ALL six categories, taken from category_counts' key
    # order, which is the enum order. Deriving it only from observed species
    # would leave the empty categories unnamed -- kHiddenHeavy and
    # kOtherNoncentral have zero members in the table, and a decomposition
    # table that silently omits a category is exactly the failure mode the
    # no-overflow-bin rule exists to prevent.
    category_names: dict[int, str] = {
        index: name for index, name in enumerate(payload["category_counts"])
    }
    for row in payload["species"]:
        ordinal_to_category[int(row["ordinal"])] = int(row["category"])
        declared = category_names.get(int(row["category"]))
        if declared != row["category_name"]:
            raise SystemExit(
                f"FAIL-CLOSED: category index {row['category']} is "
                f"{row['category_name']!r} on ordinal {row['ordinal']} but "
                f"{declared!r} by category_counts order"
            )
    return ordinal_to_category, category_names, payload["table_digest_fnv1a64"]


def load_registry(registry: Path) -> tuple[dict[str, int], dict[int, str]]:
    """filename -> trigger PDG, and trigger PDG -> sector, from the signed registry.

    This is what makes trigger-level deduplication possible at all: the closure
    histograms are TRIGGER-owned, and only the registry says which trigger a
    given pair file belongs to.
    """
    payload = json.loads(registry.read_text())
    trigger_of: dict[str, int] = {}
    sector_of: dict[int, str] = {}
    for row in payload["pairs"]:
        trigger_of[str(row["filename"])] = int(row["trigger_pdg"])
        sector_of[int(row["trigger_pdg"])] = str(row["sector"])
    if len(trigger_of) != int(payload["pair_count"]):
        raise SystemExit(
            f"FAIL-CLOSED: registry declares pair_count={payload['pair_count']} "
            f"but carries {len(trigger_of)} distinct filenames"
        )
    return trigger_of, sector_of


def deduplicate_by_trigger(
    per_file: dict[str, dict[int, float]],
    filenames: set[str],
    trigger_of: dict[str, int],
    kind: str,
) -> tuple[dict[int, float], dict[int, int]]:
    """Sum each TRIGGER's closure exactly once, not once per pair file.

    WHY THIS EXISTS -- the defect it corrects. `hFlavourClosure` and
    `hFlavourClosureSpecies` are owned by the TRIGGER, not by the pair: the
    analysis builds one accumulator per distinct trigger PDG and then writes
    that same object into every pair file sharing that trigger
    (`analysis/status_analysis_THnSparse_qq.C`, the per-pair write loop). In the
    committed 300-pair registry each charm trigger is copied into 24 files and
    each beauty trigger into 26. Summing every file therefore counted every
    charm trigger 24 times and every beauty trigger 26 times -- a
    registry-weighted replication, not a physical total. Because the replication
    factor differs by sector it does NOT cancel in any cross-sector quantity:
    it inflated the total by ~24.2x and biased the charm/beauty split by
    +0.74 pp. See private error-ledger entry E5.

    FAIL-CLOSED ON DISAGREEMENT. Copies of one trigger's closure must be
    bit-identical, because they are literally the same in-memory object written
    N times. If two files carrying the same trigger disagree in any bin, the
    premise of deduplication is broken -- the histograms are not copies -- and
    picking either one would be a guess. That is a hard error, never a warning.
    """
    by_trigger: dict[int, dict[int, float]] = {}
    source_of: dict[int, str] = {}
    copies: dict[int, int] = defaultdict(int)
    for name in sorted(filenames):
        if name not in trigger_of:
            raise SystemExit(
                f"FAIL-CLOSED: {name} is not in the registry, so its trigger is "
                "unknown and its closure cannot be deduplicated"
            )
        trigger = trigger_of[name]
        bins = per_file.get(name, {})
        copies[trigger] += 1
        if trigger not in by_trigger:
            by_trigger[trigger] = bins
            source_of[trigger] = name
            continue
        first = by_trigger[trigger]
        if bins != first:
            differing = sorted(
                b for b in set(bins) | set(first)
                if bins.get(b, 0.0) != first.get(b, 0.0)
            )
            example = differing[0]
            raise SystemExit(
                f"FAIL-CLOSED: trigger {trigger} carries non-identical {kind} "
                f"closures. {source_of[trigger]} and {name} differ in "
                f"{len(differing)} bin(s); bin {example} is "
                f"{first.get(example, 0.0)!r} vs {bins.get(example, 0.0)!r}. "
                "These are supposed to be copies of one trigger-owned object; "
                "deduplication is not valid if they are not."
            )

    total: dict[int, float] = defaultdict(float)
    for trigger, bins in by_trigger.items():
        for b, value in bins.items():
            total[b] += value
    return total, dict(copies)


def load_decay_grouping(decay_map: Path, artifact: Path):
    """Experiment-comparable grouping: chain each species to the observable it feeds.

    THE SECOND CONVENTION. The category column groups by DIQUARK STRUCTURE -- what
    the species is. An experiment cannot see that; it reconstructs whatever the
    species decays into. So this walks each species' dominant channel to its
    terminal heavy descendant, which is the ground state a detector would
    actually count.

    WHERE IT STOPS, AND WHY THAT IS NOT A DEFECT. PYTHIA parametrises the weak
    decays of baryons it has no exclusive table for at the QUARK level -- the
    dominant channel of the doubly-heavy states is literally `[-2, 1, 4, 81]`,
    i.e. u-bar d c plus a string placeholder. There is no hadron-level daughter
    to follow, so those species terminate at themselves and are reported as
    UNMAPPED rather than being forced into a group they do not belong to. The
    reader states their weight explicitly; silently folding them into a
    ground-state bin is exactly the kind of invisible reallocation the
    no-overflow-bin rule exists to prevent.
    """
    dmap = json.loads(decay_map.read_text())
    art = json.loads(artifact.read_text())
    if dmap["ordinal_table_digest_fnv1a64"] != art["table_digest_fnv1a64"]:
        raise SystemExit(
            "FAIL-CLOSED: decay map was built against ordinal digest "
            f"{dmap['ordinal_table_digest_fnv1a64']}, artifact is "
            f"{art['table_digest_fnv1a64']}"
        )
    pdg_to_ord = {int(r["pdg"]): int(r["ordinal"]) for r in art["species"]}
    cat_name = {int(r["ordinal"]): r["category_name"] for r in art["species"]}
    name = {int(s["ordinal"]): s["name"] for s in dmap["species"]}
    by_ord = {int(s["ordinal"]): s for s in dmap["species"]}

    def heavy_daughter(entry):
        for product in entry["dominant_products"]:
            if product in pdg_to_ord:
                return pdg_to_ord[product]
        return None

    terminal: dict[int, int] = {}
    for ordinal in sorted(by_ord):
        seen, current = set(), ordinal
        while current not in seen:
            seen.add(current)
            nxt = heavy_daughter(by_ord[current])
            if nxt is None or nxt == current:
                break
            current = nxt
        terminal[ordinal] = current

    label: dict[int, str] = {}
    for ordinal, term in terminal.items():
        if cat_name[term] == "kCentralGround":
            label[ordinal] = f"{name[term]} ({term})"
        else:
            label[ordinal] = f"UNMAPPED/{cat_name[term]}"
    return label


def preflight(merged: Path, expected: set[str]) -> None:
    """The directory must hold EXACTLY the registry's filenames. No more, no less.

    Counting `*.root` and comparing to 300 is not the same test: a directory
    with 299 correct files and one stray copy also counts 300.
    """
    if not merged.is_dir():
        raise SystemExit(f"FAIL-CLOSED: {merged} is not a directory")
    present = {p.name for p in merged.glob("*.root")}
    missing, extra = sorted(expected - present), sorted(present - expected)
    if missing or extra:
        raise SystemExit(
            "FAIL-CLOSED: the merged directory is not the registry's file set. "
            f"missing={len(missing)} {missing[:5]} "
            f"unexpected={len(extra)} {extra[:5]}"
        )


def project(merged: Path, root_bin: str, workdir: Path, expected: int) -> Path:
    """Project every pair file, and refuse to continue if any of them failed.

    THE DEFECT THIS CLOSES (review finding A5). The embedded macro logs
    `PROJ_ERROR` and CONTINUES when a file cannot be opened, and this reader
    only required the eventual `PROJ_DONE` marker. A directory holding all 300
    expected filenames, one of them corrupt, therefore passed the filename
    preflight, projected 299 files, agreed with itself on species-vs-category
    (both views lose the same file), and exited 0 with a quietly low total.

    So: any `PROJ_ERROR` is fatal, and the number of successfully projected
    files must equal the number expected -- not merely be non-zero.
    """
    macro = workdir / "proj.C"
    macro.write_text(PROJECT_MACRO)
    csv_path = workdir / "projection.csv"
    result = subprocess.run(
        [root_bin, "-l", "-b", "-q",
         f'{macro}("{merged}","{csv_path}")'],
        capture_output=True, text=True, check=False,
    )
    if "PROJ_DONE" not in result.stdout:
        sys.stderr.write(result.stdout[-4000:] + result.stderr[-4000:])
        raise SystemExit("projection failed: no PROJ_DONE")
    errors = [l for l in result.stdout.splitlines() if l.startswith("PROJ_ERROR")]
    if errors:
        raise SystemExit(
            f"FAIL-CLOSED: {len(errors)} PROJ_ERROR line(s) -- a file was "
            f"skipped, and a skipped file is invisible to every downstream "
            f"self-check. first={errors[0]!r}"
        )
    done = [l for l in result.stdout.splitlines() if l.startswith("PROJ_DONE")][0]
    projected = int(done.split("pairs=")[1].strip())
    if projected != expected:
        raise SystemExit(
            f"FAIL-CLOSED: projected {projected} pair files, expected exactly "
            f"{expected}"
        )
    sys.stderr.write(done + "\n")
    return csv_path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("merged", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--root-bin", default="root")
    ap.add_argument("--artifact", type=Path, default=ARTIFACT,
                    help="species_ordinals_v2.json; defaults to the repo copy")
    ap.add_argument("--registry", type=Path, default=REGISTRY,
                    help="heavy_flavour_pair_registry_v1.json; defaults to the "
                         "repo copy. Required to deduplicate the TRIGGER-owned "
                         "closure histograms, which the analysis writes into "
                         "every pair file sharing that trigger (E5)")
    ap.add_argument("--decay-map", type=Path, required=True,
                    help="decay-parent map for the experiment-comparable grouping; "
                         "REQUIRED and deliberately without a default -- the old "
                         "default was the excluded historical v1 map, which does not "
                         "conjugate antiparticle decays (private error-ledger entry E1)")
    ap.add_argument("--blocks", nargs="*", default=None,
                    help="ten block directories; SEM wiring, not yet implemented")
    args = ap.parse_args()

    if args.blocks is not None:
        raise SystemExit(
            "block SEMs are not implemented and must not be faked: they require "
            "the spread across the ten deterministic blocks per tune, which do "
            "not exist until the full merge lands. Re-run without --blocks."
        )

    # The decay map is REQUIRED, so a path that does not exist is a typo, not a
    # licence to skip the second convention. The grouping used to be skipped
    # silently -- a mistyped path produced a successful, map-free extraction
    # that looked like a complete one (review finding A5).
    if not args.decay_map.exists():
        raise SystemExit(
            f"FAIL-CLOSED: --decay-map {args.decay_map} does not exist. The "
            f"experiment-comparable grouping is not optional; a missing map is "
            f"a bad path, not a reason to emit a partial extraction."
        )

    ordinal_to_category, category_names, want_digest = load_table(args.artifact)
    trigger_of, sector_of = load_registry(args.registry)
    preflight(args.merged, set(trigger_of))
    out_dir = args.out or (args.merged.parent / "extraction")
    out_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        csv_path = project(args.merged, args.root_bin, Path(tmp),
                           expected=len(trigger_of))
        rows = list(csv.DictReader(csv_path.open()))

    # ---- per-FILE accumulation; the summing happens after deduplication -----
    per_file_species: dict[str, dict[int, float]] = defaultdict(dict)
    per_file_category: dict[str, dict[int, float]] = defaultdict(dict)
    digests: set[str] = set()
    pairs: set[str] = set()
    unknown: list[tuple[str, int]] = []

    for row in rows:
        pair, kind, b = row["pair"], row["kind"], int(row["bin"])
        pairs.add(pair)
        if kind == "digest":
            digests.add(row["content"])
            continue
        if row["content"] == "MISSING":
            raise SystemExit(f"FAIL-CLOSED: {pair} is missing its {kind} object")
        value = float(row["content"])
        if kind == "species":
            if b not in ordinal_to_category:
                unknown.append((pair, b))
                continue
            per_file_species[pair][b] = value
        elif kind == "category":
            if value != 0.0:
                per_file_category[pair][b] = value

    # ---- TRIGGER-LEVEL DEDUPLICATION (the E5 correction) -------------------
    species_tot, species_copies = deduplicate_by_trigger(
        per_file_species, pairs, trigger_of, "species")
    category_tot, _ = deduplicate_by_trigger(
        per_file_category, pairs, trigger_of, "category")
    grouped_tot: dict[int, float] = defaultdict(float)
    for ordinal, value in species_tot.items():
        grouped_tot[ordinal_to_category[ordinal]] += value

    # ---- fail-closed conditions ------------------------------------------
    if digests != {want_digest}:
        raise SystemExit(
            f"FAIL-CLOSED: species_ordinal_digest mismatch. artifact={want_digest} "
            f"files={sorted(digests)}"
        )
    if unknown:
        raise SystemExit(
            f"FAIL-CLOSED: {len(unknown)} filled species bins outside the table "
            f"(no overflow bin by design). first={unknown[:5]}"
        )

    # ---- THE SELF-CHECK ---------------------------------------------------
    checks = []
    worst = 0.0
    for category in sorted(set(grouped_tot) | set(category_tot)):
        g, c = grouped_tot.get(category, 0.0), category_tot.get(category, 0.0)
        denominator = max(abs(g), abs(c), 1e-30)
        rel = abs(g - c) / denominator
        worst = max(worst, rel)
        checks.append((category, category_names.get(category, "?"), g, c, g - c, rel))

    verdict = "AGREE" if worst < 1e-9 else "DISAGREE"

    # ---- SECOND CONVENTION: experiment-comparable, via F4's decay-parent map --
    # The map is mandatory and its existence was enforced before any projection
    # ran, so there is no longer a SKIPPED branch: this grouping always happens.
    decay_label = load_decay_grouping(args.decay_map, args.artifact)
    decay_tot: dict[str, float] = defaultdict(float)
    for ordinal, value in species_tot.items():
        decay_tot[decay_label[ordinal]] += value
    # THE INVARIANCE CHECK. Regrouping moves weight between bins; it cannot
    # create or destroy it. Both groupings must sum to the ungrouped species
    # total EXACTLY -- not to tolerance. Any deviation is a bug by
    # construction, so this is an item-STOP rather than a warning.
    ungrouped = sum(species_tot.values())
    by_category = sum(grouped_tot.values())
    by_decay = sum(decay_tot.values())
    if by_category != ungrouped or by_decay != ungrouped:
        raise SystemExit(
            "FAIL-CLOSED: regrouping did not conserve weight. "
            f"ungrouped={ungrouped!r} by_category={by_category!r} "
            f"by_decay={by_decay!r}"
        )
    decay_verdict = "CONSERVED"
    decay_rows = sorted(decay_tot.items(), key=lambda kv: -abs(kv[1]))

    # ---- outputs -----------------------------------------------------------
    with (out_dir / "per_species.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["ordinal", "category", "category_name", "total"])
        for ordinal in sorted(species_tot):
            w.writerow([ordinal, ordinal_to_category[ordinal],
                        category_names[ordinal_to_category[ordinal]],
                        repr(species_tot[ordinal])])
    with (out_dir / "per_category.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["category", "category_name", "from_species", "from_closure",
                    "difference", "relative"])
        for row in checks:
            w.writerow([row[0], row[1], repr(row[2]), repr(row[3]),
                        repr(row[4]), repr(row[5])])

    print(f"EXTRACTION pairs={len(pairs)} triggers={len(species_copies)} "
          f"filled_species_ordinals={len(species_tot)} digest={want_digest}")
    by_sector: dict[str, set[int]] = defaultdict(set)
    for trigger, n in sorted(species_copies.items()):
        by_sector[sector_of[trigger]].add(n)
    print("DEDUPLICATION trigger-owned closures counted once each; "
          "replication in this directory: " + ", ".join(
              f"{sector} {sorted(counts)}x"
              for sector, counts in sorted(by_sector.items())))
    print(f"{'cat':>4} {'name':<20} {'from species':>20} {'from closure':>20} {'rel':>10}")
    for category, name, g, c, _d, rel in checks:
        print(f"{category:>4} {name:<20} {g:>20.10g} {c:>20.10g} {rel:>10.2e}")
    print(f"SELF_CHECK {verdict} worst_relative={worst:.3e}")
    if decay_rows:
        total = sum(v for _, v in decay_rows)
        unmapped = sum(v for k, v in decay_rows if k.startswith("UNMAPPED/"))
        print()
        print("EXPERIMENT-COMPARABLE grouping (F4 decay-parent map), top 12:")
        print(f"{'observable':<28} {'weight':>18} {'share %':>9}")
        for k, v in decay_rows[:12]:
            print(f"{k:<28} {v:>18.10g} {100.0*v/total:>9.4f}")
        if len(decay_rows) > 12:
            print(f"  ... {len(decay_rows)-12} more groups")
        print(f"UNMAPPED (quark-level dominant channel): {unmapped:.10g} "
              f"= {100.0*unmapped/total:.6f} %")
        print(f"INVARIANCE {decay_verdict} "
              f"(both groupings sum exactly to the ungrouped species total)")
        with (out_dir / "per_observable.csv").open("w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["observable", "total", "share_pct"])
            for k, v in decay_rows:
                w.writerow([k, repr(v), repr(100.0 * v / total)])
    print(f"SEM: not computed -- requires ten block directories per tune "
          f"(stub only; --blocks refuses)")
    print(f"wrote {out_dir}/per_species.csv and {out_dir}/per_category.csv")
    return 0 if verdict == "AGREE" else 3


if __name__ == "__main__":
    raise SystemExit(main())
