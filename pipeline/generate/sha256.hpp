#ifndef HADRONIZATION_SHA256_H
#define HADRONIZATION_SHA256_H

#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace Hadronization {

// Small dependency-free SHA-256 implementation for immutable metadata
// digests. The streaming interface permits provenance checks of multi-GB ROOT
// files without loading them into memory.
class Sha256 {
 public:
  Sha256()
      : hash_{0x6a09e667U, 0xbb67ae85U, 0x3c6ef372U, 0xa54ff53aU,
              0x510e527fU, 0x9b05688cU, 0x1f83d9abU, 0x5be0cd19U} {}

  void Update(const char* input, std::size_t size) {
    if (finalized_) {
      throw std::logic_error("cannot update a finalized SHA-256 digest");
    }
    if (size > (std::numeric_limits<std::uint64_t>::max() - bitLength_) / 8U) {
      throw std::overflow_error("SHA-256 input length exceeds 64-bit domain");
    }
    bitLength_ += static_cast<std::uint64_t>(size) * 8U;
    std::size_t offset = 0;
    if (bufferSize_ != 0U) {
      const std::size_t take = std::min(size, 64U - bufferSize_);
      std::copy(input, input + take, buffer_.begin() + bufferSize_);
      bufferSize_ += take;
      offset += take;
      if (bufferSize_ == 64U) {
        Transform(reinterpret_cast<const std::uint8_t*>(buffer_.data()));
        bufferSize_ = 0U;
      }
    }
    while (offset + 64U <= size) {
      Transform(reinterpret_cast<const std::uint8_t*>(input + offset));
      offset += 64U;
    }
    if (offset < size) {
      bufferSize_ = size - offset;
      std::copy(input + offset, input + size, buffer_.begin());
    }
  }

  void Update(std::string_view input) { Update(input.data(), input.size()); }

  std::string FinalHex() {
    if (!finalized_) Finalize();
    std::ostringstream digest;
    digest << std::hex << std::setfill('0');
    for (const std::uint32_t word : hash_) digest << std::setw(8) << word;
    return digest.str();
  }

 private:
  static constexpr std::array<std::uint32_t, 64> constants_{
      0x428a2f98U, 0x71374491U, 0xb5c0fbcfU, 0xe9b5dba5U,
      0x3956c25bU, 0x59f111f1U, 0x923f82a4U, 0xab1c5ed5U,
      0xd807aa98U, 0x12835b01U, 0x243185beU, 0x550c7dc3U,
      0x72be5d74U, 0x80deb1feU, 0x9bdc06a7U, 0xc19bf174U,
      0xe49b69c1U, 0xefbe4786U, 0x0fc19dc6U, 0x240ca1ccU,
      0x2de92c6fU, 0x4a7484aaU, 0x5cb0a9dcU, 0x76f988daU,
      0x983e5152U, 0xa831c66dU, 0xb00327c8U, 0xbf597fc7U,
      0xc6e00bf3U, 0xd5a79147U, 0x06ca6351U, 0x14292967U,
      0x27b70a85U, 0x2e1b2138U, 0x4d2c6dfcU, 0x53380d13U,
      0x650a7354U, 0x766a0abbU, 0x81c2c92eU, 0x92722c85U,
      0xa2bfe8a1U, 0xa81a664bU, 0xc24b8b70U, 0xc76c51a3U,
      0xd192e819U, 0xd6990624U, 0xf40e3585U, 0x106aa070U,
      0x19a4c116U, 0x1e376c08U, 0x2748774cU, 0x34b0bcb5U,
      0x391c0cb3U, 0x4ed8aa4aU, 0x5b9cca4fU, 0x682e6ff3U,
      0x748f82eeU, 0x78a5636fU, 0x84c87814U, 0x8cc70208U,
      0x90befffaU, 0xa4506cebU, 0xbef9a3f7U, 0xc67178f2U};

  static std::uint32_t RotateRight(std::uint32_t value, unsigned amount) {
    return (value >> amount) | (value << (32U - amount));
  }

