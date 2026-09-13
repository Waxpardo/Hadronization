"""Build the current-science TEST_ONLY nonzero chain fixture from raw events.

The source of the raw fixture is the validated analysis test generator, with
bounded replacements below.  Generated ROOT files and receipts are external.
"""

from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tests"))
from test_analysis import AnalysisShardContract, fixture_source, sha256

TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
EVENTS = 120


def claim_fresh_base():
    """Admit an explicit fresh destination before compiling or writing bytes."""
    value = os.environ.get("NONZERO_CHAIN_BASE", "")
    if not value.strip():
        raise ValueError("NONZERO_CHAIN_BASE must name a fresh directory")
    base = Path(value).expanduser()
    if not base.is_absolute():
        raise ValueError("NONZERO_CHAIN_BASE must be absolute")
    if any(component.is_symlink() for component in (base, *base.parents)):
        raise ValueError("NONZERO_CHAIN_BASE contains a symlink")
    if not base.parent.is_dir():
        raise ValueError("NONZERO_CHAIN_BASE parent must already exist")
    base.mkdir(exist_ok=False)
    return base


def replace_once(source, before, after):
    assert source.count(before) == 1, (source.count(before), before[:100])
    return source.replace(before, after)


def raw_source():
    source = fixture_source()
    source = replace_once(source, 'TH1D hMultiplicity("hMULTIPLICITY", "fixture", 10, -0.5, 9.5);', 'TH1D hMultiplicity("hMULTIPLICITY", "fixture", 32, -0.5, 31.5);')
    source = replace_once(source, 'TH1D hMultiplicityWide("hMULTIPLICITY_ETA40", "fixture", 10, -0.5, 9.5);', 'TH1D hMultiplicityWide("hMULTIPLICITY_ETA40", "fixture", 32, -0.5, 31.5);')
    source = replace_once(source, 'for (int row = 0; row < 3; ++row) {', 'for (int row = 0; row < 120; ++row) {')
    source = replace_once(source, 'const bool beautyEvent = mode != "one_channel" && row == 1;', 'const int channel = row % 4;\n    const bool beautyEvent = channel >= 2;')
    source = replace_once(source, 'mult10 = row; mult40 = row;', '''const int baseActivity = (fixtureLogical * 3 + row / 4) % 30;
    mult10 = baseActivity;
    // One extreme event per original block populates the genuine 0-1% tail.
    if (baseActivity == 0 && channel == fixtureLogical % 4) mult10 = 30;
    // Moving one low-activity row inside selected blocks gives P1 a finite
    // K10 dispersion without changing any percentile-threshold cumulative.
    if (fixtureLogical % 2 == 0 && baseActivity == 1 && channel == 0)
      mult10 = 0;
    mult40 = mult10;''')
    source = replace_once(source, 'legacyMultiplicity = row;', 'legacyMultiplicity = mult10;')
    begin = source.index('    std::vector<int> heavyPdgs = beautyEvent\n')
    end = source.index('    if (resolutionEvents && row == 0)', begin)
    source = source[:begin] + '''    std::vector<int> heavyPdgs;
    if (channel == 0)
      heavyPdgs = {421,-421,411,-411,4122,-4122,431,-431};
    else if (channel == 1)
      heavyPdgs = {4122,-4122,421,-421,411,-411,431,-431};
    else if (channel == 2)
      heavyPdgs = {521,-521,511,-511,531,-531,541,-541,5122,-5122};
    else
      heavyPdgs = {5122,-5122,521,-521,511,-511,531,-531,541,-541};
    // A second charge-balanced pair varies block-level ratios and MC errors.
    if ((fixtureLogical + row / 4 + fixtureTuneOrdinal) % 3 == 0) {
      heavyPdgs.push_back(beautyEvent ? 521 : 421);
      heavyPdgs.push_back(beautyEvent ? -521 : -421);
    }
''' + source[end:]
    source = replace_once(source, 'if (row == 0 && absolutePdg != 421) {', 'if (slot >= 2) {')
    begin = source.index('    if (row == 0) {\n      // Exact synthetic-digest inputs')
    end = source.index('    const std::vector<int> originalMatchedC', begin)
    source = source[:begin] + '''    // Actual four-vectors drive the analysis' kinematics cross-checks.
    for (std::size_t slot = 0; slot < heavyPdgs.size(); ++slot) {
      const bool trigger = slot == 0;
      const double pt = trigger ?
          ((fixtureLogical + row / 4) % 7 == 0 ? 0.0 :
           (fixtureLogical + row / 4) % 7 == 1 ? 0.5 :
           (fixtureLogical + row / 4) % 7 == 2 ? 1.0 :
           (fixtureLogical + row / 4) % 7 == 3 ? 0.2 : 1.5) :
          (slot == 1 && row == 0 ? 2.0 :
           slot == 1 && row == 4 ? 0.5 :
           slot % 3 == 0 ? 0.5 : slot % 3 == 1 ? 1.0 : 0.2);
      const double phi = trigger ?
          ((fixtureLogical + row / 4) % 3 - 1) * 1.1 :
          ((static_cast<int>(slot) + fixtureLogical + row / 4) % 5 - 2) * 0.65;
      // Suppress a varying signed partner, while preserving the final-heavy
      // conservation census.  All eleven activity classes retain channels.
      bool out = !trigger && ((fixtureLogical == 4 && (row == 4 || row == 5)) ||
          (slot > 1 &&
           (fixtureLogical + row / 4 + static_cast<int>(slot) + fixtureTuneOrdinal) % 7 == 0));
      // Selected signed reference parents must survive each delete-one block.
      // Only toy eta acceptance changes; the final-heavy census is untouched.
      if (channel == 0) {
        if (slot == 1 || slot == 5) out = false;
        if (slot == 4) out = true;
      }
      if (channel == 2) {
        if (slot == 1 || slot == 3 || slot == 5 || slot == 7 || slot == 8)
          out = false;
        if (slot == 2 || slot == 4 || slot == 6 || slot == 9)
          out = true;
      }
      const double eta = out ? 4.25 :
          ((static_cast<int>(slot) + fixtureLogical + row / 4) % 5 - 2) * 0.7;
      const double px = pt * std::cos(phi), py = pt * std::sin(phi);
      const double pz = pt * std::sinh(eta);
      const double energy = std::sqrt(1.0 + px * px + py * py + pz * pz);
      const double actualPt = std::hypot(px, py);
      const double actualEta = actualPt == 0.0 ? 0.0 : std::asinh(pz / actualPt);
      const double actualPhi = std::atan2(py, px);
      const double rapidity = std::atanh(pz / energy);
      doubleVectors["heavyPx"][slot] = px;
      doubleVectors["heavyPy"][slot] = py;
      doubleVectors["heavyPz"][slot] = pz;
      doubleVectors["heavyE"][slot] = energy;
      doubleVectors["heavyPt"][slot] = actualPt;
      doubleVectors["heavyEta"][slot] = actualEta;
      doubleVectors["heavyY"][slot] = rapidity;
      doubleVectors["heavyPhi"][slot] = actualPhi;
      doubleVectors["PT"][slot] = actualPt;
      doubleVectors["ETA"][slot] = actualEta;
      doubleVectors["Y"][slot] = rapidity;
      doubleVectors["PHI"][slot] = actualPhi;
    }
''' + source[end:]
    source = replace_once(source, '(mode == "one_channel" ? 3 : 2);', '(mode == "one_channel" ? 120 : 60);')
    source = replace_once(source, 'summaryCode = 123; summaryCount = 1; processes.Fill();', 'summaryCode = 123; summaryCount = 60; processes.Fill();')
    source = replace_once(source, 'settingValues["Main:numberOfEvents"] = "3";', 'settingValues["Main:numberOfEvents"] = "120";')
    source = replace_once(source, 'mu["requested_successes"] = 3; mu["attempts"] = 3;', 'mu["requested_successes"] = 120; mu["attempts"] = 120;')
    source = replace_once(source, 'mu["successful_events"] = mode == "accounting" ? 2 : 3;', 'mu["successful_events"] = mode == "accounting" ? 2 : 120;')
    source = replace_once(source, 'mu["failed_attempts"] = 0; mu["tree_entries"] = 3;', 'mu["failed_attempts"] = 0; mu["tree_entries"] = 120;')
    source = replace_once(source, 'md["sum_weights"] = 3.0; md["sum_weights2"] = 3.0;', 'md["sum_weights"] = 120.0; md["sum_weights2"] = 120.0;')
    source = replace_once(source, 'md["pythia_weight_sum"] = 3.0;', 'md["pythia_weight_sum"] = 120.0;')
    return source


