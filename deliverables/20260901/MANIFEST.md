# MANIFEST — the handoff package

One row per file. Every sha256 below was verified twice: the mirror copy against
its current acceptance record, and the delivered copy again after the copy
(`HANDOFF_EVIDENCE_3cccb75_20260901/verify/build_and_verify.txt`).

Package assembled at repository HEAD `3cccb750d36f356467caa5b810f45c80555153d5`.

## The result roots this package draws on

The files come from more than one root. Each row names its own.

| result root | rendered at HEAD | producing session | rows |
|---|---|---|---|
| `/data/alice/ipardoza/hf/hadronization_merged` | `6729b3f0b7b9` | RUN-N4b | G1, G2, G3, G4, G5, G6, G7, G8, G9 |
| `/data/alice/ipardoza/hf/hadronization_production/HF_RUN3_V1/raw (counts, via the sealed canonical manifest) ; /data/alice/ipardoza/hf/hadronization_merged (n_ev)` | `fe3262c729ec` | RUN-N | T1 |

The figure bytes were staged from the deployment plot slot at the same HEAD and
mirrored to the bench as `DELIVERABLES_REVIEW_20260901B/`, which carries a
two-sided sha proof: `SHA256SUMS.deployment` written at Nikhef before and after
the copy, `SHA256SUMS.bench` written independently on the bench. This session
re-verified that mirror: 166 of 166 files agree, and the two sum files are
byte-identical (VERIFIED, `entry/mirror_verify.txt`).

## Figures

`Overleaf path` is relative to the Overleaf project root and is byte-exact.
Drop `figures/` in whole.

| id | Overleaf path | produced as | sha256 | bytes | session | acceptance record |
|---|---|---|---|---|---|---|
| G1 | `figures/Kinematic Plots/MultiplicitySpectrum_Shared_shape.png` | `KinematicSpectra/Multiplicity/MultiplicitySpectrum_Shared_shape.png` | `221b96b033ced9461cc5ee689f57708535097992baed00c62ab553f2678ec2d0` | 71,209 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G1.json` |
| G2 | `figures/AngularCorrelations/CharmCorrelations_MONASH_PDF.pdf` **(renamed)** | `THnSparse/Correlations/CHARMCorrelations_MONASH_PDF.pdf` | `d3ce9d7821a98f71985dc4a36e94505205c2577688de0cc4db3088b955c65126` | 37,698 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G2.json` |
| G3 | `figures/AngularCorrelations/BeautyCorrelations_MONASH_PDF.pdf` **(renamed)** | `THnSparse/Correlations/BEAUTYCorrelations_MONASH_PDF.pdf` | `525ada3955f3c1a149e592e81abec4f2aa4efe627ef6b8aa24d74cd5346e7d38` | 47,935 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G3.json` |
| G4 | `figures/YieldsBalancing/global_balancing_plots_integrated_charm_PDF.pdf` | `VariantIntegrated/global_balancing_plots_integrated_charm_PDF.pdf` | `821badb7a1c3247ca68dac0bff1997758f8907cfac615ab44df8caa5a1ff6404` | 19,585 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G4.json` |
| G5 | `figures/YieldsBalancing/global_balancing_plots_multiplicity_charm_PDF.pdf` | `VariantExtremes/global_balancing_plots_multiplicity_charm_PDF.pdf` | `941901ca08ceceb19238fd0ad381736baedd92c0d323502e9cc012820f491dc4` | 21,731 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G5.json` |
| G6 | `figures/YieldsBalancing/global_balancing_plots_integrated_beauty_PDF.pdf` | `VariantIntegrated/global_balancing_plots_integrated_beauty_PDF.pdf` | `9231bf9fe36dbad5e7572ff568b44d80a2380b6b3e0deab1946db84d9b752828` | 24,277 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G6.json` |
| G7 | `figures/YieldsBalancing/global_balancing_plots_multiplicity_beauty_PDF.pdf` | `VariantExtremes/global_balancing_plots_multiplicity_beauty_PDF.pdf` | `baa1aa32954b58c7e9e73a63aa6e5c6f50568b2c18a273acb9f6003e50a70056` | 23,181 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G7.json` |
| G8 | `figures/BaryonMesonRelativeYieldsBalancing/global_balancing_baryon_over_meson_ratio_multiplicity_PDF.pdf` | `VariantBaryonMeson/global_balancing_baryon_over_meson_ratio_multiplicity_PDF.pdf` | `a17ff527233112f64fdb57ee9649489a11339ca7f6bb171596e39a2d33c87bd5` | 23,156 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G8.json` |

