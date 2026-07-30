#!/bin/bash
# LEGACY randomized directory-discovery subsampling. The canonical workflow
# uses frozen manifest blocks and never randomizes the accepted job set.
set -euo pipefail

# Build Paul-style subsample complete_root directories from per-job THnSparse
# status-analysis outputs.
#
# Usage:
#   ./make_subsamples.sh
#   ./make_subsamples.sh TUNE NSUBSAMPLES NJOBS_PER_SUBSAMPLE [SEED] [JOB_TAG] [SUBSAMPLE_TAG]
#   ./make_subsamples.sh ALL 10 10 123 Job700 700
#
# TUNE can be MONASH, JUNCTIONS, CLOSEPACKING, or ALL.
#
# Numeric shorthand is also accepted:
#   ./make_subsamples.sh NSUBSAMPLES NJOBS_PER_SUBSAMPLE [SEED]
# which defaults to TUNE=ALL.

usage() {
    cat <<'USAGE'
Usage:
  ./make_subsamples.sh
  ./make_subsamples.sh TUNE NSUBSAMPLES NJOBS_PER_SUBSAMPLE [SEED] [JOB_TAG] [SUBSAMPLE_TAG]
  ./make_subsamples.sh ALL 10 10 123 Job700 700

Numeric shorthand:
  ./make_subsamples.sh NSUBSAMPLES NJOBS_PER_SUBSAMPLE [SEED]

TUNE:
  MONASH
  JUNCTIONS
  CLOSEPACKING
  ALL

Defaults:
  TUNE          = ALL
  NSUBSAMPLES   = 10
  NJOBS/SAMPLE  = 10
  SEED          = 123
  JOB_TAG       = Job700
  SUBSAMPLE_TAG = 700

Environment overrides:
  ANALYSIS_OUTPUT_BASE Per-job THnSparse analysis output base directory.
  ANALYZED_DATA_BASE   Destination base for AnalyzedData.
  HADRONIZATION_BASE   Hadronization checkout, used for setupEnv.sh and AnalyzedData default.
  SUBSAMPLE_MODE       partition (default) or bootstrap.
  MERGE_BACKEND        object (default), hadd, hadd-chunked, or hybrid.
  HADD_JOBS            Parallel hadd workers when MERGE_BACKEND=hadd (default: 4).
  HADD_FINAL_JOBS      Parallel hadd workers for the final merge of chunk files
                       when using hadd-chunked or hybrid fallback (default: 4).
  HADD_CHUNK_SIZE      Number of input files per intermediate chunk when using
                       hadd-chunked or hybrid fallback (default: 10).
  MERGE_OBJECT_FALLBACK_REGEX
                       ROOT filename regex merged with the chunked backend when
                       MERGE_BACKEND=hybrid (default: ^(Dplus|Dzero|Lambdacplus).*\.root$).

The default partition mode shuffles the available jobs once per tune and then
splits them into non-overlapping subsamples. Use SUBSAMPLE_MODE=bootstrap only
when overlapping random resamples are intentional.
USAGE
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_base="${HADRONIZATION_BASE:-${script_dir}}"
project_base="${project_base%/}"
export HADRONIZATION_BASE="${project_base}"

default_tune="ALL"
default_nsubsamples="10"
default_njobs_per_subsample="10"
default_seed="123"
default_job_tag="Job700"
default_subsample_tag="700"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    usage
    exit 0
fi

if [[ "$#" -eq 0 ]]; then
    requested_tune="${default_tune}"
    nsubsamples="${default_nsubsamples}"
    njobs_per_subsample="${default_njobs_per_subsample}"
    seed="${default_seed}"
    job_tag="${default_job_tag}"
    subsample_tag="${default_subsample_tag}"
elif [[ "${1}" =~ ^[0-9]+$ ]]; then
    requested_tune="${default_tune}"
    nsubsamples="${1}"
    njobs_per_subsample="${2:-}"
    seed="${3:-${default_seed}}"
    job_tag="${default_job_tag}"
    subsample_tag="${default_subsample_tag}"
else
    requested_tune="$(printf '%s' "${1}" | tr '[:lower:]' '[:upper:]')"
    nsubsamples="${2:-${default_nsubsamples}}"
    njobs_per_subsample="${3:-${default_njobs_per_subsample}}"
    seed="${4:-${default_seed}}"
    job_tag="${5:-${default_job_tag}}"
    subsample_tag="${6:-${default_subsample_tag}}"
fi

for value_name in nsubsamples njobs_per_subsample seed; do
    value="${!value_name}"
    if ! [[ "${value}" =~ ^[0-9]+$ ]]; then
        echo "ERROR: ${value_name} must be an integer, got '${value}'" >&2
        exit 1
    fi
done

analysis_output_base="${ANALYSIS_OUTPUT_BASE:-/data/alice/pveen_new/PanosPaper/RootFiles/AnalysisResults/HF}"
analyzed_data_base="${ANALYZED_DATA_BASE:-${project_base}/AnalyzedData}"
output_base_dir="${analyzed_data_base}/SUBSAMPLES_${subsample_tag}"
subsample_mode="${SUBSAMPLE_MODE:-partition}"
merge_backend="${MERGE_BACKEND:-object}"
hadd_jobs="${HADD_JOBS:-4}"
hadd_final_jobs="${HADD_FINAL_JOBS:-4}"
hadd_chunk_size="${HADD_CHUNK_SIZE:-10}"
merge_object_fallback_regex="${MERGE_OBJECT_FALLBACK_REGEX:-^(Dplus|Dzero|Lambdacplus).*\\.root$}"

case "${subsample_mode}" in
    partition|bootstrap)
        ;;
    *)
        echo "ERROR: SUBSAMPLE_MODE must be 'partition' or 'bootstrap', got '${subsample_mode}'" >&2
        exit 1
        ;;
