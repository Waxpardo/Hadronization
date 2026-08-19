"""Static guardrails for publication raw-v5 resource metadata."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRODUCER = (
    ROOT / "generation" / "producer" / "heavyflavourcorrelations_status.cpp"
).read_text()
VALIDATOR = (ROOT / "Validation" / "ValidateRawOutput.C").read_text()


def test_peak_rss_is_measured_and_persisted_as_ulong64_kib() -> None:
    assert "getrusage(RUSAGE_SELF, &usage)" in PRODUCER
    assert "Darwin reports ru_maxrss in bytes" in PRODUCER
    assert "Linux and the BSDs report ru_maxrss in KiB" in PRODUCER
    assert (
        'metadata.Branch("peak_rss_kib", &peakRssKiB, "peak_rss_kib/l")'
        in PRODUCER
    )


def test_validator_requires_positive_peak_rss_with_exact_scalar_type() -> None:
    assert 'ReadScalar(metadata, "peak_rss_kib", peakRssKiB)' in VALIDATOR
    assert "if (peakRssKiB == 0)" in VALIDATOR
    assert (
        "std::is_same_v<T, unsigned long long> && type == \"ULong64_t\""
        in VALIDATOR
    )


def test_root_compression_contract_is_persisted_and_cross_checked() -> None:
    for name in (
        "root_compression_settings",
        "root_compression_algorithm",
        "root_compression_level",
    ):
        assert f'metadata.Branch("{name}"' in PRODUCER
        assert f'ReadScalar(metadata, "{name}"' in VALIDATOR
    assert "rootCompressionSettings != file.GetCompressionSettings()" in (
        VALIDATOR
    )
    assert "rootCompressionAlgorithm != file.GetCompressionAlgorithm()" in (
        VALIDATOR
    )
    assert "rootCompressionLevel != file.GetCompressionLevel()" in VALIDATOR


def test_exact_signed_hard_pair_persists_root_and_bottom_copy_state() -> None:
    for branch in (
        "hard_indices",
        "hard_status",
        "hard_bottom_indices",
        "hard_bottom_ids",
        "hard_bottom_status",
    ):
        assert f'tree.Branch("{branch}"' in PRODUCER
        assert f'"{branch}"' in VALIDATOR
    assert "std::abs((*hardStatus)[hard]) != 23" in VALIDATOR


def test_raw_v5_compatibility_status_and_indices_are_integer_typed() -> None:
    assert (
        "std::vector<int> legacyStatus, legacyMother, legacyMotherId;"
        in PRODUCER
    )
    assert "std::vector<double> legacyStatus" not in PRODUCER
    for name in ("ID", "HFCLASS", "STATUS", "MOTHER", "MOTHERID"):
        assert f'"{name}"' in VALIDATOR


def test_primary_charged_multiplicity_is_independently_auditable() -> None:
    """The pilot record must let the validator recompute Nch from scratch."""
    for branch in (
        "multAuditParticleIndex",
        "multAuditPdg",
        "multAuditStatus",
        "multAuditIsHeavy",
        "multAuditPt",
        "multAuditEta",
    ):
        assert f"BRANCH_VECTOR({branch})" in PRODUCER
        assert f'"{branch}"' in VALIDATOR

    # Both windows are stored, and the central one is the published classifier.
    for branch in (
        "multiplicity_primary_charged_eta10_v1",
        "multiplicity_primary_charged_eta40_v1",
        "multiplicity_central_by_species",
    ):
        assert f'tree.Branch("{branch}"' in PRODUCER
        assert f'"{branch}"' in VALIDATOR

    # Charge and heavy content come from the generator, never from hand-rolled
    # PDG digit arithmetic in the producer's multiplicity path.
    assert "particle.isCharged()" in PRODUCER
    assert 'pythia.particleData.nQuarksInCode(id, 4)' in PRODUCER
    assert "CountsNchPrimaryChargedV1" in PRODUCER
    assert "CountsNchPrimaryChargedV1" in VALIDATOR

    # The superseded ancestry-based cross-check must be fully gone: with
    # ParticleDecays:limitTau0 in force it reconstructed a condition the
    # generator already guarantees.
    for removed in (
        "HasWeakDecayTransition",
        "RecomputeWeakDecayTransition",
        "multAuditHasWeakDecayTransition",
        "multAuditEventMothers",
        "weak_parent_registry_schema",
        "multiplicity_final_strong_em_v1",
    ):
        assert removed not in PRODUCER, removed
        assert removed not in VALIDATOR, removed

    # The recomputation and the window-nesting invariant must be enforced.
    assert "independent pilot multiplicity recomputation mismatch" in VALIDATOR
    assert "central multiplicity window exceeds the wider window" in VALIDATOR
    for metadata_name in ("multiplicity_definition",):
        assert f'metadata.Branch("{metadata_name}"' in PRODUCER
        assert f'ReadString(metadata, "{metadata_name}"' in VALIDATOR


def main() -> int:
    test_peak_rss_is_measured_and_persisted_as_ulong64_kib()
    test_validator_requires_positive_peak_rss_with_exact_scalar_type()
    test_root_compression_contract_is_persisted_and_cross_checked()
    test_exact_signed_hard_pair_persists_root_and_bottom_copy_state()
    test_raw_v5_compatibility_status_and_indices_are_integer_typed()
    test_primary_charged_multiplicity_is_independently_auditable()
    print("raw-v5 resource-contract tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
