#include <Pythia8/Pythia.h>

#include <iostream>

int main() {
  Pythia8::Pythia pythia;
  const int dMeson = pythia.particleData.baryonNumberType(411);
  const int antiDMeson = pythia.particleData.baryonNumberType(-411);
  const int lambdaB = pythia.particleData.baryonNumberType(5122);
  const int antiLambdaB = pythia.particleData.baryonNumberType(-5122);
  const bool valid =
      !pythia.particleData.name(411).empty() && dMeson == 0 &&
      antiDMeson == 0 && lambdaB == 3 && antiLambdaB == -3;
  std::cout << "PYTHIA_RUNTIME_TEST valid="
            << (valid ? "true" : "false")
            << " D=" << dMeson << " antiD=" << antiDMeson
            << " LambdaB=" << lambdaB
            << " antiLambdaB=" << antiLambdaB << "\n";
  return valid ? 0 : 1;
}
