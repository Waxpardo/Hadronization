// Nominal tune-setting audit used by the retained producer.
#ifndef HADRONIZATION_GENERATED_TUNE_SETTING_REGISTRY_H
#define HADRONIZATION_GENERATED_TUNE_SETTING_REGISTRY_H

#include <array>
#include <string_view>

namespace Hadronization {
inline constexpr std::string_view kStudyDefinitionSchema =
    "hadronization_study_v1";
inline constexpr std::string_view kStudyDefinitionSha256 =
    "694bc8c32d7be18e57abd8629ed76de2d09ccfdf25d87c3c9df4a4472c34354d";
struct TuneSettingValue {
  std::string_view name;
  std::string_view value;
};
inline constexpr std::array<std::string_view, 46>
    kAuditedPythiaSettingKeys{{
  "BeamRemnants:remnantMode",
  "BeamRemnants:saturation",
  "Beams:eCM",
  "Beams:idA",
  "Beams:idB",
  "ClosePacking:PT0",
  "ClosePacking:baryonSup",
  "ClosePacking:doClosePacking",
  "ClosePacking:doEnhanceDiquark",
  "ClosePacking:enhancePT",
  "ClosePacking:enhanceStrange",
  "ClosePacking:parallelBaryonSup",
  "ColourReconnection:allowDoubleJunRem",
  "ColourReconnection:allowJunctions",
  "ColourReconnection:junctionCorrection",
  "ColourReconnection:m0",
  "ColourReconnection:mPseudo",
  "ColourReconnection:mode",
  "ColourReconnection:timeDilationMode",
  "ColourReconnection:timeDilationPar",
  "HardQCD:hardbbbar",
  "HardQCD:hardccbar",
  "Init:showChangedParticleData",
  "Init:showMultipartonInteractions",
  "Main:numberOfEvents",
  "MultipartonInteractions:pT0Ref",
  "Next:numberCount",
  "Next:numberShowEvent",
  "Next:numberShowInfo",
  "Next:numberShowProcess",
  "ParticleDecays:limitTau0",
  "ParticleDecays:tau0Max",
  "PhaseSpace:pTHatMin",
  "Random:seed",
  "Random:setSeed",
  "Ropewalk:RopeHadronization",
  "StringFlav:probQQ1toQQ0join",
  "StringFlav:probQQtoQ",
  "StringFlav:probStoUD",
  "StringFragmentation:doStrangeJunctions",
  "StringFragmentation:enhanceStrangeJunction",
  "StringPT:sigma",
  "StringZ:aLund",
  "StringZ:bLund",
  "StringZ:useOldAExtra",
  "Tune:pp"
}};
inline constexpr std::array<std::string_view, 28>
    kAllowedTuneDifferenceKeys{{
  "BeamRemnants:remnantMode",
  "BeamRemnants:saturation",
  "ClosePacking:PT0",
  "ClosePacking:baryonSup",
  "ClosePacking:doClosePacking",
  "ClosePacking:doEnhanceDiquark",
  "ClosePacking:enhancePT",
  "ClosePacking:enhanceStrange",
  "ClosePacking:parallelBaryonSup",
  "ColourReconnection:allowDoubleJunRem",
  "ColourReconnection:allowJunctions",
  "ColourReconnection:junctionCorrection",
  "ColourReconnection:m0",
  "ColourReconnection:mPseudo",
  "ColourReconnection:mode",
  "ColourReconnection:timeDilationMode",
  "ColourReconnection:timeDilationPar",
  "MultipartonInteractions:pT0Ref",
  "Ropewalk:RopeHadronization",
  "StringFlav:probQQ1toQQ0join",
  "StringFlav:probQQtoQ",
  "StringFlav:probStoUD",
  "StringFragmentation:doStrangeJunctions",
  "StringFragmentation:enhanceStrangeJunction",
  "StringPT:sigma",
  "StringZ:aLund",
  "StringZ:bLund",
  "StringZ:useOldAExtra"
}};
inline constexpr std::array<std::string_view, 4>
    kAllowedPerJobDifferenceKeys{{
  "Main:numberOfEvents",
  "PhaseSpace:pTHatMin",
  "Random:seed",
  "Random:setSeed"
}};
inline constexpr std::array<TuneSettingValue, 15>
    kCommonRequiredCardValues{{
  TuneSettingValue{"Beams:eCM", "13600"},
  TuneSettingValue{"Beams:idA", "2212"},
  TuneSettingValue{"Beams:idB", "2212"},
  TuneSettingValue{"HardQCD:hardbbbar", "on"},
  TuneSettingValue{"HardQCD:hardccbar", "on"},
  TuneSettingValue{"Init:showChangedParticleData", "off"},
  TuneSettingValue{"Init:showMultipartonInteractions", "off"},
  TuneSettingValue{"Next:numberCount", "0"},
  TuneSettingValue{"Next:numberShowEvent", "0"},
  TuneSettingValue{"Next:numberShowInfo", "0"},
  TuneSettingValue{"Next:numberShowProcess", "0"},
  TuneSettingValue{"ParticleDecays:limitTau0", "on"},
  TuneSettingValue{"ParticleDecays:tau0Max", "0.01"},
  TuneSettingValue{"PhaseSpace:pTHatMin", "2."},
  TuneSettingValue{"Tune:pp", "14"}
}};
}  // namespace Hadronization
#endif
