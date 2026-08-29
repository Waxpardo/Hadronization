#!/usr/bin/env python3
"""Focused synthetic refusals for the corrected verdict-v3 writer."""

from __future__ import annotations

import copy
import hashlib
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "extraction"))

import write_verdict as writer  # noqa: E402
from harvest_class_axis import sample_sem  # noqa: E402

BASE_CONTRACT = json.loads((ROOT / "config/verdict_v3.json").read_text())
CLASS_CONTRACT = json.loads(
    (ROOT / "config/multiplicity_percentile_classes_v2.json").read_text()
)
POLICY = json.loads((ROOT / "config/systematics_sources_v1.json").read_text())
COMMIT = subprocess.check_output(
    ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True
).strip()
SHORT = COMMIT[:12]
TUNES = writer.TUNES


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def vector(values: list[float]) -> str:
    return ",".join(format(value, ".17g") for value in values)


def campaign_rows(campaign_index: int) -> tuple[str, str]:
    lines = []
    legacy = ["historical shared-field control"]
    campaign = BASE_CONTRACT["rendered_configurations"][campaign_index]["campaign"]
    for tune_index, tune in enumerate(TUNES):
        lines.append(
            f"Beauty central resolver {tune}: base=/synthetic, "
            f"tag=complete_root_{campaign}"
        )
    for class_index, class_row in enumerate(CLASS_CONTRACT["classes"], start=1):
        bin_name = "hDPhi" + class_row["bin"]
        pair_bin = class_row["bin"]
        for tune_index, tune in enumerate(TUNES):
            n_trig = 1000
            ref_ss = 10
            ref_os = 1010 + 100 * tune_index + class_index + campaign_index
            num_ss = 10
            num_os = 510 + 80 * tune_index + 10 * class_index + campaign_index
            reference = (ref_os - ref_ss) / n_trig
            numerator = (num_os - num_ss) / n_trig
            pooled_ratio = numerator / reference
            offsets = [
                (block - 4.5) * 0.0005 for block in range(10)
            ]
            ref_blocks = [reference + offset for offset in offsets]
            ratio_blocks = [
                pooled_ratio + offset * (1.0 + class_index / 20.0)
                for offset in offsets
            ]
            num_blocks = [
                ratio * ref
                for ratio, ref in zip(ratio_blocks, ref_blocks)
            ]
            common = (
                "schema=hadronization_uncertainty_matrix_v2 "
                "block_count=10 flavour=BEAUTY trigger=B^{+} "
                f"tune={tune} bin={bin_name} central_triggers={n_trig} "
                "block_triggers=100,100,100,100,100,100,100,100,100,100 "
            )
            reference_line = (
                "UNCERTAINTY_MATRIX " + common
                + "associate=B- is_reference=true "
                + f"block_yields={vector(ref_blocks)} block_ratios=NA "
                + f"central_yield={reference:.17g} "
                + f"yield_sem={sample_sem(ref_blocks):.17g} "
                + f"reference_yield={reference:.17g} ratio_sem=NA "
                + "finite_yields=10 finite_ratios=NA status=PASS "
                + "ratio_status=NOT_APPLICABLE"
            )
            numerator_line = (
                "UNCERTAINTY_MATRIX " + common
                + "associate=Lambda_b is_reference=false "
                + f"block_yields={vector(num_blocks)} "
                + f"block_ratios={vector(ratio_blocks)} "
                + f"central_yield={numerator:.17g} "
                + f"yield_sem={sample_sem(num_blocks):.17g} "
                + f"reference_yield={reference:.17g} "
                + f"ratio_sem={sample_sem(ratio_blocks):.17g} "
                + "finite_yields=10 finite_ratios=10 status=PASS "
                + "ratio_status=PASS"
            )
            lines.extend([
                f"PAIR_COUNTS tune={tune} flavour=BEAUTY trigger=B^{{+}} "
                f"associate=B- os_file=BplusBminus.root bin={pair_bin} "
                f"n_os={ref_os} n_ss={ref_ss} n_trig={n_trig}",
                f"PAIR_COUNTS tune={tune} flavour=BEAUTY trigger=B^{{+}} "
                f"associate=Lambda_b os_file=LbbarBminus.root bin={pair_bin} "
                f"n_os={num_os} n_ss={num_ss} n_trig={n_trig}",
                reference_line,
                numerator_line,
            ])
            for line in (reference_line, numerator_line):
                fields = dict(
                    token.split("=", 1)
                    for token in line.split() if "=" in token
                )
                legacy.append(
                    "UNCERTAINTY_MATRIX "
                    f"flavour={fields['flavour']} trigger={fields['trigger']} "
                    f"tune={fields['tune']} associate={fields['associate']} "
                    f"bin={fields['bin']} central_yield={fields['central_yield']} "
                    f"yield_sem={fields['yield_sem']} "
                    f"central_triggers={fields['central_triggers']}"
                )
    return "\n".join(lines) + "\n", "\n".join(legacy) + "\n"


