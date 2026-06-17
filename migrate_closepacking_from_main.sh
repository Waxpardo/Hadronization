#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  ./migrate_closepacking_from_main.sh [--execute] [--allow-incomplete] [--copy-workdirs] [SRC_BASE] [DST_BASE]

Default source:
  /data/alice/ipardoza/Hadronization-main

Default destination:
  /data/alice/ipardoza/Hadronization

By default this is a dry run. Pass --execute to copy files.
The script refuses to migrate unless the source Close Packing production has
100 logical job ids unless --allow-incomplete is passed.
USAGE
}

execute=0
allow_incomplete=0
copy_workdirs=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --execute)
      execute=1
      shift
      ;;
    --allow-incomplete)
      allow_incomplete=1
      shift
      ;;
    --copy-workdirs)
      copy_workdirs=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --*)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
    *)
      break
      ;;
  esac
done

src_base="${1:-/data/alice/ipardoza/Hadronization-main}"
dst_base="${2:-/data/alice/ipardoza/Hadronization}"
expected_jobs="${CLOSEPACKING_EXPECTED_JOBS:-100}"
recovery_cluster="${CLOSEPACKING_RECOVERY_CLUSTER:-4842786}"

src_root="${src_base}/RootFiles/HF/CLOSEPACKING"
dst_root="${dst_base}/RootFiles/HF/CLOSEPACKING"
src_logs="${src_base}/logs/HF/CLOSEPACKING"
dst_logs="${dst_base}/logs/HF/CLOSEPACKING"
src_jobs="${src_base}/Jobs/HF/CLOSEPACKING"
dst_jobs="${dst_base}/Jobs/HF/CLOSEPACKING"

require_dir() {
  local dir="$1"
  if [[ ! -d "$dir" ]]; then
    echo "Missing directory: $dir" >&2
    exit 1
  fi
}

logical_job_ids() {
  local dir="$1"
  find "$dir" -maxdepth 1 -type f -name 'hf_CLOSEPACKING_cluster*_job*.root' -printf '%f\n' \
    | sed -E 's/^.*_job([0-9]+)\.root$/\1/' \
    | sort -n
}

count_files() {
  local dir="$1"
  find "$dir" -maxdepth 1 -type f -name 'hf_CLOSEPACKING_cluster*_job*.root' -printf '.' | wc -c
}

count_unique_jobs() {
  local dir="$1"
  logical_job_ids "$dir" | uniq | wc -l
}

duplicate_jobs() {
  local dir="$1"
  logical_job_ids "$dir" | uniq -d
}

missing_jobs() {
  local dir="$1"
  local present_ids
  present_ids="$(logical_job_ids "$dir" | uniq)"

  local job_id
  for ((job_id = 0; job_id < expected_jobs; job_id++)); do
    if ! grep -qx "$job_id" <<<"$present_ids"; then
      echo "$job_id"
    fi
  done
}

copy_dir_contents() {
  local src="$1"
  local dst="$2"
  shift 2

  mkdir -p "$dst"
  local dry_run_arg=()
  if [[ "$execute" -eq 0 ]]; then
    dry_run_arg=(--dry-run)
  fi

  rsync -av --ignore-existing "${dry_run_arg[@]}" "$@" "${src}/" "${dst}/"
}

require_dir "$src_root"

echo "Source:      $src_base"
echo "Destination: $dst_base"
echo "Mode:        $([[ "$execute" -eq 1 ]] && echo execute || echo dry-run)"
echo

if command -v condor_q >/dev/null 2>&1; then
  active_recovery_jobs="$(condor_q "$recovery_cluster" -af ProcId 2>/dev/null | wc -l || true)"
  if [[ "${active_recovery_jobs:-0}" -gt 0 ]]; then
    echo "Recovery cluster $recovery_cluster still has $active_recovery_jobs active jobs."
  else
    echo "Recovery cluster $recovery_cluster has no active jobs in condor_q."
  fi
  echo
fi

source_file_count="$(count_files "$src_root")"
source_unique_count="$(count_unique_jobs "$src_root")"
source_duplicates="$(duplicate_jobs "$src_root" || true)"
source_missing="$(missing_jobs "$src_root" || true)"

echo "Source ROOT files:       $source_file_count"
echo "Source unique job ids:   $source_unique_count / $expected_jobs"

if [[ -n "$source_duplicates" ]]; then
  echo "Duplicate logical job ids in source:"
  echo "$source_duplicates"
fi

if [[ -n "$source_missing" ]]; then
  echo "Missing logical job ids in source:"
  echo "$source_missing"
fi

if [[ "$allow_incomplete" -eq 0 ]]; then
  if [[ "$source_unique_count" -ne "$expected_jobs" || -n "$source_duplicates" || -n "$source_missing" ]]; then
    echo
    echo "Source production is not migration-ready. Re-run after the Close Packing jobs finish." >&2
    echo "Use --allow-incomplete only for a deliberate partial dry run or diagnostic copy." >&2
    exit 1
  fi
fi

echo
echo "Copying Close Packing ROOT outputs..."
copy_dir_contents "$src_root" "$dst_root" --include='hf_CLOSEPACKING_cluster*_job*.root' --exclude='*'

if [[ -d "$src_logs" ]]; then
  echo
  echo "Copying Close Packing logs..."
  copy_dir_contents "$src_logs" "$dst_logs"
fi

if [[ "$copy_workdirs" -eq 1 ]]; then
  require_dir "$src_jobs"
  echo
  echo "Copying Close Packing work directories..."
  copy_dir_contents "$src_jobs" "$dst_jobs"
fi

if [[ "$execute" -eq 1 ]]; then
  echo
  echo "Destination ROOT files:     $(count_files "$dst_root")"
  echo "Destination unique job ids: $(count_unique_jobs "$dst_root") / $expected_jobs"
  destination_missing="$(missing_jobs "$dst_root" || true)"
  if [[ -n "$destination_missing" ]]; then
    echo "Destination still missing logical job ids:"
    echo "$destination_missing"
    exit 1
  fi
else
  echo
  echo "Dry run complete. Re-run with --execute after the source production is complete."
fi
