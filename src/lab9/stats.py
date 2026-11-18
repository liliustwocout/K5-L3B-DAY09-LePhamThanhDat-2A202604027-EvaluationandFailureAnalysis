"""Statistics students implement (M2 judge calibration, M4 paired bootstrap).

Rules: a judge is a classifier -- measure it like one. A higher mean is not
"better" until the paired CI of the difference excludes 0.
Reference values to self-check are in tests/test_lab9_stats.py.
"""

from __future__ import annotations

from collections.abc import Sequence

POS = "FAIL"   # the judge's job is to FIND failures, so FAIL is the positive class


def confusion(human: Sequence[str], judge: Sequence[str]) -> dict[str, int]:
    """tp/fp/fn/tn with FAIL as positive."""
    counts = dict(tp=0, fp=0, fn=0, tn=0)
    for actual, predicted in zip(human, judge, strict=True):
        if actual not in ("PASS", POS) or predicted not in ("PASS", POS):
            raise ValueError("Expected PASS or FAIL")
        if predicted == POS:
            counts["tp" if actual == POS else "fp"] += 1
        else:
            counts["fn" if actual == POS else "tn"] += 1
    return counts


def precision_recall(human: Sequence[str], judge: Sequence[str]) -> tuple[float, float]:
    counts = confusion(human, judge)
    hits = counts["tp"]
    flagged = hits + counts["fp"]
    failures = hits + counts["fn"]
    return (hits / flagged if flagged else 0.0, hits / failures if failures else 0.0)


def cohen_kappa(human: Sequence[str], judge: Sequence[str]) -> float:
    counts = confusion(human, judge)
    n = len(human)
    failures = counts["tp"] + counts["fn"]
    flagged = counts["tp"] + counts["fp"]
    chance = failures * flagged + (n - failures) * (n - flagged)
    denominator = n * n - chance
    if not denominator:
        raise ValueError("Kappa undefined for empty or identical constant labels")
    return (n * (counts["tp"] + counts["tn"]) - chance) / denominator


def rogan_gladen(observed_rate: float, sensitivity: float, specificity: float) -> float:
    """Correct the observed failure rate and clip to the probability range."""
    denominator = sensitivity + specificity - 1
    if denominator == 0:
        return float("nan")
    return min(1.0, max(0.0, (observed_rate + specificity - 1) / denominator))


def paired_bootstrap(a: Sequence[float], b: Sequence[float], *, n_resamples: int = 1000,
                     rng: int = 2027, confidence: float = 0.95) -> tuple[float, float, float]:
    """a[i], b[i] = per-item mean over seeds, SAME items, SAME order.
    Return (mean(a)-mean(b), lo, hi) with scipy.stats.bootstrap(paired=True, method="percentile",
    rng=numpy.random.default_rng(rng)). If a == b everywhere return (0.0, 0.0, 0.0)."""
    import numpy as np
    from scipy.stats import bootstrap

    left, right = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if left.ndim != 1 or left.shape != right.shape or not left.size:
        raise ValueError("Expected two nonempty, aligned sequences")
    delta = float(np.mean(left - right))
    if left.size == 1 or np.array_equal(left, right):
        return delta, delta, delta

    def difference(x, y, axis):
        return np.mean(x - y, axis=axis)

    interval = bootstrap((left, right), difference, paired=True, method="percentile",
                         n_resamples=n_resamples, confidence_level=confidence,
                         rng=np.random.default_rng(rng)).confidence_interval
    return delta, float(interval.low), float(interval.high)


def pass_at_k(n: int, c: int, k: int) -> float:
    """Probability that AT LEAST ONE of k trials drawn from n (c of them passing) passes.
    Unbiased estimator (Chen et al. 2021): 1 - C(n-c, k) / C(n, k). Raise ValueError if k > n."""
    # TODO M6
    raise NotImplementedError


def pass_hat_k(n: int, c: int, k: int) -> float:
    """pass^k (tau-bench, Yao et al. 2024): probability that ALL k trials drawn from n pass.
    Unbiased estimator: C(c, k) / C(n, k). Raise ValueError if k > n.
    pass^k <= pass@1 <= pass@k; a reliable agent keeps pass^k close to pass@1."""
    # TODO M6
    raise NotImplementedError