def boundary_payload() -> dict:
    receipt = {
        "schema": writer.BOUNDARY_SCHEMA,
        "schema_version": 2,
        "completion_status": "PASS",
        "algorithm": "per_tune_summed_multiplicity_quantiles_discrete_v2",
        "class_contract_sha256": digest(
            ROOT / "config/multiplicity_percentile_classes_v2.json"
        ),
        "tunes": {},
    }
    for tune_index, tune in enumerate(TUNES):
        classes = []
        for index, row in enumerate(CLASS_CONTRACT["classes"], start=1):
            classes.append({
                "percentile_min": row["percentile_min"],
                "percentile_max": row["percentile_max"],
                "nch_min_inclusive": index,
                "nch_max_inclusive": index,
                "target_fraction": (
                    row["percentile_max"] - row["percentile_min"]
                ) / 100.0,
                "achieved_weighted_fraction":
                    0.05 + 0.001 * index + 0.0001 * tune_index,
            })
        receipt["tunes"][tune] = {
            "classes": classes,
            "partition": {
                "coverage": "PASS",
                "disjointness": "PASS",
            },
        }
    receipt["payload_sha256"] = writer.json_sha256(receipt)
    return receipt


class Fixture:
    def __init__(self, base: Path):
        self.base = base
        self.results = base / "results"
        self.results.mkdir()
        self.contract = copy.deepcopy(BASE_CONTRACT)
        self.logs: dict[str, Path] = {}
        self.receipts: dict[str, Path] = {}
        self.boundaries: dict[str, Path] = {}
        self.raw: dict[str, Path] = {}
        legacy_text = ""
        for index, configuration in enumerate(
            self.contract["rendered_configurations"]
        ):
            campaign = configuration["campaign"]
            directory = (
                self.results / campaign / SHORT / "measurements"
                / configuration["dataset"]
            )
            plots = directory / "plots"
            plots.mkdir(parents=True)
            log = directory / "render.log"
            text, legacy = campaign_rows(index)
            log.write_text(text)
            if index == 0:
                legacy_text = legacy
            receipt = directory / "measurement_receipt.json"
            receipt.write_text(json.dumps({
                "schema": writer.RECEIPT_SCHEMA,
                "completion_status": "PASS",
                "failure_reasons": [],
                "purpose": "measurement",
                "publication_eligible": False,
                "campaign": campaign,
                "render_exit_status": 0,
                "output_assertion_exit_status": 0,
                "log_sha256": digest(log),
                "uncertainty_matrix_rows": 66,
                "expected_uncertainty_matrix_rows": 66,
                "missing_uncertainty_identities": [],
                "unexpected_uncertainty_identities": [],
                "duplicate_uncertainty_identities": 0,
                "non_pass_uncertainty_rows": [],
            }))
            boundary = plots / "multiplicity_boundary_receipt_v2.json"
            boundary.write_text(json.dumps(boundary_payload()))
            self.logs[campaign] = log
            self.receipts[campaign] = receipt
            self.boundaries[campaign] = boundary

        control = (
            self.results
            / self.contract["historical_control"]["results_root_relative_path"]
        )
        control.parent.mkdir(parents=True)
        control.write_text(legacy_text)
        self.control = control
        self.contract["historical_control"]["sha256"] = digest(control)
        self.contract_path = base / "verdict_contract.json"
        self.contract_path.write_text(json.dumps(self.contract))

        allowlist_sha = digest(ROOT / "config/tune_difference_allowlist_v1.json")
        for tune in TUNES:
            raw = base / "raw" / tune / f"hf_{tune}_job000.root"
            raw.parent.mkdir(parents=True)
            raw.write_text(f"{tune} raw\n")
            self.raw[tune] = raw
        outputs = self.contract["output_paths_relative_to_results_root"]
        self.effective = self.results / outputs[
            "effective_settings_receipt"
        ].format(commit=SHORT)
        self.effective.parent.mkdir(parents=True)
        self.effective.write_text(json.dumps({
            "schema": writer.EFFECTIVE_SETTINGS_SCHEMA,
            "status": "PASS",
            "allowlist": {"sha256": allowlist_sha},
            "inputs": {
                tune: {"basename": self.raw[tune].name,
                       "sha256": digest(self.raw[tune])}
                for tune in TUNES
            },
        }))

        exclusions, problems = writer.source_exclusions(POLICY)
        assert not problems
        self.envelope = self.results / outputs[
            "systematics_envelope"
        ].format(commit=SHORT)
        self.envelope.parent.mkdir(parents=True, exist_ok=True)
        nominal = self.contract["nominal"]["campaign"]
        variations = [
            row["campaign"]
            for row in self.contract["rendered_configurations"][1:]
        ]
        self.envelope.write_text(json.dumps({
            "schema": writer.ENVELOPE_SCHEMA,
            "status": "COMPLETE",
            "missing": [],
            "sources": POLICY["sources"],
            "exclusions": exclusions,
            "rows": [{"class": "c1"}],
            "provenance": {
                "producing_commit": COMMIT,
                "sources_contract_sha256": digest(
                    ROOT / "config/systematics_sources_v1.json"
                ),
                "measurement_receipts": {
                    campaign: {
                        "receipt_sha256": digest(self.receipts[campaign]),
                        "boundary_receipt_sha256":
                            digest(self.boundaries[campaign]),
                        "completion_status": "PASS",
                    }
                    for campaign in variations
                },
                "nominal_boundary_receipt_sha256":
                    digest(self.boundaries[nominal]),
                "nominal_boundary_receipt_path":
                    self.boundaries[nominal].resolve().as_posix(),
            },
        }))
        self.out_json = self.results / outputs["verdict_json"].format(
            commit=SHORT
        )
        self.out_markdown = self.results / outputs[
            "verdict_markdown"
        ].format(commit=SHORT)

    def refresh(self, campaign: str) -> None:
        receipt = json.loads(self.receipts[campaign].read_text())
        receipt["log_sha256"] = digest(self.logs[campaign])
        self.receipts[campaign].write_text(json.dumps(receipt))
        if campaign != self.contract["nominal"]["campaign"]:
            envelope = json.loads(self.envelope.read_text())
            record = envelope["provenance"]["measurement_receipts"][campaign]
            record["receipt_sha256"] = digest(self.receipts[campaign])
            record["boundary_receipt_sha256"] = digest(
                self.boundaries[campaign]
            )
            self.envelope.write_text(json.dumps(envelope))

    def command(self) -> list[str]:
        nominal = self.contract["nominal"]["campaign"]
        command = [
            sys.executable,
            str(ROOT / "extraction/write_verdict.py"),
            "--results-root", str(self.results),
            "--nominal", str(self.logs[nominal]),
            "--nominal-receipt", str(self.receipts[nominal]),
            "--control", str(self.control),
        ]
        for configuration in self.contract["rendered_configurations"][1:]:
            campaign = configuration["campaign"]
            command.extend(["--variation", f"{campaign}={self.logs[campaign]}"])
        for configuration in self.contract["rendered_configurations"][1:]:
            campaign = configuration["campaign"]
            command.extend([
                "--variation-receipt",
                f"{campaign}={self.receipts[campaign]}",
            ])
        command.extend([
            "--envelope", str(self.envelope),
            "--effective-settings", str(self.effective),
        ])
        for tune in TUNES:
            command.extend(["--effective-raw", f"{tune}={self.raw[tune]}"])
        command.extend([
            "--out-json", str(self.out_json),
            "--out-markdown", str(self.out_markdown),
            "--contract", str(self.contract_path),
        ])
        return command

    def run(self, extra: list[str] | None = None) -> subprocess.CompletedProcess:
        return subprocess.run(
            self.command() + (extra or []),
            text=True,
            capture_output=True,
            check=False,
        )