esac

case "${merge_backend}" in
    object|hadd|hadd-chunked|hybrid)
        ;;
    *)
        echo "ERROR: MERGE_BACKEND must be 'object', 'hadd', 'hadd-chunked', or 'hybrid', got '${merge_backend}'" >&2
        exit 1
        ;;
esac

if ! [[ "${hadd_jobs}" =~ ^[0-9]+$ ]] || [[ "${hadd_jobs}" -lt 1 ]]; then
    echo "ERROR: HADD_JOBS must be a positive integer, got '${hadd_jobs}'" >&2
    exit 1
fi

if ! [[ "${hadd_final_jobs}" =~ ^[0-9]+$ ]] || [[ "${hadd_final_jobs}" -lt 1 ]]; then
    echo "ERROR: HADD_FINAL_JOBS must be a positive integer, got '${hadd_final_jobs}'" >&2
    exit 1
fi

if ! [[ "${hadd_chunk_size}" =~ ^[0-9]+$ ]] || [[ "${hadd_chunk_size}" -lt 1 ]]; then
    echo "ERROR: HADD_CHUNK_SIZE must be a positive integer, got '${hadd_chunk_size}'" >&2
    exit 1
fi

if [[ -f "${project_base}/setupEnv.sh" ]]; then
    # shellcheck disable=SC1091
    source "${project_base}/setupEnv.sh"
fi

resolve_tunes() {
    case "$1" in
        MONASH|JUNCTIONS|CLOSEPACKING)
            printf '%s\n' "$1"
            ;;
        ALL)
            printf '%s\n' MONASH JUNCTIONS CLOSEPACKING
            ;;
        *)
            echo "ERROR: unknown tune '$1'. Expected MONASH, JUNCTIONS, CLOSEPACKING, or ALL." >&2
            exit 1
            ;;
    esac
}

shuffle_jobs() {
    local tune_index="$1"
    local subsample_index="$2"
    local shuffle_seed=$((seed + tune_index * 100000 + subsample_index))

    awk -v seed="${shuffle_seed}" '
        BEGIN { srand(seed) }
        { print rand() "\t" $0 }
    ' | sort -k1,1n | cut -f2-
}

merge_files() {
    local output_file="$1"
    shift
    local rootfile
    rootfile="$(basename "${output_file}")"
    local effective_backend="${merge_backend}"

    if [[ "${merge_backend}" == "hybrid" ]]; then
        effective_backend="hadd"
        if [[ "${rootfile}" =~ ${merge_object_fallback_regex} ]]; then
            effective_backend="hadd-chunked"
        fi
        echo "Merge backend for ${rootfile}: ${effective_backend}"
    fi

    case "${effective_backend}" in
        object)
            local merge_macro="${project_base}/AnalysisScripts/MergeAnalysisObjects.C"
            if [[ ! -f "${merge_macro}" ]]; then
                echo "ERROR: object merge backend requested, but macro not found: ${merge_macro}" >&2
                return 1
            fi

            local input_list
            input_list="$(mktemp "/tmp/make_subsamples_XXXXXX.txt")"
            printf '%s\n' "$@" > "${input_list}"
            local tmp_output
            tmp_output="$(mktemp "/tmp/hadronization_object_XXXXXX.root")"
            rm -f "${tmp_output}"
            mkdir -p "$(dirname "${output_file}")"

            root -l -b <<ROOTCMDS