  void Transform(const std::uint8_t* block) {
    std::array<std::uint32_t, 64> words{};
    for (std::size_t index = 0; index < 16U; ++index) {
      const std::size_t byte = 4U * index;
      words[index] =
          (static_cast<std::uint32_t>(block[byte]) << 24U) |
          (static_cast<std::uint32_t>(block[byte + 1U]) << 16U) |
          (static_cast<std::uint32_t>(block[byte + 2U]) << 8U) |
          static_cast<std::uint32_t>(block[byte + 3U]);
    }
    for (std::size_t index = 16U; index < words.size(); ++index) {
      const std::uint32_t s0 =
          RotateRight(words[index - 15U], 7U) ^
          RotateRight(words[index - 15U], 18U) ^
          (words[index - 15U] >> 3U);
      const std::uint32_t s1 =
          RotateRight(words[index - 2U], 17U) ^
          RotateRight(words[index - 2U], 19U) ^
          (words[index - 2U] >> 10U);
      words[index] =
          words[index - 16U] + s0 + words[index - 7U] + s1;
    }

    std::uint32_t a = hash_[0];
    std::uint32_t b = hash_[1];
    std::uint32_t c = hash_[2];
    std::uint32_t d = hash_[3];
    std::uint32_t e = hash_[4];
    std::uint32_t f = hash_[5];
    std::uint32_t g = hash_[6];
    std::uint32_t h = hash_[7];
    for (std::size_t index = 0; index < words.size(); ++index) {
      const std::uint32_t sigma1 =
          RotateRight(e, 6U) ^ RotateRight(e, 11U) ^ RotateRight(e, 25U);
      const std::uint32_t choose = (e & f) ^ ((~e) & g);
      const std::uint32_t temporary1 =
          h + sigma1 + choose + constants_[index] + words[index];
      const std::uint32_t sigma0 =
          RotateRight(a, 2U) ^ RotateRight(a, 13U) ^ RotateRight(a, 22U);
      const std::uint32_t majority = (a & b) ^ (a & c) ^ (b & c);
      const std::uint32_t temporary2 = sigma0 + majority;
      h = g;
      g = f;
      f = e;
      e = d + temporary1;
      d = c;
      c = b;
      b = a;
      a = temporary1 + temporary2;
    }
    hash_[0] += a;
    hash_[1] += b;
    hash_[2] += c;
    hash_[3] += d;
    hash_[4] += e;
    hash_[5] += f;
    hash_[6] += g;
    hash_[7] += h;
  }

  void Finalize() {
    if (bufferSize_ >= buffer_.size()) {
      throw std::logic_error("invalid SHA-256 internal buffer size");
    }
    std::array<std::uint8_t, 128> tail{};
    for (std::size_t index = 0; index < bufferSize_; ++index) {
      tail[index] = static_cast<std::uint8_t>(buffer_[index]);
    }
    tail[bufferSize_] = 0x80U;
    const std::size_t tailSize = bufferSize_ < 56U ? 64U : 128U;
    for (int shift = 56; shift >= 0; shift -= 8) {
      tail[tailSize - 8U + static_cast<std::size_t>((56 - shift) / 8)] =
          static_cast<std::uint8_t>((bitLength_ >> shift) & 0xffU);
    }
    Transform(tail.data());
    if (tailSize == 128U) Transform(tail.data() + 64U);
    finalized_ = true;
  }

  std::array<std::uint32_t, 8> hash_;
  std::array<char, 64> buffer_{};
  std::size_t bufferSize_ = 0;
  std::uint64_t bitLength_ = 0;
  bool finalized_ = false;
};

inline std::string Sha256Hex(std::string_view input) {
  Sha256 digest;
  digest.Update(input);
  return digest.FinalHex();
}

inline std::string Sha256FileHex(const std::string& path) {
  std::ifstream stream(path, std::ios::binary);
  if (!stream) throw std::runtime_error("cannot open file for SHA-256: " + path);
  Sha256 digest;
  std::array<char, 1024U * 1024U> buffer{};
  while (stream) {
    stream.read(buffer.data(), static_cast<std::streamsize>(buffer.size()));
    const std::streamsize count = stream.gcount();
    if (count > 0) digest.Update(buffer.data(), static_cast<std::size_t>(count));
  }
  if (!stream.eof()) {
    throw std::runtime_error("failed while hashing file: " + path);
  }
  return digest.FinalHex();
}

}  // namespace Hadronization

#endif
