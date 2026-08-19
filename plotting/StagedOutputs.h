// Temp-then-promote for gate-guarded figure outputs.
//
// WHY THIS EXISTS. The balancing canvases are written by writeCanvasToFiles and
// the boundary-receipt gate runs AFTERWARDS. So the old order was: write the new
// PNG/PDF/.C straight into the published directory, then check whether this run
// was allowed to publish at all. When the gate threw -- a receipt disagreeing
// with the frozen one is exactly the case it exists to catch -- the directory
// had already been half-rewritten. That is how
// `PolishProposal.mixed_preamendment_20260817T224548` came to exist: a directory
// holding some files from a rejected run and some from an accepted one, with
// nothing in the bytes to say which was which.
//
// A digest taken from such a directory is worse than no digest, because it looks
// exactly like a good one.
//
// THE RULE. Gate-guarded outputs are written to a staging directory beside the
// destination and are moved into place only after the gate has passed. A failed
// gate leaves the published directory byte-for-byte untouched.
//
// Promotion uses rename(2) within the same parent directory, so each file
// appears at its final path atomically and no reader can observe a half-written
// figure.
//
// Deliberately free of ROOT so the behaviour can be tested by compiling this
// header alone -- see tests/test_staged_outputs.py.

#ifndef HADRONIZATION_STAGED_OUTPUTS_H
#define HADRONIZATION_STAGED_OUTPUTS_H

#include <dirent.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

#include <cerrno>
#include <cstdio>
#include <cstring>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

namespace Hadronization {
namespace StagedOutputs {

inline std::string StagingDirFor(const std::string& finalDir)
{
  return finalDir + ".staging";
}

inline void MakeDirectories(const std::string& path)
{
  if (path.empty()) return;
  std::string built;
  size_t start = 0;
  if (path[0] == '/') {
    built = "/";
    start = 1;
  }
  while (start <= path.size()) {
    const size_t slash = path.find('/', start);
    const std::string component =
        path.substr(start, slash == std::string::npos ? std::string::npos
                                                      : slash - start);
    if (!component.empty()) {
      if (!built.empty() && built.back() != '/') built += "/";
      built += component;
      if (::mkdir(built.c_str(), 0755) != 0 && errno != EEXIST) {
        throw std::runtime_error("Could not create directory " + built + ": " +
                                 std::strerror(errno));
      }
    }
    if (slash == std::string::npos) break;
    start = slash + 1;
  }
}

inline std::vector<std::string> EntriesOf(const std::string& dir)
{
  std::vector<std::string> names;
  DIR* handle = ::opendir(dir.c_str());
  if (handle == nullptr) return names;
  while (struct dirent* entry = ::readdir(handle)) {
    const std::string name = entry->d_name;
    if (name == "." || name == "..") continue;
    names.push_back(name);
  }
  ::closedir(handle);
  return names;
}

// Tracks every destination staged during a run.
//
// Stage() hands back the directory to write into; Promote() moves everything
// into place once the gate has passed; Discard() throws the staging away and
// leaves the destination untouched. Doing NEITHER is also safe: the destination
// is only ever modified by Promote().
class Staging {
 public:
  std::string Stage(const std::string& finalDir)
  {
    const std::string staging = StagingDirFor(finalDir);
    if (finalDirs_.insert(finalDir).second) {
      // First use this run: clear any staging left by an earlier aborted run,
      // so a promotion can never carry a stale file into the destination.
      RemoveTree(staging);
    }
    MakeDirectories(staging);
    return staging;
  }

  // Move staged files into their destinations. Call ONLY after the gate passes.
  // Returns the number of files promoted.
  std::size_t Promote()
  {
    std::size_t moved = 0;
    for (const std::string& finalDir : finalDirs_) {
      const std::string staging = StagingDirFor(finalDir);
      MakeDirectories(finalDir);
      for (const std::string& name : EntriesOf(staging)) {
        const std::string from = staging + "/" + name;
        const std::string to = finalDir + "/" + name;
        if (::rename(from.c_str(), to.c_str()) != 0) {
          throw std::runtime_error("Could not promote " + from + " to " + to +
                                   ": " + std::strerror(errno));
        }
        ++moved;
      }
      ::rmdir(staging.c_str());
    }
    finalDirs_.clear();
    return moved;
  }

  void Discard()
  {
    for (const std::string& finalDir : finalDirs_) {
      RemoveTree(StagingDirFor(finalDir));
    }
    finalDirs_.clear();
  }

  bool empty() const { return finalDirs_.empty(); }
  std::size_t destinations() const { return finalDirs_.size(); }

 private:
  static void RemoveTree(const std::string& dir)
  {
    for (const std::string& name : EntriesOf(dir)) {
      const std::string path = dir + "/" + name;
      if (::remove(path.c_str()) != 0) {
        // A nested directory: recurse, then retry.
        RemoveTree(path);
        ::rmdir(path.c_str());
      }
    }
    ::rmdir(dir.c_str());
  }

  std::set<std::string> finalDirs_;
};

}  // namespace StagedOutputs
}  // namespace Hadronization

#endif  // HADRONIZATION_STAGED_OUTPUTS_H
