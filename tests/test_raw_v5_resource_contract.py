"""Static guardrails for publication raw-v5 resource metadata."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRODUCER = (
    ROOT / "SimulationScripts" / "heavyflavourcorrelations_status.cpp"
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


def test_weak_decay_transition_is_independently_auditable() -> None:
    for branch in (
        "multAuditParticleIndex",
        "multAuditHasWeakDecayTransition",
        "multAuditEventPdg",
        "multAuditEventStatus",
        "multAuditEventMotherOffsets",
        "multAuditEventMothers",
    ):
        assert f"BRANCH_VECTOR({branch})" in PRODUCER
        assert f'"{branch}"' in VALIDATOR
    assert "HasWeakDecayTransition(pythia.event, index)" in PRODUCER
    assert "RecomputeWeakDecayTransition(" in VALIDATOR
    assert (
        "stored weak-decay transition disagrees with independent "
        in VALIDATOR
    )
    assert "multiplicity audit candidate index set is incomplete" in VALIDATOR
    assert "multAuditHasWeakAncestor" not in PRODUCER
    assert "multAuditHasWeakAncestor" not in VALIDATOR
    for metadata_name in (
        "weak_parent_registry_schema",
        "weak_parent_registry_sha256",
        "weak_decay_transition_rule",
    ):
        assert f'metadata.Branch("{metadata_name}"' in PRODUCER
        assert f'ReadString(metadata, "{metadata_name}"' in VALIDATOR


def main() -> int:
    test_peak_rss_is_measured_and_persisted_as_ulong64_kib()
    test_validator_requires_positive_peak_rss_with_exact_scalar_type()
    test_root_compression_contract_is_persisted_and_cross_checked()
    test_exact_signed_hard_pair_persists_root_and_bottom_copy_state()
    test_raw_v5_compatibility_status_and_indices_are_integer_typed()
    test_weak_decay_transition_is_independently_auditable()
    print("raw-v5 resource-contract tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
