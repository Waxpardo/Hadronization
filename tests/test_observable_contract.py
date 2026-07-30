#!/usr/bin/env python3
import math
import statistics


def sem(values):
    return statistics.stdev(values) / math.sqrt(len(values))


def main():
    # Directed conditional pairs: each positive trigger sees all negative
    # associates and all other positive associates.
    for n in range(1, 8):
        n_os = n * n
        n_ss = n * (n - 1)
        conditional = (n_os - n_ss) / n
        legacy_half_ss = (n_os - 0.5 * n_ss) / n
        assert conditional == 1
        assert legacy_half_ss == (n + 1) / 2

    # Self pairs are excluded by identity, not by species.
    assert 2 * (2 - 1) == 2
    assert 3 * (3 - 1) == 6

    values = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    expected = math.sqrt(sum((x - 5.5) ** 2 for x in values) / (10 * 9))
    assert math.isclose(sem(values), expected, rel_tol=1e-15)

    # Nonlinear ratios are formed within blocks.
    numerator = [2.0 + i for i in range(10)]
    denominator = [1.0 + 0.5 * i for i in range(10)]
    block_ratios = [a / b for a, b in zip(numerator, denominator)]
    assert not math.isclose(
        sem(block_ratios),
        math.hypot(sem(numerator) / statistics.mean(denominator),
                   statistics.mean(numerator) * sem(denominator)
                   / statistics.mean(denominator) ** 2),
    )
    print("observable-contract tests passed")


if __name__ == "__main__":
    main()
