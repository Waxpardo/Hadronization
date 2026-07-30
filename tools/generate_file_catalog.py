#!/usr/bin/env python3
"""Generate and mechanically verify the publication repository file catalog."""

from __future__ import annotations

import argparse
import hashlib
import mimetypes
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


AUTHORITATIVE_EXACT = {
    "setupEnv.sh",
    "runCondorJob.sh",
    "submit_full_production.sh",
    "submit_full_retry.sh",
    "submit_gate_b_pilots.sh",
    "submit_gate_b_analysis.sh",
    "run_status_analysis.sh",
    "submit_status_analysis.sh",
    "merge_root_files.sh",
    "make_subsamples.sh",
    "SimulationScripts/Makefile",
    "SimulationScripts/heavyflavourcorrelations_status.cpp",
    "SimulationScripts/HeavyFlavourUtils.h",
    "SimulationScripts/Sha256.h",
    "SimulationScripts/GeneratedHeavyFlavourRegistry.h",
    "SimulationScripts/GeneratedTuneSettingRegistry.h",
    "SimulationScripts/GeneratedWeakParentRegistry.h",
    "SimulationScripts/pythiasettings_Hard_Low_ccbb_MONASH.cmnd",
    "SimulationScripts/pythiasettings_Hard_Low_ccbb_JUNCTIONS.cmnd",
    "SimulationScripts/pythiasettings_Hard_Low_ccbb_CLOSEPACKING.cmnd",
    "AnalysisScripts/status_analysis_THnSparse_qq.C",
    "AnalysisScripts/AssociateOriginCategoryContract.h",
    "AnalysisScripts/GeneratedPairRegistry.h",
    "AnalysisScripts/MergeAnalysisObjects.C",
    "AnalysisScripts/MergeCanonicalAnalysis.C",
    "PlottingScripts/improvedPlotting_THnSparse.C",
    "PlottingScripts/HistogramErrorUtils.h",
    "PlottingScripts/MultiplicityBoundaryUtils.h",
    "PlottingScripts/PairInputSelectionUtils.h",
    "PlottingScripts/TunePlotStyle.h",
    "PlottingScripts/Plot_InclusiveKinematicSpectra_Raw.C",
    "PlottingScripts/Plot_MultiplicityDistribution_PercentileBoundaries.C",
    "PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse.json",
    "PlottingScripts/configuration_multiplicity_reduced_JUNCTIONS_THnSparse_complete_root.json",
    "PlottingScripts/run_paper_plots.sh",
    "tools/campaign_manifest.py",
    "tools/canonical_manifest.py",
    "tools/canonical_merge_contract.py",
    "tools/dataset_selector.py",
    "tools/final_plot_provenance.py",
    "tools/merged_pair_provenance.py",
    "tools/render_analysis_submit.py",
    "tools/render_gate_b_analysis_submit.py",
    "tools/render_production_submit.py",
    "tools/statistical_robustness.py",
    "tools/validate_analysis_outputs.py",
    "tools/validate_gate_b_analysis_outputs.py",
}

AUTHORITATIVE_PREFIXES = (
    "config/",
)

SUPPORT_PREFIXES = (
    "Validation/",
    "tests/",
    "tools/",
    "ValidationReports/",
)

LEGACY_PREFIXES = (
    "Balancing_and_Sampling/",
    "PlottingScripts/DpDmBpBm_ComparisonStudy/",
    "PlottingScripts/PtMultiplicity/",
    "PlottingScripts/FinalAnalysis/",
    "Plots/",
    "RootFiles/",
)

LEGACY_EXACT = {
    "runCondorJob_legacy.sh",
    "submitCondor_10M.sub",
    "submitCondor_hf_10M.sub",
    "submitCondor_hf_90M.sub",
    "submitCondor_hf_CLOSEPACKING_100M.sub",
    "update_submit_paths.sh",
}

GENERATED_SUFFIXES = {
    ".root",
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".eps",
    ".so",
    ".d",
    ".pcm",
}

STALE_NAMES = {".DS_Store"}


def tracked_paths(root: Path) -> list[str]:
    data = subprocess.check_output(["git", "-C", root, "ls-files", "-z"])
    paths = [item.decode() for item in data.split(b"\0") if item]
    if "REPOSITORY_FILE_CATALOG.md" not in paths:
        paths.append("REPOSITORY_FILE_CATALOG.md")
    return sorted(paths)


def index_blob(root: Path, relative: str) -> bytes:
    return subprocess.check_output(
        ["git", "-C", str(root), "cat-file", "blob", f":{relative}"]
    )


def is_text(relative: str, data: bytes) -> bool:
    if Path(relative).suffix.lower() in GENERATED_SUFFIXES:
        return False
    try:
        data.decode(errors="strict")
        return True
    except UnicodeDecodeError:
        return False