def check(name: str, function) -> None:
    try:
        function()
    except Exception as error:
        raise AssertionError(f"{name}: {error}") from error


def with_fixture(function) -> None:
    with tempfile.TemporaryDirectory() as temporary:
        function(Fixture(Path(temporary)))


def test_complete_record() -> None:
    def run(fixture: Fixture) -> None:
        result = fixture.run()
        assert result.returncode == 0, result.stdout + result.stderr
        payload = json.loads(fixture.out_json.read_text())
        assert payload["schema"] == writer.VERDICT_SCHEMA
        assert len(payload["rendered_configurations"]) == 7
        disclosed = sum(
            len(tune["classes"])
            for configuration in payload["rendered_configurations"]
            for tune in configuration["tunes"].values()
        )
        assert disclosed == 7 * 3 * 11
        assert "cancellation_fraction" not in fixture.out_json.read_text()
        for tune in TUNES:
            trend = payload["nominal_ratio_trend"][tune]
            assert len(trend["covariance_of_class_means"]["covariance_of_means"]) == 11
            assert all(row["agrees"] for row in trend["covariance_diagonal_proof"])
            assert len(trend["endpoint_c11_minus_c1"]["block_contrasts"]) == 10
        assert payload["supporting_fit_status"]["physical_coordinate_fit_produced"] is False
        body = dict(payload)
        claimed = body.pop("payload_sha256")
        assert claimed == writer.json_sha256(body)
    with_fixture(run)


