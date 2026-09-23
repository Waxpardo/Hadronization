"""Independent generator-row oracle and physical collection equality check."""

from array import array
from collections import Counter, defaultdict
import json
import math
import os
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT_DIR / "pipeline/query"))
import collection as c

TUNES = ("MONASH", "JUNCTIONS", "CLOSEPACKING")
required_order = (421,4122,521,5122)
percentiles = (0,1,10,20,30,40,50,60,70,80,90,100)
PARENTS = ((421, -4122), (421, 4122), (421, -421), (421, 421),
           (4122, -421), (4122, 421),
           (521, 5122), (521, -5122), (521, -521), (521, 521),
           (521, -511), (521, 511), (521, -531), (521, 531),
           (521, -541), (521, 541))
EXTENDED = {421: (-431,-4112,-4212,-4222,-4132,-4232),
            4122: (-431,-4112,-4212,-4222,-4132,-4232),
            521: (5112,5222,5132,5232),
            5122: (-5112,-5222,-5132,-5232)}
PARENTS += tuple((trigger,signed) for trigger,associates in EXTENDED.items()
                 for associate in associates for signed in (associate,-associate))
BALANCES = {
    "D0_reference_meson": ((421,-421),(421,421)),
    "D0_P8_baryon": ((421,-4122),(421,4122)),
    "Bplus_reference_meson": ((521,-521),(521,521)),
    "Bplus_D": ((521,-511),(521,511)),
    "Bplus_Bs": ((521,-531),(521,531)),
    "Bplus_Bc": ((521,-541),(521,541)),
    "Bplus_P8_baryon": ((521,5122),(521,-5122)),
}


def admitted_paths():
    """Require an explicit existing input and a fresh nonsymlink report path."""
    value = os.environ.get("NONZERO_CHAIN_BASE", "")
    if not value.strip():
        raise ValueError("NONZERO_CHAIN_BASE must name an existing fixture")
    base = Path(value).expanduser()
    if not base.is_absolute() or any(p.is_symlink() for p in (base, *base.parents)):
        raise ValueError("NONZERO_CHAIN_BASE must be absolute and nonsymlinked")
    if not base.is_dir():
        raise ValueError("NONZERO_CHAIN_BASE must be an existing directory")
    report_value = os.environ.get("NONZERO_CHAIN_REPORT", "")
    if "NONZERO_CHAIN_REPORT" in os.environ and not report_value.strip():
        raise ValueError("NONZERO_CHAIN_REPORT must name a fresh file")
    report = Path(report_value).expanduser() if report_value else base / "oracle.json"
    if not report.is_absolute() or any(p.is_symlink() for p in (report, *report.parents)):
        raise ValueError("NONZERO_CHAIN_REPORT must be absolute and nonsymlinked")
    if not report.parent.is_dir() or report.exists():
        raise FileExistsError("NONZERO_CHAIN_REPORT needs an existing parent and fresh filename")
    return base, report


def publish_report(report_path, report):
    """Never replace the evidence of an earlier independent audit."""
    with report_path.open("x", encoding="utf-8") as output:
        output.write(json.dumps(report,indent=2,sort_keys=True)+"\n")


def event_id(tune, logical, row):
    return (3 << 48) | (tune << 46) | (logical << 32) | row