def file_type(path: Path) -> str:
    if path.name == "REPOSITORY_FILE_CATALOG.md":
        return "Markdown"
    suffix = path.suffix.lower()
    labels = {
        ".c": "ROOT/C++ macro",
        ".cc": "C++",
        ".cpp": "C++",
        ".h": "C++ header",
        ".hpp": "C++ header",
        ".py": "Python",
        ".sh": "shell",
        ".json": "JSON",
        ".md": "Markdown",
        ".txt": "text",
        ".tex": "LaTeX",
        ".bib": "BibTeX",
        ".cmnd": "PYTHIA card",
        ".sub": "HTCondor submit",
        ".root": "ROOT binary",
        ".pdf": "PDF",
        ".png": "PNG",
        ".eps": "EPS",
    }
    return labels.get(suffix, mimetypes.guess_type(path.name)[0] or "other")


def owner_and_stage(path: str) -> tuple[str, str]:
    if path.startswith("SimulationScripts/") or path in {
        "setupEnv.sh",
        "runCondorJob.sh",
        "submit_full_production.sh",
        "submit_full_retry.sh",
        "submit_gate_b_pilots.sh",
    }:
        return "production", "PYTHIA generation"
    if path.startswith("AnalysisScripts/") or path in {
        "run_status_analysis.sh",
        "submit_status_analysis.sh",
        "submit_gate_b_analysis.sh",
        "merge_root_files.sh",
        "make_subsamples.sh",
    }:
        return "analysis", "raw-to-pair reduction/merge"
    if path.startswith("PlottingScripts/") or path == "plotting_documentation.md":
        return "plotting", "pair inputs-to-figures"
    if path.startswith("Validation/") or path.startswith("tests/"):
        return "validation", "gates A-D"
    if path.startswith("run_publication_gate_") or path == (
        "resolve_publication_gate_b_signoff.sh"
    ):
        return "validation", "gates A-D"
    if path.startswith("tools/") or path.startswith("config/"):
        return "contracts", "manifest/configuration"
    if path.startswith("AnalyzedData/"):
        return "legacy data", "retained derived input"
    if path.startswith("Literature/"):
        return "paper support", "literature"
    if path.startswith("Balancing_and_Sampling/"):
        return "legacy analysis", "historical balancing"
    return "project documentation", "documentation/history"


def classify(path: str) -> tuple[str, str]:
    name = Path(path).name
    suffix = Path(path).suffix.lower()
    if name in STALE_NAMES:
        return "stale", "remove from future release after owner confirmation"
    if path.startswith("AnalyzedData/") or suffix in GENERATED_SUFFIXES:
        return "generated", "regenerate from its documented legacy/current producer"
    pending_review_configs = {
        "config/pdg_2025_species_reference_v1.json",
        "config/pthat_sensitivity_v1.json",
        "config/statistical_robustness_v1.json",
    }
    if path in pending_review_configs:
        return "support", "named scientific review before publication promotion"
    if path in AUTHORITATIVE_EXACT or path.startswith(AUTHORITATIVE_PREFIXES):
        return "authoritative", ""
    if path in LEGACY_EXACT or path.startswith(LEGACY_PREFIXES):
        return "legacy", "canonical manifest-driven production/analysis/plotting path"
    if (
        "legacy" in path.lower()
        or path.startswith("submitCondor")
        or Path(path).name
        in {
            "improvedPlotting.C",
            "combinedCanvasPlots.C",
            "B_Balancing_GeneralPlotting.C",
            "PlottingWizard.C",
        }
    ):
        return "legacy", "current files named in REPRODUCIBILITY.md"
    if path.startswith("AnalysisScripts/") and not path.endswith(
        "Analysis_README.md"
    ):
        return "legacy", "AnalysisScripts/status_analysis_THnSparse_qq.C"
    if path == "SimulationScripts/Simulation_README.md":
        return "support", ""
    if path.startswith("SimulationScripts/"):
        return "legacy", "SimulationScripts/heavyflavourcorrelations_status.cpp"
    if path.startswith("PlottingScripts/"):
        support_names = {
            "README.md",
            "PAPER_FIGURE_PROVENANCE.md",
            "HistogramErrorUtils.h",
            "ListHistos.C",
            "Plot_KinematicSpectra_THnSparse.C",
            "Validate_THnSparse_Production.C",
            "validate_thnsparse_inputs.sh",
            "validate_plot_inputs.py",
            "validate_subsample_log.py",
            "summarize_subsample_coverage.py",
        }
        if Path(path).name not in support_names and not path.startswith(
            "PlottingScripts/validation/"
        ):
            return "legacy", "PlottingScripts/improvedPlotting_THnSparse.C"
    if path.startswith(SUPPORT_PREFIXES):
        return "support", ""
    return "support", ""