.L ${merge_macro}+
int __merge_result = MergeAnalysisObjects("${input_list}", "${tmp_output}", true);
if (__merge_result != 0) { gSystem->Exit(__merge_result); }
.q
ROOTCMDS
            local merge_status=$?
            rm -f "${input_list}"
            if [[ ${merge_status} -eq 0 ]]; then
                mv -f "${tmp_output}" "${output_file}"
            else
                rm -f "${tmp_output}"
                return "${merge_status}"
            fi
            ;;
        hadd)
            local tmp_output
            tmp_output="$(mktemp "/tmp/hadronization_hadd_XXXXXX.root")"
            rm -f "${tmp_output}"
            mkdir -p "$(dirname "${output_file}")"

            local hadd_args=(-f -v 0)
            if [[ "${hadd_jobs}" -gt 1 ]]; then
                hadd_args+=(-j "${hadd_jobs}")
            fi

            if hadd "${hadd_args[@]}" "${tmp_output}" "$@"; then
                mv -f "${tmp_output}" "${output_file}"
            else
                rm -f "${tmp_output}"
                return 1
            fi
            ;;
        hadd-chunked)
            local tmp_output
            tmp_output="$(mktemp "/tmp/hadronization_hadd_XXXXXX.root")"
            rm -f "${tmp_output}"
            mkdir -p "$(dirname "${output_file}")"

            local hadd_args=(-f -v 0)
            if [[ "${hadd_jobs}" -gt 1 ]]; then
                hadd_args+=(-j "${hadd_jobs}")
            fi

            local final_hadd_args=(-f -v 0)
            if [[ "${hadd_final_jobs}" -gt 1 ]]; then
                final_hadd_args+=(-j "${hadd_final_jobs}")
            fi

            local tmp_dir
            tmp_dir="$(mktemp -d "/tmp/hadronization_hadd_chunks_XXXXXX")"
            local -a partials=()
            local -a chunk=()
            local input
            local chunk_index=0

            for input in "$@"; do
                chunk+=("${input}")
                if [[ "${#chunk[@]}" -ge "${hadd_chunk_size}" ]]; then
                    local partial="${tmp_dir}/partial_${chunk_index}.root"
                    if ! hadd "${hadd_args[@]}" "${partial}" "${chunk[@]}"; then
                        rm -rf "${tmp_dir}" "${tmp_output}"
                        return 1
                    fi
                    partials+=("${partial}")
                    chunk=()
                    chunk_index=$((chunk_index + 1))
                fi
            done

            if [[ "${#chunk[@]}" -gt 0 ]]; then
                local partial="${tmp_dir}/partial_${chunk_index}.root"
                if ! hadd "${hadd_args[@]}" "${partial}" "${chunk[@]}"; then
                    rm -rf "${tmp_dir}" "${tmp_output}"
                    return 1
                fi
                partials+=("${partial}")
            fi

            if [[ "${#partials[@]}" -eq 1 ]]; then
                mv -f "${partials[0]}" "${tmp_output}"
            elif ! hadd "${final_hadd_args[@]}" "${tmp_output}" "${partials[@]}"; then
                rm -rf "${tmp_dir}" "${tmp_output}"
                return 1
            fi

            mv -f "${tmp_output}" "${output_file}"
            rm -rf "${tmp_dir}"
            ;;
    esac
}