def command(args, env, log=None):
    result = subprocess.run([str(x) for x in args], cwd=ROOT, env=env,
                            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if log is not None:
        Path(log).write_text(result.stdout + "\nSTDERR\n" + result.stderr)
    if result.returncode:
        raise RuntimeError(f"command failed {result.returncode}: {' '.join(str(x) for x in args)}\n{result.stdout[-3000:]}\n{result.stderr[-3000:]}")
    return result.stdout


def main():
    BASE = claim_fresh_base()
    F = AnalysisShardContract
    F.setUpClass()
    try:
        source = raw_source()
        (BASE / "raw-fixture.cpp").write_text(source)
        F._compile(source, BASE / "raw-fixture.cpp", BASE / "raw-fixture", include_generate=True)
        raw_root = BASE / "raw"
        work = BASE / "analyze-work"
        analyzed = BASE / "analyzed"
        control = BASE / "control"
        data = control / "data"
        config = control / "config"
        for path in (raw_root, work, analyzed, data, config):
            path.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / "config/study.json", config / "study.json")
        settings = {}
        rows = []
        attempts = ["tune,logical_id,attempt,seed,outcome,evidence_status,raw_storage_key"]
        for ordinal, tune in enumerate(TUNES):
            for logical in range(10):
                key = f"{tune}/toy-{logical:04d}.root"
                path = raw_root / key
                path.parent.mkdir(parents=True, exist_ok=True)
                command([BASE / "raw-fixture", path, "valid", logical, 0, tune, ordinal, 3], F.environment)
                if logical == 0:
                    settings[tune] = json.loads(command([F.base / "analyzer", "inspect-raw", path], F.environment))["effective_settings_sha256"]
                seed = 130000001 + ordinal * 1000000 + logical
                rows.append(dict(accepted_attempt=0, accepted_seed=seed, block=logical + 1,
                                 bytes=path.stat().st_size, logical_id=logical, raw_sha256=sha256(path),
                                 raw_storage_key=key, successful_events=EVENTS, tune=tune,
                                 validation_log_sha256="d" * 64, validation_receipt_sha256="e" * 64))
                attempts.append(f"{tune},{logical},0,{seed},accepted,accepted_manifest_confirmed,{key}")
        campaign = json.loads((ROOT / "data/campaign.json").read_text())
        campaign["tune_order"] = list(TUNES)
        campaign["logical_jobs_per_tune"] = 10
        campaign["successful_events_per_logical_job"] = EVENTS
        campaign["successful_events_per_tune"] = 10 * EVENTS
        campaign["blocks"] = {"count":10,"logical_id_domain":[0,9],"logical_id_rule":"block=(logical_id%10)+1"}
        campaign["seed"]["attempt_domain"] = [0,1]
        campaign["seed"]["tune_ordinals"] = {t:i for i,t in enumerate(TUNES)}
        campaign["attempt_evidence_inventory"] = {"file_count":30,"sha256":"a"*64}
        campaign["accepted_source"]["producer_executable_sha256"] = "b"*64
        campaign["accepted_source"]["producer_repository_commit"] = "c"*40
        for tune in TUNES:
            campaign["accepted_source"]["tune_cards"][tune]["accepted_effective_sha256"] = settings[tune]
        (data / "campaign.json").write_text(json.dumps(campaign,sort_keys=True))
        (data / "raw_manifest.jsonl").write_text("".join(json.dumps(row,sort_keys=True,separators=(",",":"))+"\n" for row in rows))
        (data / "attempts.csv").write_text("\n".join(attempts)+"\n")
        argv = [ROOT / "hadronization", "analyze", "plan", "--campaign", data / "campaign.json",
                "--manifest", data / "raw_manifest.jsonl", "--attempts", data / "attempts.csv",
                "--raw-root", raw_root, "--work-root", work, "--output-root", analyzed,
                "--plan", work / "plan.json", "--target-bytes", max(
                    sum(row["bytes"] for row in rows if row["tune"] == tune)
                    for tune in TUNES)]
        (work / "plan.json").unlink(missing_ok=True)
        command(argv, F.environment, BASE / "plan.log")
        command([ROOT / "hadronization", "analyze", "run", "--plan", work / "plan.json", "--jobs", 3],
                F.environment, BASE / "analyze.log")
        shard_dir = analyzed / "HF_RUN3_V1"
        qwork = BASE / "query-work"
        qroots = [shard_dir / f"shard-{i:04d}.root" for i in range(3)]
        receipts = [shard_dir / f"shard-{i:04d}.json" for i in range(3)]
        census = [ROOT / "hadronization", "query", "census"]
        for raw, receipt in zip(qroots, receipts):
            census += ["--input", raw, "--receipt", receipt]
        census += ["--expected-source-count", 30, "--output", BASE / "dictionary.json",
                   "--work-root", qwork]
        command(census, F.environment, BASE / "census.log")
        workspaces = []
        pins = []
        for i, (raw, receipt) in enumerate(zip(qroots, receipts)):
            workspace = BASE / "queries" / f"shard-{i:04d}"
            workspaces.append(workspace)
            command([ROOT / "hadronization", "query", "build", "--input", raw,
                     "--receipt", receipt, "--output", workspace,
                     "--dictionary", BASE / "dictionary.json", "--work-root", qwork],
                    F.environment, BASE / f"query-build-{i:04d}.log")
            pin = json.loads((workspace / "manifest.json").read_text())["scientific_content_sha256"]
            pins.append(pin)
            command([ROOT / "hadronization", "query", "verify", "--workspace", workspace,
                     "--expected-content-sha256", pin, "--work-root", qwork],
                    F.environment, BASE / f"query-verify-{i:04d}.log")
        planned = json.loads((work / "plan.json").read_text())
        expected = []
        for item in planned["sources"]:
            row = item["manifest_row"]
            expected.append(dict(source_id=item["source_id"], tune=row["tune"],
                                 tune_ordinal=TUNES.index(row["tune"]),
                                 logical_id=row["logical_id"], block=row["block"],
                                 events=row["successful_events"]))
        expected_path = BASE / "expected-sources.json"
        expected_path.write_text(json.dumps(expected,sort_keys=True,separators=(",",":"))+"\n")
        expected_sha = sha256(expected_path)
        sharded = BASE / "SHARDED.json"
        create = [ROOT / "hadronization", "collection", "create"]
        for workspace, pin in zip(workspaces, pins):
            create += ["--workspace", workspace, "--expected-content-sha256", pin]
        create += ["--expected-sources", expected_path, "--expected-sources-sha256", expected_sha,
                   "--output", sharded, "--work-root", BASE / "collection-work", "--test-only"]
        command(create, F.environment, BASE / "collection-create.log")
        sharded_sha = sha256(sharded)
        command([ROOT / "hadronization", "collection", "verify", "--index", sharded,
                 "--expected-index-sha256", sharded_sha], F.environment, BASE / "collection-verify.log")
        command([ROOT / "hadronization", "merge", "build", "--index", sharded,
                 "--expected-index-sha256", sharded_sha, "--output", BASE / "merged"],
                F.environment, BASE / "merge-build.log")
        merged = BASE / "merged" / "index.json"
        merged_sha = sha256(merged)
        command([ROOT / "hadronization", "merge", "verify", "--index", merged,
                 "--expected-index-sha256", merged_sha,
                 "--merge-receipt", BASE / "merged" / "merge-receipt.json",
                 "--merge-receipt-sha256", sha256(BASE / "merged" / "merge-receipt.json")],
                F.environment, BASE / "merge-verify.log")
        print(json.dumps({"base":str(BASE),"source_sha256":hashlib.sha256(source.encode()).hexdigest(),
                          "raw_sources":len(rows),"plan":str(work / "plan.json"),
                          "query_pins":pins,"sharded_sha256":sharded_sha,
                          "merged_sha256":merged_sha}, indent=2))
    finally:
        F.tearDownClass()


if __name__ == "__main__":
    main()