def purpose(path: str, status: str, owner: str) -> str:
    name = Path(path).name
    if status == "generated":
        return f"retained generated {file_type(Path(path)).lower()} artifact"
    if status == "legacy":
        return f"retained compatibility/history file for {owner}"
    if name.endswith("README.md") or name in {
        "README.md",
        "REPRODUCIBILITY.md",
        "plotting_documentation.md",
        "PUBLICATION_READY_CODING_AGENT_INSTRUCTIONS.md",
    }:
        return "operational or scientific documentation"
    if path.startswith("tests/") or path.startswith("Validation/"):
        return "executable validation or audit"
    if path.startswith("config/"):
        return "machine-readable scientific/workflow contract"
    if path.startswith("tools/"):
        return "deterministic generation, manifest, or validation utility"
    if owner == "production":
        return "canonical event generation component"
    if owner == "analysis":
        return "canonical one-pass analysis or merge component"
    if owner == "plotting":
        return "paper plotting component or documentation"
    return "project support file"


def validation_for(path: str, status: str, owner: str) -> str:
    if status == "authoritative":
        return {
            "production": "Gate A build/unit + Gate B raw validation",
            "analysis": "Gate D pair/output/merge validators",
            "plotting": "Gate A ACLiC + Gate D smoke/strict log audit",
            "contracts": "registry/manifest/dataset-selector tests",
        }.get(owner, "Gate A-D review")
    if status == "generated":
        return "checksum/provenance or visual validation; legacy artifacts may lack it"
    if status == "legacy":
        return "legacy regression only; excluded by canonical manifests/selector"
    return "documentation review or component-specific test"