def test_missing_and_failed_receipts() -> None:
    def missing(fixture: Fixture) -> None:
        fixture.receipts["HF_RUN3_V1"].unlink()
        result = fixture.run()
        assert result.returncode != 0 and "receipt" in result.stderr
    with_fixture(missing)

    def failed(fixture: Fixture) -> None:
        receipt = json.loads(fixture.receipts["HF_SYS_MUR_UP"].read_text())
        receipt["completion_status"] = "FAIL"
        fixture.receipts["HF_SYS_MUR_UP"].write_text(json.dumps(receipt))
        fixture.refresh("HF_SYS_MUR_UP")
        result = fixture.run()
        assert result.returncode != 0 and "not an exact PASS" in result.stderr
    with_fixture(failed)


def test_missing_pair_counts_and_count_identity() -> None:
    def missing(fixture: Fixture) -> None:
        log = fixture.logs["HF_RUN3_V1"]
        lines = log.read_text().splitlines()
        lines.remove(next(line for line in lines if line.startswith("PAIR_COUNTS")
                          and "associate=Lambda_b" in line))
        log.write_text("\n".join(lines) + "\n")
        fixture.refresh("HF_RUN3_V1")
        result = fixture.run()
        assert result.returncode != 0 and "missing PAIR_COUNTS" in result.stderr
    with_fixture(missing)

    def mismatch(fixture: Fixture) -> None:
        log = fixture.logs["HF_RUN3_V1"]
        text = log.read_text()
        target = next(line for line in text.splitlines()
                      if line.startswith("PAIR_COUNTS")
                      and "associate=Lambda_b" in line)
        token = next(part for part in target.split()
                     if part.startswith("n_os="))
        value = int(token.split("=", 1)[1])
        changed = target.replace(token, f"n_os={value + 1}", 1)
        log.write_text(text.replace(target, changed, 1))
        fixture.refresh("HF_RUN3_V1")
        result = fixture.run()
        assert result.returncode != 0 and "yield disagrees" in result.stderr
    with_fixture(mismatch)


def test_malformed_blocks_and_boundary_receipts() -> None:
    def missing_blocks(fixture: Fixture) -> None:
        log = fixture.logs["HF_RUN3_V1"]
        text = log.read_text()
        line = next(line for line in text.splitlines()
                    if line.startswith("UNCERTAINTY_MATRIX")
                    and "associate=Lambda_b" in line)
        token = next(token for token in line.split()
                     if token.startswith("block_yields="))
        log.write_text(text.replace(token + " ", "", 1))
        fixture.refresh("HF_RUN3_V1")
        result = fixture.run()
        assert result.returncode != 0 and "block_yields" in result.stderr
    with_fixture(missing_blocks)

    def blocks(fixture: Fixture) -> None:
        log = fixture.logs["HF_RUN3_V1"]
        text = log.read_text()
        line = next(line for line in text.splitlines()
                    if line.startswith("UNCERTAINTY_MATRIX")
                    and "associate=Lambda_b" in line)
        token = next(token for token in line.split()
                     if token.startswith("block_ratios="))
        changed = token.rsplit(",", 1)[0]
        log.write_text(text.replace(token, changed, 1))
        fixture.refresh("HF_RUN3_V1")
        result = fixture.run()
        assert result.returncode != 0 and "block_ratios" in result.stderr
    with_fixture(blocks)

    def boundary(fixture: Fixture) -> None:
        fixture.boundaries["HF_RUN3_V1"].unlink()
        result = fixture.run()
        assert result.returncode != 0 and "boundary" in result.stderr
    with_fixture(boundary)

    def boundary_mismatch(fixture: Fixture) -> None:
        path = fixture.boundaries["HF_RUN3_V1"]
        receipt = json.loads(path.read_text())
        receipt["tunes"]["MONASH"]["classes"][0][
            "achieved_weighted_fraction"
        ] += 0.00001
        receipt.pop("payload_sha256")
        receipt["payload_sha256"] = writer.json_sha256(receipt)
        path.write_text(json.dumps(receipt))
        result = fixture.run()
        assert result.returncode != 0
        assert "nominal boundary binding differs" in result.stderr
    with_fixture(boundary_mismatch)


