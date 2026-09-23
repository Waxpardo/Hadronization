"""Cold drawing boundary mutants; no published result cache is required."""

import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "phasea_plot_cold_contract", ROOT / "pipeline/plot/run.py")
plot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(plot)


class ColdDrawingBoundary(unittest.TestCase):
    def test_species_display_order_groups_content_and_preserves_signed_membership(self):
        charm = ['-411', '-421', '-431', '-4122', '-4112', '-4212',
                 '-4222', '-4132', '-4232']
        beauty = ['-521', '-511', '-531', '-541', '5122', '5112',
                  '5222', '5132', '5232']
        self.assertEqual(plot.species_display_order(charm),
                         ['-421','-411','-431','-4122','-4212','-4112',
                          '-4222','-4232','-4132'])
        self.assertEqual(plot.species_display_order(beauty),
                         ['-521','-511','-531','-541','5122','5222',
                          '5112','5232','5132'])
        for species in (charm, beauty):
            opposite = [str(-int(pdg)) for pdg in species]
            self.assertEqual(plot.species_display_order(opposite),
                [str(-int(pdg)) for pdg in plot.species_display_order(species)])
            self.assertCountEqual(plot.species_display_order(species),species)
        with self.assertRaisesRegex(ValueError, 'baryon-content'):
            plot.species_display_order(['999999'])

    def test_joined_columns_have_equal_width_and_do_not_change_data(self):
        import copy
        panels=[]
        for index in range(2):
            panels.append(dict(id=str(index),geometry=[index*.5,.3,(index+1)*.5,.9],
                margins=[.2,.035,0.,.17],y_range=[.1,10.],log_y=True,
                y_title='Balancing yield',title='Trigger '+str(index),
                series=[{'points':[{'semantic_id':str(index),'y':1.,'error':.2}]}]))
        original=copy.deepcopy(panels)
        plot.join_paired_columns([{'panels':panels}])
        left,right=panels
        self.assertEqual(left['geometry'][2],right['geometry'][0])
        self.assertEqual((left['margins'][1],right['margins'][0]),(0.,0.))
        self.assertAlmostEqual((left['geometry'][2]-left['geometry'][0])*
            (1-left['margins'][0]),(right['geometry'][2]-right['geometry'][0])*
            (1-right['margins'][1]))
        self.assertEqual(right['y_title'],'')
        for actual,before in zip(panels,original):
            for field in ('series','y_range','log_y','title'):
                self.assertEqual(actual[field],before[field])
        right['y_range']=[.1,11.]
        with self.assertRaisesRegex(ValueError,'share their y axis'):
            plot.join_paired_columns([{'panels':panels}])

    def test_joined_baryon_ratio_panels_keep_each_signed_identity(self):
        panels=[dict(geometry=[i*.5,.3,(i+1)*.5,.9],margins=[.2,.035,0.,.17],
            y_range=[0.,1.],log_y=False,title='trigger '+str(i),
            y_title='signed ratio '+str(i)) for i in range(2)]
        plot.join_paired_columns([{'panels':panels}])
        self.assertEqual(panels[0]['y_title'],'Balancing yield ratio')
        self.assertEqual(panels[1]['y_title'],'')
        for i,panel in enumerate(panels):
            self.assertIn('signed ratio '+str(i),panel['title'])

    def test_public_cold_command_imports_reader_from_external_cwd(self):
        with tempfile.TemporaryDirectory(dir=ROOT.parent) as directory:
            external = Path(directory)
            result = subprocess.run([
                sys.executable, str(ROOT / 'hadronization'), 'plot',
                'render-cold', '--numerics-root',
                str(external / 'missing.root'), '--expected-root-sha256',
                '0' * 64, '--expected-value-sha256', '0' * 64,
                '--work-dir', str(external / 'work'), '--output',
                str(external / 'output')], cwd=external,
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn('v4 ROOT differs from trusted physical hash', result.stderr)
            self.assertNotIn('ModuleNotFoundError', result.stderr)

    def test_p1_owner_inset_is_large_lower_left(self):
        config, _ = plot.checked_plot_config(ROOT / "config/plot.json")
        self.assertEqual(config["layout"]["p1_inset_geometry"],
                         [.15, .05, .62, .48])
        self.assertEqual(config['layout']['correlation_view'],
                         'monash_pair_sign')
        self.assertEqual(config['presets']['paper_default']['trigger_pdgs'][0],
                         421)

    def test_p1_nested_inset_preserves_reference_physical_aspect(self):
        relative=[.15,.05,.62,.48]
        original=plot.prelean_inset_geometry(relative,[0.,.31,1.,1.],1800,1650)
        for actual,expected in zip(original,[.15,.31+.05*.69,.62,.31+.48*.69]):
            self.assertAlmostEqual(actual,expected)
        original_aspect=(original[2]-original[0])*1800/((original[3]-original[1])*1650)
        for width,height,parent in ((1050,1360,[0.,.26,1.,.98]),
                                     (1050,1360,[0.,0.,1.,.98])):
            mapped=plot.prelean_inset_geometry(relative,parent,width,height)
            self.assertAlmostEqual((mapped[2]-mapped[0])*width/
                                   ((mapped[3]-mapped[1])*height),original_aspect)
            self.assertAlmostEqual((mapped[1]-parent[1])/(parent[3]-parent[1]),.05)

    def test_centers_only_teaching_discloses_hidden_nonzero_errors(self):
        point={'state':'DRAW','error':.2}
        panel={'id':'correlation.teaching.421.identified',
               'uncertainty_display':'CENTERS_ONLY',
               'series':[{'points':[point]}]}
        page={'role':'correlations.charm','panels':[panel],
              'information':'Exact-zero SE saved in ROOT'}
        self.assertIn('lacks visible SE disclosure',
                      plot.review_uncertainty_presentation(page))
        page['information']=(
            'P2-P8: no final-hadron pT floor; '+
            plot.CORRELATION_CENTER_ONLY_DISCLOSURE)
        self.assertIsNone(plot.review_uncertainty_presentation(page))
        panel['uncertainty_display']='STANDARD'
        page['information']=''
        self.assertIsNone(plot.review_uncertainty_presentation(page))
        point['error']=0.
        self.assertIn('lacks retained finite-MC error',
                      plot.review_uncertainty_presentation(page))

    def test_dplus_and_all_tune_are_explicit_presentation_alternates(self):
        config, _ = plot.checked_plot_config(ROOT / "config/plot.json")
        dplus, _ = plot.checked_plot_config(ROOT / "config/plot-dplus.json")
        all_tune, _ = plot.checked_plot_config(ROOT / "config/plot-all-tune.json")
        self.assertEqual(dplus['presets']['paper_default']['trigger_pdgs'],
                         [411, 4122, 521, 5122])
        self.assertEqual(dplus['layout']['correlation_view'],
                         'monash_pair_sign')
        self.assertEqual(all_tune['presets']['paper_default']['trigger_pdgs'],
                         [421, 4122, 521, 5122])
        self.assertEqual(all_tune['layout']['correlation_view'],
                         'all_tune_ratio')
        config['presets']['paper_default']['trigger_pdgs'][0] = 411
        config['presets']['paper_default']['baryon_meson_trigger_pdgs'][0] = 411
        config['layout']['correlation_view'] = 'all_tune_ratio'
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            path = Path(directory) / 'plot.json'
            path.write_text(json.dumps(config), encoding='utf-8')
            checked, _ = plot.checked_plot_config(path)
        self.assertEqual(checked['layout']['correlation_view'],
                         'all_tune_ratio')

    def test_p1_authenticated_extent_retains_observed_tail(self):
        series = [{"points": [
            {"state": "DRAW", "y": 0.3, "error": 0.01,
             "support_low": 0., "support_high": 1.},
            {"state": "DRAW", "y": 0.0002, "error": None,
             "support_low": 163., "support_high": 164.},
            {"state": "DRAW", "y": 0., "error": 0.,
             "support_low": 4095., "support_high": 4096.},
        ]}]
        main, inset = plot.checked_p1_occupied_support(
            {"low": 0., "positive_low": 1., "high": 164.}, series)
        self.assertEqual(main, [0., 164.])
        self.assertEqual(inset, [1., 164.])
        with self.assertRaisesRegex(ValueError, "crops materialized tail"):
            plot.checked_p1_occupied_support(
                {"low": 0., "positive_low": 1., "high": 163.}, series)
        with self.assertRaisesRegex(ValueError, "geometry"):
            plot.checked_p1_occupied_support(
                {"low": 1., "positive_low": 1., "high": 164.}, series)

    def test_p1_finite_withheld_ratio_error_has_visible_disclosure(self):
        points = [
            {'state': 'DRAW', 'y': 1.2, 'error': .1},
            {'state': 'DRAW', 'y': .8, 'error': None},
            {'state': 'MISSING', 'y': None, 'error': None},
        ]
        self.assertEqual(plot.p1_ratio_uncertainty_note(
            'multiplicity.composite', 'lower.ratio', points, 'old note'),
            plot.P1_WITHHELD_SE_DISCLOSURE)
        self.assertNotIn('?', plot.P1_WITHHELD_SE_DISCLOSURE)
        self.assertEqual(plot.p1_ratio_uncertainty_note(
            'multiplicity.composite', 'upper.distribution', points,
            'old note'), 'old note')

    def test_p1_paper_range_uses_complete_reference_support(self):
        series = [
            {"tune": "MONASH", "points": [
                {"state": "DRAW", "y": 0.3, "support_high": 1.},
                {"state": "DRAW", "y": 1e-8, "support_high": 374.},
                {"state": "MISSING", "y": None, "support_high": 4096.},
            ]},
            {"tune": "CLOSEPACKING", "points": [
                {"state": "DRAW", "y": 1e-8, "support_high": 2109.},
            ]},
        ]
        self.assertEqual(
            plot.p1_reference_display_high(series, "MONASH"), 374.)
        with self.assertRaisesRegex(ValueError, "no positive occupied"):
            plot.p1_reference_display_high(series, "ABSENT")

    def test_category_order_preserves_signed_five_channel_beauty(self):
        order = ["-521", "-511", "-531", "-541", "5122"]
        self.assertEqual(plot.checked_category_order(
            order, set(order), False, "balancing.integrated.beauty", "521"),
            order)
        self.assertEqual(plot.checked_category_order(
            order, {"-521", "-511"}, True,
            "balancing.integrated.beauty", "521"), order)
        for mutant in (order[:-1], order[:-1] + ["-5122"],
                       order[:-1] + ["-521"]):
            with self.subTest(mutant=mutant), self.assertRaises(ValueError):
                plot.checked_category_order(
                    mutant, set(order), False,
                    "balancing.integrated.beauty", "521")

    def test_correlation_requires_all_three_component_comparisons(self):
        components = ("OS", "SS", "OS_MINUS_SS")
        rows = [{"trigger_pdg": "411", "component": component,
                 "tune": "MONASH", "reference_tune": ""}
                for component in components]
        rows += [{"trigger_pdg": "411", "component": component,
                  "tune": "JUNCTIONS", "reference_tune": "MONASH"}
                 for component in components]
        self.assertTrue(plot.checked_tune_ratio_layout(
            ["MONASH", "JUNCTIONS"], "MONASH", rows,
            "correlations.charm"))
        with self.assertRaisesRegex(ValueError, "OS/SS/net"):
            plot.checked_tune_ratio_layout(
                ["MONASH", "JUNCTIONS"], "MONASH", rows[:-1],
                "correlations.charm")

    def test_reference_correlation_captions_use_registered_component_sign(self):
        for expected in (
                {421: (-421, 421), 4122: (-421, 421),
                 521: (-521, 521), 5122: (521, -521)},
                {411: (-411, 411), 4122: (-411, 411),
                 521: (-521, 521), 5122: (521, -521)}):
            registered = []
            for trigger, (opposite, same) in expected.items():
                for sign, associate in ((-1, opposite), (1, same)):
                    registered.append({"trigger_pdg": trigger, "sign": sign,
                                       "associate_pdg": associate,
                                       "reference_meson_pdg": abs(associate)})
            for trigger, (opposite, same) in expected.items():
                self.assertEqual(plot.correlation_reference_partners(
                    registered, trigger), {"OS": opposite, "SS": same})
            with self.assertRaisesRegex(ValueError, "reference pair"):
                plot.correlation_reference_partners(registered[:-1], 5122)

    def test_charm_presentation_preset_must_match_s_science_recipe(self):
        d0, _ = plot.checked_plot_config(ROOT / 'config/plot.json')
        dplus, _ = plot.checked_plot_config(ROOT / 'config/plot-dplus.json')

        def science_scope(charm):
            return {'ordered_triggers': [charm, 4122, 521, 5122],
                    'ordered_associate_pairs': [
                        {'trigger_pdg': trigger, 'sector': 'CHARM',
                         'reference_meson_pdg': -charm,
                         'associate_pdg': associate, 'sign': sign}
                        for trigger in (charm, 4122)
                        for sign, associate in (('OS', -charm),
                                                ('SS', charm))],
                    'roles': [{'role_id':
                               'balancing.baryon_meson.activity',
                               'required_curve_keys': [{'trigger_pdg': charm,
                                 'associate_pdg': -4122,
                                 'reference_pdg': -charm}]}]}

        d0_scope = science_scope(421)
        dplus_scope = science_scope(411)
        plot.checked_charm_recipe_binding(d0_scope, d0)
        plot.checked_charm_recipe_binding(dplus_scope, dplus)
        with self.assertRaisesRegex(ValueError, 'ordered triggers'):
            plot.checked_charm_recipe_binding(d0_scope, dplus)
        wrong_reference = json.loads(json.dumps(d0_scope))
        wrong_reference['ordered_associate_pairs'][0][
            'reference_meson_pdg'] = -411
        with self.assertRaisesRegex(ValueError, 'reference meson'):
            plot.checked_charm_recipe_binding(wrong_reference, d0)
        wrong_sign = json.loads(json.dumps(d0_scope))
        wrong_sign['ordered_associate_pairs'][0]['associate_pdg'] = 421
        with self.assertRaisesRegex(ValueError, 'signed pairs'):
            plot.checked_charm_recipe_binding(wrong_sign, d0)
        wrong_p8 = json.loads(json.dumps(d0_scope))
        wrong_p8['roles'][0]['required_curve_keys'][0][
            'reference_pdg'] = -411
        with self.assertRaisesRegex(ValueError, 'P8 reference'):
            plot.checked_charm_recipe_binding(wrong_p8, d0)

    def test_paper_requires_inclusive_no_floor_no_diagonal_profile(self):
        d0, _ = plot.checked_plot_config(ROOT / 'config/plot.json')
        dplus, _ = plot.checked_plot_config(ROOT / 'config/plot-dplus.json')
        cut = {'domain': 'PHYSICAL', 'units': 'GeV', 'low': None,
               'high': None, 'low_operator': None, 'high_operator': None}
        profile = {'id': 'inclusive',
                   'relative_pt': 'NONE',
                   'minimum_hierarchy': 'NONE',
                   'trigger_pt': dict(cut), 'associate_pt': dict(cut)}
        payload = {'schema': 'hadronization_projection_result_v4',
                   'request_echo': {'scope': {'roles': [{
                       'role_id': 'correlations.charm',
                       'required_curve_keys': [{
                           'profile_id': 'inclusive'}]}, {
                       'role_id': 'balancing.baryon_meson.activity',
                       'required_curve_keys': [{
                           'profile_id': 'inclusive'}]}]}}}
        caption = plot.checked_paper_pair_profile(payload, d0, profile)
        self.assertIn('no final-hadron #it{p}_{T} floor', caption)
        self.assertNotIn('#geq', caption)
        self.assertIn('eligible singles', caption)
        self.assertEqual(plot.checked_paper_pair_profile(
            payload, dplus, profile), caption)
        for mutation, message in (
                (dict(profile, relative_pt='TRIGGER_GE_ASSOCIATE'),
                 'no-diagonal'),
                (dict(profile, trigger_pt=dict(cut, low='0x1p-1')),
                 'fixed pT cut')):
            with self.assertRaisesRegex(ValueError, message):
                plot.checked_paper_pair_profile(payload, d0, mutation)
        wrong_role = json.loads(json.dumps(payload))
        wrong_role['request_echo']['scope']['roles'][0][
            'required_curve_keys'][0]['profile_id'] = 'trigger_ge_associate'
        with self.assertRaisesRegex(ValueError, 'different pair profile'):
            plot.checked_paper_pair_profile(wrong_role, d0, profile)

    def test_negative_center_and_withheld_error_remain_distinct(self):
        row = {"family": "balancing", "quantity": "os_minus_ss_per_trigger",
               "value": "-2", "value_status": "AVAILABLE",
               "finite_mc_error": "", "uncertainty_status":
               "WITHHELD_UNCERTAINTY", "bin_index": "", "bin_low": "",
               "bin_high": "", "axis": "", "reference_tune": "",
               "tune": "MONASH"}
        value = plot._render_numbers(row)
        self.assertEqual(value["value"], -2.)
        self.assertIsNone(value["finite_mc_error"])
        wrong = dict(row, uncertainty_status="AVAILABLE")
        with self.assertRaisesRegex(ValueError, "uncertainty/status"):
            plot._render_numbers(wrong)

    def test_finite_v4_covariance_leaf_cannot_become_a_plotted_error(self):
        curve = {
            "role_id": "balancing.integrated.charm",
            "quantity": "os_minus_ss_per_trigger",
            "tune_id": "MONASH", "reference_tune_id": None,
            "profile_id": "inclusive", "activity_id": None,
            "class_id": None, "trigger_pdg": 421,
            "associate_pdg": -4122, "reference_pdg": -421,
            "component": "NONE", "axis_id": None,
        }
        point = {"semantic_id": "diagnostic-only", "key": {
            "curve": curve, "bins": []}, "units": "yield / trigger",
            "center": "0x1p-1", "center_status": "AVAILABLE",
            "standard_error": None,
            "uncertainty_status": "WITHHELD_UNCERTAINTY",
            "reasons": ["INCOMPLETE_BLOCK_COVERAGE"]}
        payload = {"points": [point], "covariance": [{
            "independent_families": [{
                "finite_mask": [[True]], "usable_mask": [False],
                "complements": [["0x1p-2"]]}]}]}
        row = plot.typed_point_rows(payload)[0]
        self.assertEqual(row["finite_mc_error"], "")
        self.assertIsNone(plot._render_numbers(row)["finite_mc_error"])
        point["standard_error"] = "0x1p-2"
        leaked = plot.typed_point_rows(payload)[0]
        with self.assertRaisesRegex(ValueError, "uncertainty/status"):
            plot._render_numbers(leaked)

    def test_focused_extremes_preserve_all_class_canonical_page(self):
        classes = [{"id": "0", "integrated": True,
                    "percentile_interval": [0., 100.]}]
        classes += [{"id": str(index), "integrated": False,
                     "percentile_interval": [float(index-1)*9.,
                                             float(index)*9.]}
                    for index in range(1, 11)]
        classes.append({"id": "11", "integrated": False,
                        "percentile_interval": [90., 100.]})
        self.assertEqual(plot.selected_extreme_class_ids(classes),
                         ["1", "11"])
        panel = {"id": "upper.411", "series": [
            {"class_id": str(index), "points": [{"state": "DRAW",
             "y": float(index), "error": None}]}
            for index in range(1, 12)],
            "log_y": True, "x_range": [.5, 3.5],
            "y_range": [0.1, 20.], "guides": [], "note": "",
            "status": "AVAILABLE"}
        canonical = {"role": "balancing.activity.charm",
                     "panels": [panel], "title": "all classes"}
        context = SimpleNamespace(
            tunes=["MONASH", "JUNCTIONS", "CLOSEPACKING"],
            classes=classes, package_state="VALIDATED_PARTIAL",
            campaign_state="PARTIAL_SAMPLE",
            numerics_schema="hadronization_projection_result_v3_g9_science")
        pages = plot.focused_extreme_pages([canonical], context, .08)
        self.assertEqual(len(pages), 1)
        self.assertEqual([series["class_id"] for series in
                          pages[0]["panels"][0]["series"]], ["1", "11"])
        self.assertEqual(len(canonical["panels"][0]["series"]), 11)
        self.assertIn("supplemental", pages[0]["filename"])

    def test_extreme_emphasis_uses_typed_intervals_not_caption(self):
        classes = [
            {"id": "0", "integrated": True,
             "percentile_interval": [0., 100.]},
            {"id": "7", "integrated": False,
             "percentile_interval": [3., 14.]},
            {"id": "2", "integrated": False,
             "percentile_interval": [14., 65.]},
            {"id": "9", "integrated": False,
             "percentile_interval": [65., 97.]},
        ]
        self.assertEqual(plot.selected_extreme_class_ids(classes),
                         ["7", "9"])
        self.assertEqual([plot.activity_emphasis(
            "balancing.activity.charm", class_id, classes)
            for class_id in ("0", "7", "2", "9")],
            ["NORMAL", "EXTREME", "NORMAL", "EXTREME"])

    def test_baryon_meson_axis_names_exact_signed_particle_yields(self):
        labels = {'-4122': '#bar{#it{#Lambda}}_{c}^{-}',
                  '-421': '#bar{#it{D}}^{0}'}
        rows = [{'associate_pdg': '-4122', 'reference_pdg': '-421'},
                {'associate_pdg': '-4122', 'reference_pdg': '-421'}]
        self.assertEqual(plot.exact_particle_ratio_title(
            rows, labels.__getitem__),
            '#it{Y}(#bar{#it{#Lambda}}_{c}^{-}) / #it{Y}(#bar{#it{D}}^{0})')
        with self.assertRaisesRegex(ValueError, 'mixes particle yield ratios'):
            plot.exact_particle_ratio_title(rows + [{
                'associate_pdg': '5122', 'reference_pdg': '-521'}],
                labels.get)

    def test_sparse_protocol_fixture_cannot_pass_style_review_gate(self):
        classes = [{"id": "0", "integrated": True,
                    "percentile_interval": [0., 100.]},
                   {"id": "1", "integrated": False,
                    "percentile_interval": [0., 10.]},
                   {"id": "2", "integrated": False,
                    "percentile_interval": [90., 100.]}]
        context = SimpleNamespace(
            campaign_state="PARTIAL_SAMPLE",
            tunes=["MONASH", "JUNCTIONS", "CLOSEPACKING"],
            reference_tune="MONASH", classes=classes)
        config, _ = plot.checked_plot_config(ROOT / "config/plot.json")
        with self.assertRaisesRegex(ValueError,
                                    "synthetic review coverage failed"):
            plot.review_packet_coverage({"pages": []}, context, config)

    def test_category_tunes_and_classes_share_scientific_centers(self):
        tunes = ["MONASH", "JUNCTIONS", "CLOSEPACKING"]
        for tune in tunes:
            self.assertEqual(plot.categorical_display_x(
                7., "balancing.baryon_meson.activity", "7", tune,
                tunes, ["7"], {}, ratio=tune != "MONASH"), 7.)
            self.assertEqual(plot.categorical_display_x(
                3., "balancing.integrated.charm", "0", tune,
                tunes, ["0"], {}, ratio=tune != "MONASH"), 3.)

    def test_joined_ratio_frames_share_edges_and_drop_lower_title(self):
        upper={"id":"upper.411","geometry":[0.,.31,.5,.89],
               "margins":[.2,.035,.1,.17],"x_range":[.5,3.5]}
        lower={"id":"lower.411","geometry":[0.,0.,.5,.30],
               "margins":[.2,.035,.43,.17],"x_range":[.5,3.5],
               "title":"duplicate"}
        pages=[{"role":"balancing.integrated.charm",
                "panels":[upper,lower]}]
        plot.join_ratio_pads(pages)
        self.assertEqual(upper['geometry'][1],lower['geometry'][3])
        self.assertEqual(upper['margins'][2],0.)
        self.assertEqual(lower['margins'][3],0.)
        self.assertEqual(lower['geometry'][1],.08)
        self.assertEqual(lower['title'],'')
        self.assertEqual(upper['x_range'],lower['x_range'])

    def test_joined_beauty_net_ratio_has_tick_label_headroom(self):
        upper={"id":"correlation.main.521.OS_MINUS_SS",
               "geometry":[0.,.45,.5,.69],"margins":[.08,.02,0.,.1],
               "x_range":[-1.,4.]}
        lower={"id":"correlation.compare.521.OS_MINUS_SS",
               "geometry":[0.,.32,.5,.44],"margins":[.08,.02,.13,0.],
               "x_range":[-1.,4.],"y_range":[.95,1.64],"title":""}
        plot.join_ratio_pads([{"role":"correlations.beauty",
                               "panels":[upper,lower]}])
        self.assertEqual(upper['geometry'][1],lower['geometry'][3])
        self.assertEqual(lower['y_range'][1],1.8)

    def test_p8_shared_x_frames_join_without_a_gap(self):
        upper={"id":"upper.charm.421", "geometry":[0.,.32,.5,.89],
               "margins":[.20,.035,.29,.21], "x_range":[.5,3.5]}
        lower={"id":"lower.charm.421", "geometry":[0.,0.,.5,.32],
               "margins":[.20,.035,.29,.21], "x_range":[.5,3.5],
               "title":"old"}
        plot.join_ratio_pads([{"role":"balancing.baryon_meson.activity",
                               "panels":[upper,lower]}])
        self.assertEqual(upper['geometry'][1], lower['geometry'][3])
        self.assertEqual(upper['margins'][2], 0.)
        self.assertEqual(lower['margins'][3], 0.)
        self.assertEqual(lower['geometry'][1], .08)
        self.assertEqual(upper['x_range'], lower['x_range'])
        self.assertEqual(lower['title'], '')

    def test_activity_pages_are_three_tune_rows_plus_one_shared_ratio_row(self):
        tunes = ['MONASH', 'JUNCTIONS', 'CLOSEPACKING']
        def panel(id_, left, right, series):
            return {'id': id_, 'geometry': [left, .3, right, .89],
                    'title': id_, 'series': series,
                    'margins': [.2, .035, .1, .17],
                    'y_title': 'old'}
        series = [{'tune': tune} for tune in tunes]
        source = {'role': 'balancing.activity.charm', 'height': 1250,
                  'panels': [
                      panel('upper.421', 0., .5, series),
                      panel('upper.4122', .5, 1., series),
                      panel('lower.421', 0., .5, series[1:]),
                      panel('lower.4122', .5, 1., series[1:])]}
        page = plot.tune_separated_activity_pages([source], tunes)[0]
        self.assertEqual([item['id'] for item in page['panels']], [
            'upper.MONASH.421', 'upper.MONASH.4122',
            'upper.JUNCTIONS.421', 'upper.JUNCTIONS.4122',
            'upper.CLOSEPACKING.421', 'upper.CLOSEPACKING.4122',
            'lower.shared.421', 'lower.shared.4122'])
        for row, tune in zip((page['panels'][0:2], page['panels'][2:4],
                              page['panels'][4:6]), tunes):
            self.assertTrue(all({entry['tune'] for entry in item['series']} ==
                                {tune} for item in row))
        for column in (0, 1):
            stack = [page['panels'][column + 2 * row]
                     for row in range(4)]
            for upper, lower in zip(stack, stack[1:]):
                self.assertAlmostEqual(upper['geometry'][1],
                                       lower['geometry'][3])
        self.assertEqual({item['y_title'] for item in page['panels'][-2:]},
                         {'TUNE/MONASH'})
        self.assertEqual([item['title'] for item in page['panels'][:6]],
                         ['upper.421', 'upper.4122', '', '', '', ''])

        source['filename'] = 'supplemental.balancing.activity.charm.extremes.pdf'
        supplemental = plot.tune_separated_activity_pages([source], tunes)[0]
        self.assertEqual(supplemental['filename'], source['filename'])
        self.assertEqual(len(supplemental['panels']), 8)

    def test_tune_separated_baryon_meson_page_keeps_one_shared_ratio_row(self):
        tunes = ['MONASH', 'JUNCTIONS', 'CLOSEPACKING']
        def panel(id_, left, right, series):
            return {'id': id_, 'geometry': [left, .32, right, .89],
                    'title': id_, 'x_title': 'old', 'y_title': 'old',
                    'series': series, 'margins': [.2, .035, .29, .21]}
        series = [{'tune': tune} for tune in tunes]
        source = {'role': 'balancing.baryon_meson.activity',
                  'filename': 'balancing.baryon_meson.activity.pdf',
                  'height': 1250, 'panels': [
                      panel('upper.charm.421', 0., .5, series),
                      panel('upper.beauty.521', .5, 1., series),
                      panel('lower.charm.421', 0., .5, series[1:]),
                      panel('lower.beauty.521', .5, 1., series[1:])]}
        page = plot.tune_separated_baryon_meson_page([source], tunes)
        self.assertEqual(page['filename'],
                         'supplemental.balancing.baryon_meson.activity.by_tune.pdf')
        self.assertEqual(len(page['panels']), 8)
        self.assertEqual([item['id'] for item in page['panels'][-2:]],
                         ['lower.shared.charm.421',
                          'lower.shared.beauty.521'])
        self.assertTrue(all(item['x_title'] ==
            'Multiplicity Percentile Class (%)' for item in page['panels'][-2:]))
        self.assertTrue(all(item['y_title'] == 'TUNE/MONASH'
                            for item in page['panels'][-2:]))
        self.assertEqual([item['title'] for item in page['panels'][:6]],
                         ['upper.charm.421', 'upper.beauty.521',
                          '', '', '', ''])
        self.assertTrue(all(not series['legend_label']
                            for item in page['panels'][:-2]
                            for series in item['series']))

    def test_species_typography_covers_representative_mesons_and_baryons(self):
        self.assertEqual(plot.species_latex_label(421, 'Dzero'), '#it{D}^{0}')
        self.assertEqual(plot.species_latex_label(-421, 'Dzerobar'),
                         '#bar{#it{D}}^{0}')
        self.assertEqual(plot.species_latex_label(5212, 'PDG 5212'),
                         '#it{#Sigma}_{b}^{0}')
        self.assertEqual(plot.species_latex_label(-5212, 'PDG -5212'),
                         '#bar{#it{#Sigma}}_{b}^{0}')

    def test_left_and_right_facets_receive_one_shared_y_range(self):
        left = {'geometry': [0., .2, .5, .8], 'y_range': [1., 3.],
                'log_y': False}
        right = {'geometry': [.5, .2, 1., .8], 'y_range': [-2., 2.],
                 'log_y': False}
        plot.synchronize_paired_y_ranges([{'panels': [right, left]}])
        self.assertEqual(left['y_range'], [-2., 3.])
        self.assertEqual(right['y_range'], [-2., 3.])

    def test_activity_category_dividers_are_default_off(self):
        for name in ('plot.json', 'plot-dplus.json', 'plot-all-tune.json'):
            config, unused = plot.checked_plot_config(ROOT / 'config' / name)
            self.assertFalse(config['layout']['activity_category_dividers'])

    def test_owner_style_applies_to_preview_and_full_campaign(self):
        self.assertEqual(plot.p1_uncertainty_display(True),'DENSE_BAND')
        self.assertEqual(plot.p1_uncertainty_display(False),'DENSE_BAND')
        pages=[{'role':role,'title':'old heading',
                'information':'typed details','scientific_header':'old'}
               for role in ('multiplicity.composite','correlations.charm',
                            'spectra.signed_heavy')]
        preview=SimpleNamespace(target_analysis_caption='Target analysis',
                                synthetic=True,campaign_state='PARTIAL_SAMPLE',
                                numerics_schema='hadronization_projection_result_v3_g9_science')
        plot.apply_cold_page_style(pages,preview)
        self.assertEqual([p['title'] for p in pages],
                         ['Target analysis','','old heading'])
        self.assertEqual(pages[1]['information'],'')
        self.assertEqual(pages[2]['information'],'typed details')
        self.assertTrue(all(p['scientific_header']==
                            'TEST_ONLY / SYNTHETIC' for p in pages))
        full=SimpleNamespace(target_analysis_caption='PYTHIA 8.317',
                             synthetic=False,campaign_state='FULL_ACCEPTED_CAMPAIGN',
                             numerics_schema='hadronization_projection_result_v4')
        plot.apply_cold_page_style(pages,full)
        self.assertEqual([p['title'] for p in pages],
                         ['PYTHIA 8.317','','old heading'])
        self.assertTrue(all(p['scientific_header']=='' for p in pages))
        full.pair_selection_caption = 'P2-P8: no final-hadron #it{p}_{T} floor'
        plot.apply_cold_page_style(pages,full)
        self.assertEqual(pages[1]['information'],
                         full.pair_selection_caption)
        self.assertEqual(pages[2]['information'],'typed details')
        v4_partial=SimpleNamespace(target_analysis_caption='Target analysis',
            synthetic=True,campaign_state='PARTIAL_SAMPLE',
            numerics_schema='hadronization_projection_result_v4')
        plot.apply_cold_page_style(pages,v4_partial)
        self.assertTrue(all(p['scientific_header']==
            'TEST_ONLY / SYNTHETIC / PARTIAL_SAMPLE' for p in pages))

    def test_g9_signed_header_and_typed_no_draw_statuses(self):
        config,_=plot.checked_plot_config(ROOT / 'config/plot.json')
        science={
            'model_id':'G9_direct_primary_selected_no_pt_floor_eta4',
            'source_family':'kinematics','final':True,'selected':True,
            'status_low':81,'status_high':89,'origin_scope':'ALL_ORIGINS',
            'pt':{'domain':'PHYSICAL','units':'GeV','low':None,'high':None,
                  'low_operator':None,'high_operator':None},
            'eta':{'low':float(-4).hex(),'high':float(4).hex(),
                   'low_operator':'GE','high_operator':'LE'},
            'denominator':'weighted_all_origin_selected_final_same_signed_species_and_tune',
            'normalization':'per_bin_probability_no_bin_width_division',
            'units':'probability_per_bin',
            'ratio':'same_bin_probability_over_reference_tune_probability',
            'pt_flow':'negative_underflow_rejected_overflow_in_denominator_and_output',
            'eta_flow':'no_materialized_flow_inclusive_upper_endpoint',
            'phi_flow':'no_materialized_flow_inclusive_upper_endpoint',
            'axis_ids':['pt','eta','phi']}
        context=SimpleNamespace(g9_science=science,reference_tune='MONASH',
            numerics_schema='hadronization_projection_result_v4',
            axes=[{'id':'eta','variable':'g9_eta','units':'1',
                   'edges':[float(x).hex() for x in (-4,0,4)]}],
            tunes=['MONASH','JUNCTIONS'],
            g9_pages=[{'pdg':5212,'axis_id':'eta'}],
            materialization_by_semantic_id={})
        def row(semantic_id,ratio,value,value_status,uncertainty,reason):
            return {'semantic_id':semantic_id,'associate_pdg':'5212',
                    'axis':'eta','tune':'JUNCTIONS' if ratio else 'MONASH',
                    'reference_tune':'MONASH' if ratio else '',
                    'family':'kinematics','quantity':'normalized_spectrum'
                    if not ratio else 'spectrum_ratio_to_reference_tune',
                    'flow':'REGULAR','bin_low':'-4','bin_high':'0',
                    'bin_index':'0','class_id':'','units':'probability_per_bin',
                    'value':value,'value_status':value_status,
                    'finite_mc_error':'','uncertainty_status':uncertainty,
                    'reasons':reason}
        rows=[row('absolute',False,'','UNDEFINED',
                  'WITHHELD_UNCERTAINTY','G9_NONPOSITIVE_TOTAL'),
              row('ratio',True,'','UNDEFINED',
                  'WITHHELD_UNCERTAINTY','G9_NONPOSITIVE_TOTAL')]
        context.materialization_by_semantic_id={
            item['semantic_id']:{'status':'PRESENT','reason_codes':[]}
            for item in rows}
        pages=plot.g9_drawing_pages(context,rows,config,'TEST_ONLY','typed',
                                    {'5212':'#Sigma_{b}^{+}'})
        plot.apply_cold_page_style(pages,SimpleNamespace(
            numerics_schema='hadronization_projection_result_v4',
            synthetic=True,campaign_state='PARTIAL_SAMPLE'))
        self.assertEqual(pages[0]['title'],'G9 #it{#Sigma}_{b}^{0} #eta (1)')
        self.assertTrue(all(p['status']=='PRESENT_UNDEFINED'
                            for p in pages[0]['panels']))
        self.assertTrue(all('WITHHELD_UNCERTAINTY' in p['note'] and
                            'G9_NONPOSITIVE_TOTAL' in p['note']
                            for p in pages[0]['panels']))
        for item in rows:
            context.materialization_by_semantic_id[item['semantic_id']]={
                'status':'NOT_MATERIALIZED',
                'reason_codes':['ABSENT_SELECTED_SPECIES']}
        absent=plot.g9_drawing_pages(context,rows,config,'TEST_ONLY','typed',
                                     {'5212':'#Sigma_{b}^{+}'})[0]
        self.assertTrue(all(p['status']=='NOT_MATERIALIZED'
                            for p in absent['panels']))
        self.assertTrue(all('ABSENT_SELECTED_SPECIES' in p['note']
                            for p in absent['panels']))
        rows[0]['value']='0'
        rows[0]['value_status']='AVAILABLE'
        rows[0]['reasons']=''
        context.materialization_by_semantic_id['absolute']={
            'status':'PRESENT','reason_codes':[]}
        zero=plot.g9_drawing_pages(context,rows,config,'TEST_ONLY','typed',
                                   {'5212':'#Sigma_{b}^{+}'})[0]
        self.assertEqual(zero['panels'][0]['status'],'AVAILABLE')
        self.assertEqual(zero['panels'][0]['series'][0]['points'][0]['y'],0.)
        self.assertEqual(zero['panels'][0]['x_range'],[-4.,4.])

    def test_blank_paper_pad_uses_typed_materialization_not_drawability(self):
        row={'semantic_id':'point','value_status':'UNDEFINED',
             'uncertainty_status':'WITHHELD_UNCERTAINTY',
             'reasons':'ZERO_DENOMINATOR'}
        context=SimpleNamespace(materialization_by_semantic_id={
            'point':{'status':'PRESENT','reason_codes':[]}})
        self.assertEqual(plot.typed_panel_status(context,[row]),
            ('PRESENT_UNDEFINED',
             'UNDEFINED; WITHHELD_UNCERTAINTY; ZERO_DENOMINATOR'))
        self.assertEqual(plot.typed_panel_status(context,[
            dict(row,value_status='AVAILABLE')])[0],
            'PRESENT_NO_DRAWABLE_CENTER')
        compact=plot.typed_panel_status(context,[
            dict(row,reasons='DENOMINATOR_NUMERICALLY_UNRESOLVED:SOURCE_MONASH_INTERNAL'),
            dict(row,reasons='DENOMINATOR_NUMERICALLY_UNRESOLVED:SOURCE_JUNCTIONS_INTERNAL')])[1]
        self.assertEqual(compact,
            'UNDEFINED; WITHHELD_UNCERTAINTY; DENOMINATOR_NUMERICALLY_UNRESOLVED')
        self.assertEqual(plot.compact_paper_status_note(
            'PRESENT_UNDEFINED',compact),
            'SE withheld, denominator unresolved')
        self.assertEqual(plot.compact_paper_status_note(
            'PRESENT_UNDEFINED',compact+'; UNDEFINED_CENTER'),
            'SE withheld, denominator unresolved')
        context.materialization_by_semantic_id['point']={
            'status':'NOT_MATERIALIZED',
            'reason_codes':['ABSENT_SELECTED_SPECIES']}
        status,note=plot.typed_panel_status(context,[row])
        self.assertEqual(status,'NOT_MATERIALIZED')
        self.assertIn('ABSENT_SELECTED_SPECIES',note)
        self.assertEqual(plot.typed_panel_status(context,[]),
                         ('NOT_MATERIALIZED',''))

    def test_p1_caption_describes_typed_proxy_without_primary_overclaim(self):
        selection={'charged':True,'final':True,
                   'exclude_heavy_constituents':True,
                   'pt':{'low_operator':'GT'}}
        caption=plot.activity_proxy_caption(selection,0.15,4.0)
        self.assertIn('charged-light final-particle activity',caption)
        self.assertIn('heavy flavour excluded',caption)
        self.assertIn('#it{p}_{T} > 0.15 GeV/c',caption)
        self.assertIn('|#eta| #leq 4',caption)
        self.assertNotIn('primary',caption)
        with self.assertRaisesRegex(ValueError,'typed charged-final activity'):
            plot.activity_proxy_caption(dict(selection,final=False),0.15,4.0)

    def test_target_campaign_preview_uses_actual_energy_and_full_context_checked(self):
        payload={'schema':'hadronization_projection_result_v3_g9_science',
                 'request_echo':{'scope':{'ordered_tunes':
                     ['MONASH','JUNCTIONS','CLOSEPACKING']},
                     'sources':{'campaign_id':'TEST'}},
                 'provenance':{'data_limitations':
                     ['TEST_ONLY_SYNTHETIC_NO_PHYSICS'],
                     'generator_name':'TEST_ONLY','generator_version':'2',
                     'collision_system':'TEST_ONLY','energy_gev':float(0).hex()}}
        self.assertEqual(plot.target_analysis_caption(payload),
            'PYTHIA 8.317; pp, #sqrt{#it{s}} = 13.6 TeV')
        payload['provenance']['data_limitations']=[]
        payload['request_echo']['sources']['campaign_id']='HF_RUN3_V1'
        with self.assertRaisesRegex(ValueError,'contradicts target campaign'):
            plot.target_analysis_caption(payload)
        payload['request_echo']['sources']['campaign_id']='FUTURE_CAMPAIGN'
        self.assertEqual(plot.target_analysis_caption(payload),
            'TEST_ONLY 2; TEST_ONLY, #sqrt{#it{s}} = 0 TeV')

    def test_v4_partial_campaign_is_distinct_from_complete_package(self):
        v4 = {'schema':'hadronization_projection_result_v4',
              'package_state':'VALIDATED_COMPLETE',
              'campaign_state':'PARTIAL_SAMPLE'}
        self.assertTrue(plot.partial_numerics(v4))
        with self.assertRaisesRegex(ValueError, 'v4 numerical package state'):
            plot.partial_numerics(dict(v4, package_state='VALIDATED_PARTIAL'))
        v3 = dict(v4, schema='hadronization_projection_result_v3_g9_science')
        self.assertFalse(plot.partial_numerics(v3))
        self.assertTrue(plot.partial_numerics(dict(v3,
            package_state='VALIDATED_PARTIAL')))

    def test_v4_tune_permutation_keeps_target_caption(self):
        payload={'schema':'hadronization_projection_result_v4',
                 'request_echo':{'scope':{'ordered_tunes':
                     ['CLOSEPACKING','JUNCTIONS','MONASH']},
                     'sources':{'campaign_id':'HF_RUN3_V1'}},
                 'provenance':{'data_limitations':
                     ['TEST_ONLY_SYNTHETIC_NO_PHYSICS'],
                     'generator_name':'PYTHIA','generator_version':'8.317',
                     'collision_system':'pp','energy_gev':float(13600).hex()}}
        self.assertEqual(plot.target_analysis_caption(payload),
            'PYTHIA 8.317; pp, #sqrt{#it{s}} = 13.6 TeV')
        payload['provenance']['data_limitations'] = []
        self.assertEqual(plot.target_analysis_caption(payload),
            'PYTHIA 8.317; pp, #sqrt{#it{s}} = 13.6 TeV')
        payload['request_echo']['scope']['ordered_tunes'] = [
            'CLOSEPACKING','JUNCTIONS','JUNCTIONS']
        with self.assertRaisesRegex(ValueError, 'target campaign scope'):
            plot.target_analysis_caption(payload)

    def test_g9_signed_species_uses_archived_associate_key(self):
        curve = {"role_id": "spectra.signed_heavy",
                 "trigger_pdg": None, "associate_pdg": -5122}
        self.assertEqual(plot.g9_signed_species(curve), -5122)
        with self.assertRaisesRegex(ValueError, "G9 signed-species"):
            plot.g9_signed_species(dict(curve, trigger_pdg=5122))

    def test_g9_caption_uses_typed_science_record(self):
        science = {
            'model_id':'G9_direct_primary_selected_strict_pt0p15_eta4',
            'source_family':'kinematics','final':True,'selected':True,
            'status_low':81,'status_high':89,
            'pt':{'low':float(.15).hex(),'high':None,
                  'low_operator':'GT','units':'GeV'},
            'eta':{'low':float(-4.).hex(),'high':float(4.).hex(),
                   'low_operator':'GE','high_operator':'LE'},
            'denominator':'weighted_selected_final_same_signed_species_and_tune',
            'normalization':'per_bin_probability_no_bin_width_division',
            'units':'probability_per_bin',
            'ratio':'same_bin_probability_over_reference_tune_probability',
            'pt_flow':'underflow_and_overflow_in_denominator_and_output',
            'eta_flow':'no_materialized_flow_inclusive_upper_endpoint',
            'phi_flow':'no_materialized_flow_inclusive_upper_endpoint',
            'axis_ids':['pt','eta','phi'],
        }
        legacy_schema = 'hadronization_projection_result_v3_g9_science'
        current_schema = 'hadronization_projection_result_v4'
        caption, ratio, absolute = plot.g9_science_caption(
            science, 'MONASH', legacy_schema)
        self.assertIn('status 81-89', caption)
        self.assertIn('G9 selected final', caption)
        self.assertIn('#it{p}_{T} > 0.15 GeV', caption)
        self.assertIn('|#eta| #leq 4', caption)
        self.assertIn('per species/tune', caption)
        self.assertEqual(ratio, '#it{P}_{bin} / #it{P}_{bin,MONASH}')
        self.assertEqual(absolute, 'Probability / bin')
        with self.assertRaisesRegex(ValueError, 'G9 selection'):
            plot.g9_science_caption(dict(science,
                denominator='per_trigger_pair_profile'), 'MONASH', legacy_schema)
        with self.assertRaisesRegex(ValueError, 'G9 selection'):
            plot.g9_science_caption(science, 'MONASH', current_schema)
        current = dict(science,
            model_id='G9_direct_primary_selected_no_pt_floor_eta4',
            origin_scope='ALL_ORIGINS',
            pt={'domain':'PHYSICAL','units':'GeV','low':None,'high':None,
                'low_operator':None,'high_operator':None},
            denominator='weighted_all_origin_selected_final_same_signed_species_and_tune',
            pt_flow='negative_underflow_rejected_overflow_in_denominator_and_output')
        caption, ratio, absolute = plot.g9_science_caption(
            current, 'MONASH', current_schema)
        self.assertIn('all origins, no #it{p}_{T} floor', caption)
        self.assertNotIn('0.15', caption)
        self.assertIn('per species/tune', caption)
        self.assertEqual(ratio, '#it{P}_{bin} / #it{P}_{bin,MONASH}')
        self.assertEqual(absolute, 'Probability / bin')
        for mutation in (
                dict(current, origin_scope='SELECTED_HARD'),
                dict(current, pt=dict(current['pt'], low=float(.15).hex())),
                dict(current, pt=dict(current['pt'], domain='SELECTED'))):
            with self.assertRaisesRegex(ValueError, 'G9 cut'):
                plot.g9_science_caption(mutation, 'MONASH', current_schema)
        with self.assertRaisesRegex(ValueError, 'G9 selection'):
            plot.g9_science_caption(dict(current, status_low=80),
                                    'MONASH', current_schema)


if __name__ == "__main__":
    unittest.main()