make_tune_subsamples() {
    local tune="$1"
    local tune_index="$2"
    local input_dir="${analysis_output_base}/${tune}/${job_tag}"
    local output_dir="${output_base_dir}/combined_root_subSamples_${tune}"

    echo "========================================"
    echo "Creating subsamples for ${tune}"
    echo "Input:  ${input_dir}"
    echo "Output: ${output_dir}"
    echo "Mode:   ${subsample_mode}"
    echo "========================================"

    if [[ ! -d "${input_dir}" ]]; then
        echo "ERROR: input directory not found for ${tune}: ${input_dir}" >&2
        return 1
    fi

    mkdir -p "${output_dir}"

    all_jobs=()
    while IFS= read -r job; do
        all_jobs+=("${job}")
    done < <(
        find "${input_dir}" \
            -mindepth 1 -maxdepth 1 \
            -type d \
            -name "hf_*_job*" | sort
    )

    local njobs_total=${#all_jobs[@]}

    if [[ "${njobs_total}" -eq 0 ]]; then
        echo "ERROR: no jobs found in ${input_dir}" >&2
        return 1
    fi

    echo "Found ${njobs_total} total jobs"

    local first_job=""
    local job
    for job in "${all_jobs[@]}"; do
        if compgen -G "${job}/*.root" > /dev/null; then
            first_job="${job}"
            break
        fi
    done

    if [[ -z "${first_job}" ]]; then
        echo "ERROR: no ROOT files found in any job under ${input_dir}" >&2
        return 1
    fi

    rootfiles=()
    while IFS= read -r rootfile; do
        rootfiles+=("${rootfile}")
    done < <(
        find "${first_job}" \
            -type f -name "*.root" \
            -exec basename {} \; | sort
    )

    echo "Found ${#rootfiles[@]} ROOT file types"

    local total_requested=$((nsubsamples * njobs_per_subsample))
    local shuffled_all_jobs=()

    if [[ "${subsample_mode}" == "partition" ]]; then
        if [[ "${total_requested}" -gt "${njobs_total}" ]]; then
            echo "ERROR: partition mode requested ${total_requested} job slots (${nsubsamples} subsamples x ${njobs_per_subsample} jobs), but only ${njobs_total} jobs are available for ${tune}." >&2
            echo "       Reduce NSUBSAMPLES or NJOBS_PER_SUBSAMPLE, or set SUBSAMPLE_MODE=bootstrap if overlapping resamples are intentional." >&2
            return 1
        fi

        while IFS= read -r shuffled_job; do
            shuffled_all_jobs+=("${shuffled_job}")
        done < <(
            printf "%s\n" "${all_jobs[@]}" | shuffle_jobs "${tune_index}" 0
        )
    fi

    local s
    for (( s=1; s<=nsubsamples; s++ )); do
        echo "Creating ${tune} subsample ${s}"

        local sub_dir="${output_dir}/combined_root_${s}"
        mkdir -p "${sub_dir}"

        local joblist_file="${sub_dir}/jobs_used.txt"
        : > "${joblist_file}"

        selected_jobs=()
        if [[ "${subsample_mode}" == "partition" ]]; then
            local offset=$(((s - 1) * njobs_per_subsample))
            selected_jobs=("${shuffled_all_jobs[@]:offset:njobs_per_subsample}")
        else
            shuffled_jobs=()
            while IFS= read -r shuffled_job; do
                shuffled_jobs+=("${shuffled_job}")
            done < <(
                printf "%s\n" "${all_jobs[@]}" | shuffle_jobs "${tune_index}" "${s}"
            )
            selected_jobs=("${shuffled_jobs[@]:0:njobs_per_subsample}")
        fi

        if [[ ${#selected_jobs[@]} -lt "${njobs_per_subsample}" ]]; then
            echo "WARNING: requested ${njobs_per_subsample} jobs but only selected ${#selected_jobs[@]}" >&2
        fi

        for job in "${selected_jobs[@]}"; do
            basename "${job}" >> "${joblist_file}"
        done

        local rootfile
        for rootfile in "${rootfiles[@]}"; do
            files=()

            for job in "${selected_jobs[@]}"; do
                candidate="${job}/${rootfile}"
                if [[ -f "${candidate}" ]]; then
                    files+=("${candidate}")
                fi
            done

            if [[ ${#files[@]} -eq 0 ]]; then
                echo "Skipping ${rootfile} for ${tune} subsample ${s}: no files found" >&2
                continue
            fi

            sorted_files=()
            while IFS= read -r sorted_file; do
                sorted_files+=("${sorted_file}")
            done < <(printf '%s\n' "${files[@]}" | sort)
            files=("${sorted_files[@]}")

            echo "Merging ${rootfile} with ${#files[@]} files"
            merge_files "${sub_dir}/${rootfile}" "${files[@]}"
        done

        echo "Finished ${tune} subsample ${s}"
    done
}

tunes=($(resolve_tunes "${requested_tune}"))

tune_index=0
for tune in "${tunes[@]}"; do
    make_tune_subsamples "${tune}" "${tune_index}"
    tune_index=$((tune_index + 1))
done

echo "========================================"
echo "ALL REQUESTED SUBSAMPLES COMPLETE"
echo "Output base: ${output_base_dir}"
echo "Tunes: ${tunes[*]}"
echo "========================================"