def test_covariance_diagonal_refusal() -> None:
    per_class = [
        {"class": f"c{index}", "ratio_sem": 0.1}
        for index in range(1, 12)
    ]
    covariance = {
        "classes": [row["class"] for row in per_class],
        "covariance_of_means": [
            [0.01 if i == j else 0.0 for j in range(11)]
            for i in range(11)
        ],
    }
    covariance["covariance_of_means"][3][3] = 0.02
    try:
        writer.assert_covariance_diagonal(covariance, per_class)
    except ValueError as error:
        assert "covariance diagonal" in str(error)
        return
    raise AssertionError("a changed covariance diagonal passed")


def test_envelope_and_policy_refusals() -> None:
    def incomplete(fixture: Fixture) -> None:
        envelope = json.loads(fixture.envelope.read_text())
        envelope["status"] = "INCOMPLETE"
        fixture.envelope.write_text(json.dumps(envelope))
        result = fixture.run()
        assert result.returncode != 0 and "not COMPLETE" in result.stderr
    with_fixture(incomplete)

    def drift(fixture: Fixture) -> None:
        envelope = json.loads(fixture.envelope.read_text())
        envelope["sources"][0]["title"] = "drifted"
        fixture.envelope.write_text(json.dumps(envelope))
        result = fixture.run()
        assert result.returncode != 0 and "source drift" in result.stderr
    with_fixture(drift)

    def exclusion_drift(fixture: Fixture) -> None:
        envelope = json.loads(fixture.envelope.read_text())
        envelope["exclusions"][0]["reason"] = "drifted"
        fixture.envelope.write_text(json.dumps(envelope))
        result = fixture.run()
        assert result.returncode != 0 and "exclusion drift" in result.stderr
    with_fixture(exclusion_drift)


def test_nominal_control_separation_and_fit_deferral() -> None:
    def same_bytes(fixture: Fixture) -> None:
        nominal = fixture.logs["HF_RUN3_V1"]
        fixture.control.write_bytes(nominal.read_bytes())
        contract = json.loads(fixture.contract_path.read_text())
        contract["historical_control"]["sha256"] = digest(fixture.control)
        fixture.contract_path.write_text(json.dumps(contract))
        result = fixture.run()
        assert result.returncode != 0 and "same bytes" in result.stderr
    with_fixture(same_bytes)

    def fit_contract(fixture: Fixture) -> None:
        contract = json.loads(fixture.contract_path.read_text())
        contract["supporting_fit_status"][
            "physical_coordinate_fit_produced"
        ] = True
        fixture.contract_path.write_text(json.dumps(contract))
        result = fixture.run()
        assert result.returncode != 0
        assert "fit must remain deferred" in result.stderr
        assert not fixture.out_json.exists()
    with_fixture(fit_contract)

    def fit_argument(fixture: Fixture) -> None:
        result = fixture.run(["--fit-coordinate", "class-index"])
        assert result.returncode != 0
        assert "unrecognized arguments" in result.stderr
        assert not fixture.out_json.exists()
    with_fixture(fit_argument)


def test_zero_denominator_refusal() -> None:
    row = {"central_triggers": "0", "central_yield": "0"}
    try:
        writer.count_disclosure(
            row, {"N_trig": 0, "N_OS": 1, "N_SS": 0}, "test"
        )
    except ZeroDivisionError as error:
        assert "N_trig is zero" in str(error)
        return
    raise AssertionError("a zero trigger denominator passed")


if __name__ == "__main__":
    tests = [
        test_complete_record,
        test_missing_and_failed_receipts,
        test_missing_pair_counts_and_count_identity,
        test_malformed_blocks_and_boundary_receipts,
        test_covariance_diagonal_refusal,
        test_envelope_and_policy_refusals,
        test_nominal_control_separation_and_fit_deferral,
        test_zero_denominator_refusal,
    ]
    for test in tests:
        check(test.__name__, test)
    print(f"verdict v3: {len(tests)} focused checks passed")