def activity(logical, row):
    channel = row % 4
    base = (logical*3 + row//4) % 30
    if base == 0 and channel == logical % 4:
        return 30
    if logical % 2 == 0 and base == 1 and channel == 0:
        return 0
    return base


def pdgs(channel, logical, round_, tune):
    rows = (
        [421,-421,411,-411,4122,-4122,431,-431],
        [4122,-4122,421,-421,411,-411,431,-431],
        [521,-521,511,-511,531,-531,541,-541,5122,-5122],
        [5122,-5122,521,-521,511,-511,531,-531,541,-541],
    )
    value = rows[channel][:]
    value += ([4112,-4112,4212,-4212,4222,-4222,4132,-4132,4232,-4232]
              if channel < 2 else [5112,-5112,5222,-5222,5132,-5132,5232,-5232])
    if (logical + round_ + tune) % 3 == 0:
        parent = 521 if channel >= 2 else 421
        value += [parent, -parent]
    return value


def pt(logical, row, slot):
    if slot == 0:
        return (0.0,0.5,1.0,0.2,1.5,1.5,1.5)[(logical+row//4)%7]
    if slot == 1 and row == 0:
        return 2.0
    if slot == 1 and row == 4:
        return 0.5
    return (0.5,1.0,0.2)[slot%3]


def phi(logical, row, slot):
    if slot == 0:
        return ((logical+row//4)%3-1)*1.1
    return ((slot+logical+row//4)%5-2)*0.65


def actual_pt(logical, row, slot):
    p, angle = pt(logical,row,slot), phi(logical,row,slot)
    return math.hypot(p*math.cos(angle), p*math.sin(angle))


def out_of_eta(logical, row, slot, tune):
    channel = row % 4
    if channel == 0:
        if slot in (1,5):
            return False
        if slot == 4:
            return True
    if channel == 2:
        if slot in (1,3,5,7,8):
            return False
        if slot in (2,4,6,9):
            return True
    return slot > 0 and ((logical == 4 and row in (4,5)) or
           (slot > 1 and (logical+row//4+slot+tune)%7 == 0))


def expected_rows(tune):
    counts = Counter()
    block_counts = defaultdict(Counter)
    optional = Counter()
    above = 0
    for logical in range(10):
        for row in range(120):
            channel = row % 4
            states = pdgs(channel,logical,row//4,tune)
            trigger = states[0]
            counts[("trigger",trigger)] += 1
            for slot, associate in enumerate(states[1:], start=1):
                if out_of_eta(logical,row,slot,tune):
                    continue
                key = (trigger,associate)
                if key not in PARENTS:
                    continue
                counts[key] += 1
                block_counts[logical][key] += 1
                trigger_pt = actual_pt(logical,row,0)
                associate_pt = actual_pt(logical,row,slot)
                if trigger_pt >= 0.5 and associate_pt >= 0.5:
                    optional[key] += 1
                if associate_pt > trigger_pt:
                    above += 1
    return counts,optional,above,block_counts


def observed_rows(tune, base):
    ROOT = c._root()
    file = ROOT.TFile.Open(str(base / "queries" / f"shard-{tune:04d}" / "query.root"))
    heavy = {(int(r.event_id),int(r.heavy_index)):
             (int(r.pdg),float(r.eta)) for r in file.Get("heavy")}
    block_activity = defaultdict(Counter)
    block_channels = defaultdict(set)
    for r in file.Get("events"):
        eid,activity_value = int(r.event_id),int(r.a15_eta4)
        logical = (eid >> 32) & 0x3fff
        block_activity[logical][activity_value] += 1
        block_channels[logical,activity_value].add(heavy[eid,20][0])
    assert set(block_activity)==set(range(10))
    required = {421,4122,521,5122}
    expected_by_block = {}
    expected_channels = defaultdict(set)
    for logical in range(10):
        expected_by_block[logical] = Counter(activity(logical,row) for row in range(120))
        for row in range(120):
            expected_channels[logical,activity(logical,row)].add(required_order[row%4])
        assert block_activity[logical]==expected_by_block[logical]
        assert set(block_activity[logical])==set(range(31))
        for value in range(31):
            assert block_channels[logical,value]==expected_channels[logical,value]
        assert set().union(*(block_channels[logical,value] for value in range(31)))==required
    assert set().union(*(block_channels[logical,30] for logical in range(10)))==required
    assert {block_activity[logical][30] for logical in range(10)}=={1}
    assert {block_activity[logical][0] for logical in range(10)}=={3,4}
    def low_bin_k10_se(activity_bin):
        pooled=sum(block_activity[logical][activity_bin] for logical in range(10))
        leaves=[(pooled-block_activity[logical][activity_bin])/(9*120)
                for logical in range(10)]
        mean=sum(leaves)/10
        return math.sqrt(9.0/10.0*sum((value-mean)**2 for value in leaves))
    low_bin_se={str(value):low_bin_k10_se(value) for value in (0,1)}
    assert all(value>0 and math.isfinite(value) for value in low_bin_se.values())
    # The frozen percentile threshold is the first ascending integer whose
    # cumulative weight reaches (100-p)/100 of the tune total. Identical
    # support in every block makes each K9 complement's boundaries exact.
    def thresholds(distribution):
        total = sum(distribution.values())
        result = []
        for percentile in percentiles:
            target = (100-percentile)/100 * total
            running = 0
            for activity in range(31):
                running += distribution[activity]
                if running >= target:
                    result.append(activity)
                    break
        return result
    nominal = Counter()
    for distribution in block_activity.values():
        nominal.update(distribution)
    boundary = thresholds(nominal)
    assert len(set(boundary)) >= 8
    for omitted in range(10):
        complement = nominal - block_activity[omitted]
        assert thresholds(complement)==boundary,(tune,omitted,boundary,thresholds(complement))
    # Reproduce statistics.hpp::AuditActivityThreshold's strict t9 margins
    # independently from the retained activity rows, including K10 variance.
    t9_margins = {}
    for percentile,threshold in zip(percentiles[1:-1],boundary[1:-1]):
        fraction=(100.0-percentile)/100.0
        below=[]
        through=[]
        for logical in range(10):
            distribution=block_activity[logical]
            total=sum(distribution.values())
            below.append(sum(distribution[n] for n in range(threshold))-fraction*total)
            through.append(sum(distribution[n] for n in range(threshold+1))-fraction*total)
        sides=[]
        for margins,positive in ((below,False),(through,True)):
            pooled=sum(margins)
            mean=pooled/10.0
            variance=10.0/9.0*sum((x-mean)**2 for x in margins)
            signed_margin=pooled if positive else -pooled
            assert signed_margin > 2.2621571628540993*math.sqrt(variance),(tune,percentile,margins)
            assert signed_margin > 1e-6,(tune,percentile,"numeric margin")
            sides.append({"pooled_signed_margin":signed_margin,"K10_variance":variance})
        t9_margins[str(percentile)]={"below":sides[0],"through":sides[1]}
    classes=list(zip(percentiles[:-1],percentiles[1:]))
    class_support={}
    for low_percent,high_percent in classes:
        low=0 if high_percent==100 else boundary[percentiles.index(high_percent)]+1
        high=4095 if low_percent==0 else boundary[percentiles.index(low_percent)]
        events=sum(nominal[n] for n in range(low,min(high,30)+1))
        assert events>0,(tune,low_percent,high_percent,low,high)
        class_support[f"{low_percent}-{high_percent}"]={"low":low,"high":high,"events":events}
    assert class_support["0-1"]["low"]==30
    assert class_support["0-1"]["events"]==10
    counts = Counter()
    block_counts = defaultdict(Counter)
    optional = Counter()
    above = 0
    for r in file.Get("triggers"):
        if int(r.heavy_index)==20 and int(r.rejection_mask)==0:
            counts[("trigger",heavy[int(r.event_id),20][0])] += 1
    for r in file.Get("pairs"):
        if int(r.trigger_heavy_index)!=20:
            continue
        tid = int(r.event_id)
        trigger = heavy[tid,20]
        associate = heavy[tid,int(r.associate_heavy_index)]
        if abs(trigger[1]) > 4 or abs(associate[1]) > 4:
            continue
        key = (trigger[0],associate[0])
        if key not in PARENTS:
            continue
        counts[key] += 1
        block_counts[(tid >> 32) & 0x3fff][key] += 1
        if float(r.trigger_pt)>=0.5 and float(r.associate_pt)>=0.5:
            optional[key] += 1
        if float(r.associate_pt)>float(r.trigger_pt):
            above += 1
    # Exact event atoms prove both optional equality and above-trigger support.
    eq_id = event_id(tune,0,4)
    above_id = event_id(tune,0,0)
    equality = [(float(r.trigger_pt),float(r.associate_pt)) for r in file.Get("pairs")
                if int(r.event_id)==eq_id and int(r.trigger_heavy_index)==20
                and int(r.associate_heavy_index)==21]
    larger = [(float(r.trigger_pt),float(r.associate_pt)) for r in file.Get("pairs")
              if int(r.event_id)==above_id and int(r.trigger_heavy_index)==20
              and int(r.associate_heavy_index)==21]
    assert len(equality)==len(larger)==1
    assert equality[0] == (0.5,0.5)
    assert larger[0][1] > larger[0][0]
    file.Close()
    return counts,optional,above,boundary,t9_margins,class_support,low_bin_se,block_counts


def sparse_equality(base):
    # Deliberately do not call collection.read, verify_merge_lineage, or the
    # production sparse comparator.  This is an independent read of the two
    # declared indexes and their ROOT objects.
    sharded = json.loads((base/"SHARDED.json").read_text())
    merged = json.loads((base/"merged/index.json").read_text())
    assert sharded["layout"]=="SHARDED" and merged["layout"]=="MERGED"
    assert sharded["scientific_identity_sha256"]==merged["scientific_identity_sha256"]
    ROOT = c._root()
    families=tuple(sorted(json.loads((ROOT_DIR/"config/query.json").read_text())["sparse"]))
    block_count=sharded["block_count"]

    def cells(histogram):
        coordinates=array("i",[0]*histogram.GetNdimensions())
        for index in range(histogram.GetNbins()):
            value=histogram.GetBinContent(index,coordinates)
            variance=histogram.GetBinError2(index)
            assert math.isfinite(value) and math.isfinite(variance) and variance>=0
            yield tuple(coordinates),value,variance

    def geometry(histogram):
        assert histogram and histogram.GetCalculateErrors()
        result=[]
        for dimension in range(histogram.GetNdimensions()):
            axis=histogram.GetAxis(dimension)
            stored=axis.GetXbins()
            assert stored.GetSize()==axis.GetNbins()+1
            result.append((axis.GetName(),axis.GetTitle(),
                tuple(stored.At(edge) for edge in range(stored.GetSize())),
                tuple(axis.GetBinLabel(bin_) for bin_ in range(axis.GetNbins()+2))))
        return tuple(result)

    result = {}
    for family in families:
        for tune,ordinal in sharded["tune_ordinals"].items():
            expected = {}
            entries = 0
            reference_geometry=None
            for shard in sharded["shards"]:
                file = ROOT.TFile.Open(shard["query_root"]["path"])
                hist = file.Get("sparse_"+family)
                current_geometry=geometry(hist)
                if reference_geometry is None:reference_geometry=current_geometry
                assert current_geometry==reference_geometry,(family,tune,"source geometry")
                if {m["tune"] for m in shard["members"]}=={tune}:
                    entries += hist.GetEntries()
                for coordinate,value,variance in cells(hist):
                    if coordinate[0]!=ordinal+1:continue
                    old = expected.get(coordinate,(0.0,0.0))
                    expected[coordinate]=(old[0]+value,old[1]+variance)
                file.Close()
            parts=[p for p in merged["partitions"] if p["tune"]==tune]
            assert len(parts)==1,(family,tune,"partition inventory")
            part=parts[0]
            inventory=part["sparse_objects"][family]
            blocks=[item["block"] for item in inventory]
            names=[item["name"] for item in inventory]
            assert blocks==list(range(1,block_count+1)),(family,tune,"block inventory")
            assert len(names)==len(set(names)),(family,tune,"duplicate object inventory")
            assert names==[f"sparse_{family}__block_{block:02d}" for block in blocks]
            file = ROOT.TFile.Open(part["root"]["path"])
            declared={item["name"] for objects in part["sparse_objects"].values() for item in objects}
            keys=[key.GetName() for key in file.GetListOfKeys()]
            assert len(keys)==len(set(keys)) and set(keys)==declared,(family,tune,"ROOT object inventory")
            actual={}
            actual_entries=0
            for item in inventory:
                hist=file.Get(item["name"])
                assert geometry(hist)==reference_geometry,(family,tune,item["block"],"geometry")
                actual_entries+=hist.GetEntries()
                for coord,value,variance in cells(hist):
                    assert coord[0]==ordinal+1 and coord[1]==item["block"], \
                        (family,tune,item["block"],coord,"coordinate domain")
                    old=actual.get(coord,(0.0,0.0))
                    actual[coord]=(old[0]+value,old[1]+variance)
            assert set(expected)==set(actual),(family,tune,"coordinates")
            for coord in expected:
                assert all(math.isclose(x,y,rel_tol=1e-12,abs_tol=1e-12)
                           for x,y in zip(expected[coord],actual[coord])),(family,tune,coord)
            assert actual_entries==entries,(family,tune,"entries")
            result[f"{tune}:{family}"]={"occupied_cells":len(actual),"entries":entries}
            file.Close()
    return result


def main():
    base, report_path = admitted_paths()
    report={"schema":"nonzero_chain_v22_independent_row_oracle_v1","by_tune":{}}
    for ordinal,tune in enumerate(TUNES):
        expected,expected_optional,expected_above,expected_blocks=expected_rows(ordinal)
        observed,observed_optional,observed_above,boundaries,margins,classes,p1_se,observed_blocks=observed_rows(ordinal,base)
        for key in PARENTS:
            assert observed[key]==expected[key],(tune,key,expected[key],observed[key])
            assert observed_optional[key]==expected_optional[key],(tune,key,"optional")
        for trigger in (421,4122,521,5122):
            assert expected[("trigger",trigger)]==observed[("trigger",trigger)]==300
        assert expected_above==observed_above and observed_above>0
        for logical in range(10):
            for key in PARENTS:
                assert expected_blocks[logical][key]==observed_blocks[logical][key],(tune,logical,key)
        balances={}
        for name,(os_key,ss_key) in BALANCES.items():
            per_block=[observed_blocks[logical][os_key]-observed_blocks[logical][ss_key]
                       for logical in range(10)]
            pooled=sum(per_block)
            leaves=[pooled-per_block[logical] for logical in range(10)]
            assert min(per_block)>0 and min(leaves)>0,(tune,name,per_block,leaves)
            balances[name]={"pooled_net":pooled,"by_original_block":per_block,
                            "minimum_delete_one_K9_net":min(leaves)}
        report["by_tune"][tune]={
            "paper_trigger_counts":{str(x):observed[("trigger",x)] for x in (421,4122,521,5122)},
            "nominal_and_all_K9_percentile_thresholds":boundaries,
            "t9_strict_margins":margins,
            "eleven_class_support":classes,
            "per_block_activity_values":31,
            "top_tail_paper_trigger_channels_across_blocks":4,
            "activity_0_block_counts":[3 if logical%2 else 4 for logical in range(10)],
            "P1_low_bin_independent_K10_SE":p1_se,
            "signed_reference_and_base_category_nets":balances,
            "selected_pair_counts":{f"{t}:{a}":observed[t,a] for t,a in PARENTS},
            "optional_equal_minima_pair_counts":{f"{t}:{a}":observed_optional[t,a] for t,a in PARENTS},
            "above_trigger_pt_selected_pairs":observed_above,
            "charm_D0_OS_minus_SS":observed[421,-421]-observed[421,421],
            "beauty_Bplus_OS_minus_SS":observed[521,-521]-observed[521,521],
            "p8_charm_baryon_parent":observed[421,-4122],
            "p8_beauty_baryon_parent":observed[521,5122],
        }
    report["sparse_physical_equality"]=sparse_equality(base)
    report["scientific_identity_sha256"]=json.loads((base/"SHARDED.json").read_text())["scientific_identity_sha256"]
    publish_report(report_path, report)
    print(json.dumps(report,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