### G9 — thirty inclusive kinematic stems

Ten species by three observables. The current draft includes none of them; see
`EDITORIAL_NOTES.md`. The `.pdf` extension is this session's choice, because the
DELIVERABLES manifest names G9 by stem with no extension.

| id | Overleaf path | sha256 | bytes | session | acceptance record |
|---|---|---|---|---|---|
| G9 | `figures/Kinematic Plots/Inclusive_pT_Bplus_shape.pdf` | `16db858475792de9252243967df72503550e91119abb1050765479fb90040854` | 31,142 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G9.json` |
| G9 | `figures/Kinematic Plots/Inclusive_pT_Bminus_shape.pdf` | `0a776c0b3a379a8063e532d3eb37166c0399c98912557f619bbf06771a8a62b3` | 31,146 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G9.json` |
| G9 | `figures/Kinematic Plots/Inclusive_pT_Lambdab_shape.pdf` | `a659250ae951853a2681a27da016140ad83e69959f889f674da5293ffd256449` | 30,753 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G9.json` |
| G9 | `figures/Kinematic Plots/Inclusive_pT_Lambdabbar_shape.pdf` | `133fbe43a77116bed79703a7113dfc97f83b827a77b983aa5bc564239588cedd` | 30,839 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G9.json` |
| G9 | `figures/Kinematic Plots/Inclusive_pT_Sigmabzero_shape.pdf` | `dfff2d850b0672457da5afeee4d989d193eedd55ffe3fbfacb219244924b4b4e` | 27,955 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G9.json` |
| G9 | `figures/Kinematic Plots/Inclusive_pT_Sigmabzerobar_shape.pdf` | `49ce1b5fbb64dc00c87568b5f53e6131c42d53eed4fd6ea8e31316eb0e822b0a` | 28,124 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G9.json` |
| G9 | `figures/Kinematic Plots/Inclusive_pT_Dplus_shape.pdf` | `620e781e1f20ad15556a4af8e88e030f38dd09ef2b2bc4d36bd235ec1924d1cd` | 31,333 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G9.json` |
| G9 | `figures/Kinematic Plots/Inclusive_pT_Dminus_shape.pdf` | `c443109934a790f9675f7ac9841a9bc920d1f4a83f1dd470b2b069cc4dd2d6ed` | 31,395 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G9.json` |
| G9 | `figures/Kinematic Plots/Inclusive_pT_Lambdacplus_shape.pdf` | `fed54b8d4d2a5d90934e3be2141b007e4d62d3fe2ad9e9c3d91060523da378e3` | 29,848 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G9.json` |
| G9 | `figures/Kinematic Plots/Inclusive_pT_Lambdacplusbar_shape.pdf` | `ba44d727c89c732d1c6cd9b43ccfc1b45780c236f28081badb68861002263c34` | 29,755 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G9.json` |
| G9 | `figures/Kinematic Plots/Inclusive_eta_Bplus_shape.pdf` | `f84fac233428686c80b7287e1c3b1f897b8497f224853bcbe7a1c631333b512a` | 30,298 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G9.json` |
| G9 | `figures/Kinematic Plots/Inclusive_eta_Bminus_shape.pdf` | `493a4b118b9e2a6a504fb3edafe9769379eeb28f530e9caecae2ef90b8c06c7c` | 30,201 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G9.json` |
| G9 | `figures/Kinematic Plots/Inclusive_eta_Lambdab_shape.pdf` | `7450ea82f17b507aa9cb95c4d890d42a0c3cda1b9484f12fb9fd4c2be1b87729` | 30,324 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G9.json` |
| G9 | `figures/Kinematic Plots/Inclusive_eta_Lambdabbar_shape.pdf` | `8768e54e0a5aa249112f1b6bec605b02a9c05dfdd863a17c536844ad92999d51` | 30,334 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G9.json` |
| G9 | `figures/Kinematic Plots/Inclusive_eta_Sigmabzero_shape.pdf` | `3d5a3061cd0be5a6e25e701ed5062f6ce5e8fa354ccba98a1e3430c3a6f07634` | 30,364 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G9.json` |
| G9 | `figures/Kinematic Plots/Inclusive_eta_Sigmabzerobar_shape.pdf` | `3d98a8491344d38ec54f9e4facabe318aa612c4b86467671c2e95e648d80cdfe` | 30,256 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G9.json` |
| G9 | `figures/Kinematic Plots/Inclusive_eta_Dplus_shape.pdf` | `53038184fb9c682c8d4c272568ecefaad39045fb1a000a85f665b1d5a70d9497` | 29,915 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G9.json` |
| G9 | `figures/Kinematic Plots/Inclusive_eta_Dminus_shape.pdf` | `5f20b66c9279f7dd6ed7595d65036338ed71acf38f078c26954b5d99e0fb3b47` | 29,963 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G9.json` |
| G9 | `figures/Kinematic Plots/Inclusive_eta_Lambdacplus_shape.pdf` | `e9ec6a58a2a4ced317d80eba1da43785ab170b600668d7f3544b8063f19b4dd6` | 30,256 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G9.json` |
| G9 | `figures/Kinematic Plots/Inclusive_eta_Lambdacplusbar_shape.pdf` | `412992437f972c93ed6bd24aa15564671cb49d0199e4e0b00c1cbccea80d3621` | 30,283 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G9.json` |
| G9 | `figures/Kinematic Plots/Inclusive_phi_Bplus_shape.pdf` | `11ec6729efd3924252a0d203e7cb52cf336fa9ff44473ea09997351dcbcd3a29` | 29,642 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G9.json` |
| G9 | `figures/Kinematic Plots/Inclusive_phi_Bminus_shape.pdf` | `8325cd029e76421cb8ee443136cb4eb1cbcc74d4314c59131585a75b91a47a07` | 29,631 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G9.json` |
| G9 | `figures/Kinematic Plots/Inclusive_phi_Lambdab_shape.pdf` | `55c049d51dd8e5cbfe785eb5c4634025dc33e9969433b003d49ac16dff7e7466` | 29,636 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G9.json` |
| G9 | `figures/Kinematic Plots/Inclusive_phi_Lambdabbar_shape.pdf` | `a3726b799dbd2f298ed0593a96f4cf1e15b52433ccc596f1a0e2bd26a1823889` | 29,563 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G9.json` |
| G9 | `figures/Kinematic Plots/Inclusive_phi_Sigmabzero_shape.pdf` | `7ca31977fe4cee273396562408f9df6547018a16974238375e6566e58c5fa4f1` | 29,450 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G9.json` |
| G9 | `figures/Kinematic Plots/Inclusive_phi_Sigmabzerobar_shape.pdf` | `d498626c79e0c383b0340af434a1f67baf83d705bad21d82cb14a9907d394a24` | 29,624 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G9.json` |
| G9 | `figures/Kinematic Plots/Inclusive_phi_Dplus_shape.pdf` | `eec5008c0b034e9ceefe048cb792b54406e70b2e614e8f9a6bfc3b7b7c3a8fcb` | 29,306 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G9.json` |
| G9 | `figures/Kinematic Plots/Inclusive_phi_Dminus_shape.pdf` | `388e8458c6a5e94ad85829d5d2fb5d4b7ffec89d3d2d9f4d4476d43b52e9a3ca` | 29,280 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G9.json` |
| G9 | `figures/Kinematic Plots/Inclusive_phi_Lambdacplus_shape.pdf` | `f3c701bb871b00b75471abf7a878738938034d5e31c946e9d2975ad2f4c6e818` | 29,739 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G9.json` |
| G9 | `figures/Kinematic Plots/Inclusive_phi_Lambdacplusbar_shape.pdf` | `094164e85dda24f70b5091c96854116af4bb8a153ad455ecb39096338d5201a8` | 29,779 | RUN-N4b | `DELIVERABLES_REVIEW_20260901B/records/RUNN4B_G9.json` |

## T1 — the generated-sample table

| file | what it is | sha256 | bytes | session | acceptance record |
|---|---|---|---|---|---|
| `tables/t1_MONASH.json` | MONASH counts and the definition block | `67ef257475689c958c1261327ae219724dc847231d032a76cb7f0859bc66d73c` | 1,512 | RUN-N | `DELIVERABLES_REVIEW_20260901B/records/RUNN_T1.json` |
| `tables/t1_JUNCTIONS.json` | JUNCTIONS counts and the definition block | `2934065b751426791e09ba5742d40502999878ada13f2abe58a1beb80a83ea2e` | 1,518 | RUN-N | `DELIVERABLES_REVIEW_20260901B/records/RUNN_T1.json` |
| `tables/t1_CLOSEPACKING.json` | CLOSEPACKING counts and the definition block | `20aeedb56e404b77ffa73d51c9a9706dc8cd3d2a8a552a0cf1c0be3ce36caa72` | 1,524 | RUN-N | `DELIVERABLES_REVIEW_20260901B/records/RUNN_T1.json` |
| `tables/t1_MONASH.json.tex` | MONASH single-column body, as certified | `a08852d7eef15ee0e80115151e39e4e3c5d3c03a99f434d7bca682a272e0e637` | 371 | RUN-N | `DELIVERABLES_REVIEW_20260901B/records/RUNN_T1.json` |
| `tables/t1_JUNCTIONS.json.tex` | JUNCTIONS single-column body, as certified | `528c388f2d07a360226dbdfc57b43c9cb04053db2ff284adc50180f157637c59` | 371 | RUN-N | `DELIVERABLES_REVIEW_20260901B/records/RUNN_T1.json` |
| `tables/t1_CLOSEPACKING.json.tex` | CLOSEPACKING single-column body, as certified | `c36c63070fff9746d4bfee7b778f5701290c8e4ce4b52528fcb1d0957a79f806` | 371 | RUN-N | `DELIVERABLES_REVIEW_20260901B/records/RUNN_T1.json` |

### The assembled table body

`tables/T1_generated_sample.tex` is the three certified single-column bodies
above, regrouped into three columns, with ruling R37's definition record
carried beside them as LaTeX comments. **It is the only file in this package
that this session wrote rather than copied**, and it contains no number that is
not in the JSONs: 108 transcription checks confirm every printed value against
its JSON field and against the certified per-tune body
(`HANDOFF_EVIDENCE_3cccb75_20260901/t1/recheck_t1.txt`).

| file | what it is | sha256 | bytes | written by |
|---|---|---|---|---|
| `tables/T1_generated_sample.tex` | the three tunes in three columns, plus the R37 definition record | `c6ed7961542f725135956490857d96f1c0e0824adc1db97ff4eb33e0c18c657c` | 4,109 | HANDOFF |

## Totals

| | |
|---|---|
| files copied and verified | 44 |
| files written by this session | 1 |
| files in `figures/` and `tables/` | 45 |
| bytes | 1,174,573 |
| result roots | 2 |
| acceptance records cited | 10 |