def portability(path: str, status: str) -> str:
    if status == "generated":
        return "binary/data artifact; reproduce on Nikhef from recorded inputs"
    if path.endswith(".sub"):
        return "shared-filesystem paths; canonical files are rendered, legacy files fixed"
    if path.endswith(".json") or path.endswith(".md") or path.endswith(".py"):
        return "checkout-relative"
    return "local/Nikhef via HADRONIZATION_BASE and setupEnv.sh"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--output", type=Path, default=Path("REPOSITORY_FILE_CATALOG.md")
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output if args.output.is_absolute() else root / args.output
    paths = tracked_paths(root)
    if len(paths) != len(set(paths)):
        raise ValueError("duplicate tracked catalog path")

    blob_by_path: dict[str, bytes] = {}
    text_by_path: dict[str, str] = {}
    basename_to_paths: dict[str, list[str]] = defaultdict(list)
    for relative in paths:
        if relative != "REPOSITORY_FILE_CATALOG.md":
            data = index_blob(root, relative)
            blob_by_path[relative] = data
            if is_text(relative, data):
                text_by_path[relative] = data.decode(errors="replace")
        basename_to_paths[Path(relative).name].append(relative)

    rows = []
    counts: Counter[str] = Counter()
    for relative in paths:
        path = root / relative
        status, replacement = classify(relative)
        owner, stage = owner_and_stage(relative)
        counts[status] += 1
        references = []
        basename = Path(relative).name
        if len(basename_to_paths[basename]) == 1 and basename != relative:
            references = [
                candidate
                for candidate, text in text_by_path.items()
                if candidate != relative and basename in text
            ][:3]
        if not references:
            references = {
                "production": ["submit/render wrapper or campaign manifest"],
                "analysis": ["frozen manifest and run_status_analysis.sh"],
                "plotting": ["run_paper_plots.sh/configured canvas"],
                "validation": ["Gate A-D runner"],
                "contracts": ["production/analysis/plotting consumers"],
            }.get(owner, ["README/cited historical consumer"])
        paper = (
            "direct"
            if status == "authoritative" and owner in {"production", "analysis", "plotting"}
            else "methods/provenance"
            if status in {"authoritative", "support"}
            else "regression/history"
        )
        if relative == "REPOSITORY_FILE_CATALOG.md":
            size = "self"
            sha = "self"
        elif relative in blob_by_path:
            data = blob_by_path[relative]
            size = str(len(data))
            sha = hashlib.sha256(data).hexdigest()[:16]
        else:
            size = "missing"
            sha = "missing"
        rows.append(
            (
                relative,
                file_type(path),
                purpose(relative, status, owner),
                owner,
                "<br>".join(references),
                stage,
                paper,
                status,
                replacement or "—",
                validation_for(relative, status, owner),
                portability(relative, status),
                size,
                sha,
            )
        )

    authoritative_without_validation = [
        row[0] for row in rows if row[7] == "authoritative" and not row[9]
    ]
    if authoritative_without_validation:
        raise ValueError(
            f"authoritative files without validation: {authoritative_without_validation}"
        )

    untracked_notes = []
    protected_input_rows: list[tuple[str, int, str]] = []
    bibliography_relative = "Literature/References.bib"
    bibliography_path = root / bibliography_relative
    if bibliography_relative in blob_by_path and bibliography_path.is_file():
        worktree_bytes = bibliography_path.read_bytes()
        if worktree_bytes != blob_by_path[bibliography_relative]:
            bibliography_sha = hashlib.sha256(worktree_bytes).hexdigest()
            untracked_notes.append(
                f"- `{bibliography_relative}`: protected modified working "
                f"bibliography input ({len(worktree_bytes)} bytes, SHA-256 "
                f"`{bibliography_sha}`); excluded from index-derived catalog "
                "truth and from production/plotting commits."
            )
            protected_input_rows.append(
                (
                    bibliography_relative,
                    len(worktree_bytes),
                    bibliography_sha,
                )
            )
    paper = root / "Paper/Heavy_flavour_hadronisation_model_paper"
    if paper.is_dir():
        files = sorted(item for item in paper.rglob("*") if item.is_file())
        paper_digest = hashlib.sha256()
        paper_bytes = 0
        for item in files:
            relative = item.relative_to(paper).as_posix()
            data = item.read_bytes()
            paper_bytes += len(data)
            paper_digest.update(relative.encode())
            paper_digest.update(b"\0")
            paper_digest.update(str(len(data)).encode())
            paper_digest.update(b"\0")
            paper_digest.update(hashlib.sha256(data).hexdigest().encode())
            paper_digest.update(b"\n")
            protected_input_rows.append(
                (
                    (
                        "Paper/Heavy_flavour_hadronisation_model_paper/"
                        f"{relative}"
                    ),
                    len(data),
                    hashlib.sha256(data).hexdigest(),
                )
            )
        untracked_notes.append(
            f"- `Paper/Heavy_flavour_hadronisation_model_paper/`: protected "
            f"untracked working-paper tree ({len(files)} files, "
            f"{paper_bytes} bytes, path/size/content tree SHA-256 "
            f"`{paper_digest.hexdigest()}` at generation); scientific consumer "
            "of final figures; not staged or rewritten by this catalog."
        )
    campaigns = root / "campaigns"
    if campaigns.is_dir():
        untracked_notes.append(
            "- `campaigns/`: protected/untracked operational manifests in this "
            "worktree; stale raw-v2 material is not a canonical selector input."
        )

    lines = [
        "# Repository file catalog",
        "",
        "Generated mechanically by `tools/generate_file_catalog.py` and then "
        "subject to human architecture review. Every path from the Git index "
        "(`git ls-files`) is represented exactly once. Bytes, references, "
        "sizes, and checksums come from index blobs rather than the dirty "
        "worktree; binary files were inspected by type, size, and SHA-256 "
        "prefix.",
        "",
        f"- catalogued tracked paths: **{len(rows)}**",
        f"- unique catalog paths: **{len({row[0] for row in rows})}**",
        f"- status counts: **{dict(sorted(counts.items()))}**",
        "- authoritative files without a validation path: **0**",
        "- coverage result: **PASS**",
        "",
        "The status terms are defined in "
        "`PUBLICATION_READY_CODING_AGENT_INSTRUCTIONS.md`: authoritative, "
        "support, generated, legacy, stale, and deprecated. Generated legacy "
        "ROOT/plot files are not evidence of current provenance.",
        "",
        "## Intentional untracked operational inputs",
        "",
        *(untracked_notes or ["- None detected."]),
        "",
        "## Protected working-input ledger",
        "",
        (
            f"- accounted protected input files: "
            f"**{len(protected_input_rows)}**"
        ),
        "",
        "| Path | Bytes | SHA-256 |",
        "|---|---:|---|",
        *[
            "| `"
            + relative.replace("|", "\\|").replace("`", "\\`")
            + f"` | {size} | `{digest}` |"
            for relative, size, digest in protected_input_rows
        ],
        "",
        "## Complete ledger",
        "",
        "| Path | Type | Purpose | Owner | Callers/consumers | Stage | Paper | Status | Replacement | Validation | Portability | Bytes | SHA-256 prefix |",
        "|---|---|---|---|---|---|---|---|---|---|---|---:|---|",
    ]
    for row in rows:
        escaped = [str(value).replace("|", "\\|").replace("\n", " ") for value in row]
        escaped[0] = f"`{escaped[0]}`"
        lines.append("| " + " | ".join(escaped) + " |")
    text = "\n".join(lines) + "\n"
    if args.check:
        if not output.exists() or output.read_text() != text:
            raise SystemExit("repository file catalog is stale")
        print(f"FILE_CATALOG_VALID tracked={len(rows)} coverage=PASS")
        return 0
    output.write_text(text)
    print(f"FILE_CATALOG_WRITTEN tracked={len(rows)} coverage=PASS output={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
