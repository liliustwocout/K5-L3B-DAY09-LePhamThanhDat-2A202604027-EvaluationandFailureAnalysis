"""CI gate: compare a PR eval report with the main-branch baseline using the metric spec.

    python -m lab9.gate --pr reports/eval_workflow.json --baseline reports/baseline_v1.json

exit 0 = merge, exit 1 = blocked. Safety metrics: max 0, no averaging away.
Capability metrics: meet the floor AND the paired CI of (PR - main) is not entirely below 0.
Thresholds may only get stricter on the same eval-set version (ratchet).
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from lab8.console import utf8_stdio
from lab9 import stats
from lab9.graders import GRADERS
from lab9.eval import SPEC, load_spec, per_item


def integrity_check(pr: dict, base: dict, spec: dict, base_spec: dict | None = None) -> list[str]:
    """M7 (Expert): refuse to compare reports that cannot be trusted. Return a list of problems
    (empty = trustworthy). A gate that passes a broken report is worse than no gate.
    Must catch at least:
      - any metric value in pr["metrics"] that is NaN or inf
      - len(pr["rows"]) != manifest items x len(manifest seeds)   (dropped / duplicated rows)
      - the (item_id, seed) set of PR differs from the baseline's (cherry-picked seeds/items)
      - pr["evaluator_failures"] non-empty, or a row whose value for a graded spec metric is
        None (a crashed grader silently scores as "missing" and drops out of the mean)
      - base_spec given and a threshold in spec is LOOSER than in base_spec for the same
        eval-set version (ratchet: max may not rise, min may not fall, a blocking metric may
        not become non-blocking, a metric may not disappear; the same for spec["slices"],
        including dropping no_significant_drop)
      - an item's slice tags in PR rows differ from the baseline's (relabelling an item out of a
        slice hides its regression from the slice gate)"""
    problems = []
    reference = {(r["item_id"], r["seed"]): set(r.get("slices", [])) for r in base["rows"]}
    manifest = pr["manifest"]
    rows = pr["rows"]
    seeds = set(manifest["seeds"])
    items = {r["item_id"] for r in rows}
    keys = {(r["item_id"], r["seed"]) for r in rows}
    if (len(items) != manifest["items"] or len(seeds) != len(manifest["seeds"])
            or len(rows) != len(keys) or keys != {(i, seed) for i in items for seed in seeds}
            or keys != reference.keys()):
        problems.append("incomplete, duplicate or different item/seed pairs")
    if pr.get("evaluator_failures"):
        problems.append("evaluator failures reported")
    if any(not isinstance(v, (int, float)) or not math.isfinite(v) for v in pr["metrics"].values()):
        problems.append("missing or non-finite aggregate")
    graded = [m["id"] for m in spec["metrics"] if m["id"] in GRADERS]
    for row in rows:
        key = (row["item_id"], row["seed"])
        if key in reference and set(row.get("slices", [])) != reference[key]:
            problems.append(f"changed slice membership at {key}")
            break
        if any(not isinstance(row.get(metric), bool) for metric in graded):
            problems.append(f"missing or invalid grader result at {key}")
            break
    if base_spec and base_spec["eval_set_version"] == spec["eval_set_version"]:
        for section in ("metrics", "slices"):
            def rule_id(rule):
                return rule["id"] if section == "metrics" else (rule["name"], rule["metric"])

            current = {rule_id(r): r for r in spec.get(section, [])}
            for old in base_spec.get(section, []):
                key = rule_id(old)
                new = current.get(key)
                if new is None or (old.get("blocking") and not new.get("blocking")):
                    problems.append(f"ratchet: removed or disabled {key}")
                    continue
                before, after = old.get("threshold", old), new.get("threshold", new)
                for field in ("min", "max", "max_increase"):
                    if field not in before:
                        continue
                    value = after.get(field)
                    if (not isinstance(value, (int, float)) or not math.isfinite(value)
                            or (value < before[field] if field == "min" else value > before[field])):
                        problems.append(f"ratchet: loosened {key} {field}")
                if before.get("no_significant_drop") and not after.get("no_significant_drop"):
                    problems.append(f"ratchet: removed paired CI for {key}")
    return problems


def slice_check(pr: dict, base: dict, spec: dict) -> tuple[list[str], list[str]]:
    """M5 (Advanced): an average can hide a regression on a small, important slice.
    For each entry of spec["slices"] ({"name", "metric", "min"?, "no_significant_drop"?, "blocking"}):
      - value = mean of per_item(pr, metric, slice_name=name)
      - fail if below "min", or if no_significant_drop and the paired CI over the slice's items
        lies entirely below 0
    Return (blocked ids like "slice:money_movement/pass_rate", report lines)."""
    blocked, lines = [], []
    bs = spec.get("bootstrap", {})
    for rule in spec.get("slices", []):
        name, metric = rule["name"], rule["metric"]
        tag = f"slice:{name}/{metric}"
        a, b = per_item(pr, metric, name), per_item(base, metric, name)
        failed = not a or a.keys() != b.keys()
        note = "missing or unpaired slice"
        if not failed:
            keys = sorted(a)
            value = sum(a.values()) / len(a)
            failed = value < rule.get("min", -math.inf)
            note = f"mean={value:.4f} items={len(keys)}"
            if rule.get("no_significant_drop"):
                delta, lo, hi = stats.paired_bootstrap(
                    [a[k] for k in keys], [b[k] for k in keys], rng=bs.get("rng", 2027),
                    n_resamples=bs.get("n_resamples", 1000), confidence=bs.get("confidence", 0.95))
                failed |= hi < 0
                note += f" Δ {delta:+.3f} CI [{lo:+.3f}, {hi:+.3f}]"
        if failed and rule.get("blocking"):
            blocked.append(tag)
        verdict = "BLOCK" if tag in blocked else "warn" if failed else "ok"
        lines.append(f"  {tag} {note} {verdict}")
    return blocked, lines


def check(pr: dict, base: dict, spec: dict, base_spec: dict | None = None) -> tuple[list[str], list[str]]:
    if pr["manifest"]["eval_set_sha"] != base["manifest"]["eval_set_sha"]:
        return ["eval_set_sha"], ["  EVAL SET differs from the baseline's: re-run the baseline on the same eval set"]
    problems = integrity_check(pr, base, spec, base_spec)
    if problems:
        return ["integrity"], [f"  INTEGRITY {p}" for p in problems]
    blocked, lines = [], []
    bs = spec.get("bootstrap", {})
    for m in spec["metrics"]:
        mid, th, val = m["id"], m.get("threshold", {}), pr["metrics"].get(m["id"])
        verdict, note = "ok", ""
        if val is None:
            verdict = "missing"
        elif "max" in th and val > th["max"]:
            verdict = "fail"
        elif "min" in th and val < th["min"]:
            verdict = "fail"
        elif "max_increase" in th and base["metrics"].get(mid):
            if val > base["metrics"][mid] * (1 + th["max_increase"]):
                verdict = "fail"
        if th.get("no_significant_drop") and val is not None:
            a, b = per_item(pr, mid), per_item(base, mid)
            keys = sorted(set(a) & set(b))
            d, lo, hi = stats.paired_bootstrap([a[k] for k in keys], [b[k] for k in keys],
                                               n_resamples=bs.get("n_resamples", 1000), rng=bs.get("rng", 2027),
                                               confidence=bs.get("confidence", 0.95))
            note = f"Δ {d:+.3f} CI [{lo:+.3f}, {hi:+.3f}]"
            if hi < 0:
                verdict = "fail"
        if verdict != "ok" and m.get("blocking"):
            blocked.append(mid)
        label = {"ok": "ok", "missing": "MISSING"}.get(verdict, "BLOCK" if m.get("blocking") else "warn")
        lines.append(f"  {mid:<22} {val!s:<8} {json.dumps(th):<40} {note:<28} {label}")
    if spec.get("slices"):
        sb, sl = slice_check(pr, base, spec)
        blocked += sb
        lines += sl
    return blocked, lines


def main(argv: list[str] | None = None) -> int:
    utf8_stdio()
    ap = argparse.ArgumentParser(prog="lab9.gate")
    ap.add_argument("--pr", required=True)
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--spec", default=str(SPEC))
    ap.add_argument("--base-spec", help="metric spec on main, for the ratchet check (M7)")
    args = ap.parse_args(argv)
    pr = json.loads(Path(args.pr).read_text(encoding="utf-8"))
    base = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    base_spec = load_spec(Path(args.base_spec)) if args.base_spec else None
    blocked, lines = check(pr, base, load_spec(Path(args.spec)), base_spec)
    print(f"gate: PR {pr['run_id']} vs main {base['run_id']} · eval set {pr['manifest']['eval_set_sha']}")
    print("\n".join(lines))
    if blocked:
        print(f"exit 1 — blocked: {', '.join(blocked)}")
        return 1
    print("exit 0 — merge")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
