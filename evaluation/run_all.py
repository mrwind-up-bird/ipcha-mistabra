# ipcha/evaluation/run_all.py

"""
Orchestrator for the IPCHA evaluation suite.

Runs all evaluation steps in sequence:
  Step 1 — Generate synthetic corpus
  Step 2 — RQ1: metric comparison (TF-IDF IS_w vs NLI ISce)
  Step 3 — Print summary report
"""

import logging


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    # Step 1: Generate synthetic corpus
    from ipcha.evaluation.corpus.synthetic_generator import generate_all

    cases = generate_all("ipcha/evaluation/results/synthetic_corpus.json")
    print(f"\n{'='*60}")
    print(f"Corpus generated: {len(cases)} cases")
    print(f"{'='*60}\n")

    # Step 2: Run metric comparison (RQ1)
    from ipcha.evaluation.runners.metric_eval import run_metric_comparison

    results = run_metric_comparison(
        "ipcha/evaluation/results/synthetic_corpus.json",
        "ipcha/evaluation/results/metric_eval.json",
    )

    # Step 3: Print summary
    print(f"\n{'='*60}")
    print("EVALUATION RESULTS SUMMARY")
    print(f"{'='*60}")
    print(f"Total cases: {results['n']}")
    print(f"TF-IDF mean score: {results['tfidf_mean']:.4f}")
    print(f"NLI mean score:    {results['nli_mean']:.4f}")

    clf = results.get("classification", {})
    if "tfidf" in clf and "nli" in clf:
        print(f"\n--- Classification Metrics ---")
        print(f"{'Metric':<12} {'TF-IDF':>10} {'NLI':>10}")
        print(f"{'-'*32}")
        for key in ["accuracy", "precision", "recall", "f1"]:
            tf_val = clf["tfidf"].get(key, 0)
            nli_val = clf["nli"].get(key, 0)
            print(f"{key:<12} {tf_val:>10.4f} {nli_val:>10.4f}")
        print(f"\nTF-IDF threshold: {clf['tfidf'].get('threshold', 'N/A')}")
        print(f"NLI threshold:    {clf['nli'].get('threshold', 'N/A')}")

    paired = results.get("paired_comparison", {})
    if "test" in paired:
        print(f"\n--- Paired Comparison ({paired['test']}) ---")
        print(f"Statistic:       {paired.get('statistic', 'N/A'):.4f}")
        print(f"p-value:         {paired.get('p_value', 'N/A'):.6f}")
        print(f"Effect size (d): {paired.get('effect_size_d', 'N/A'):.4f}")
        print(f"Mean difference: {paired.get('mean_difference', 'N/A'):.4f}")
        print(f"95% CI:          {paired.get('ci_95', 'N/A')}")
        print(f"Significant:     {paired.get('significant', 'N/A')}")

    mcnemar = results.get("mcnemar", {})
    if "test" in mcnemar:
        print(f"\n--- McNemar's Test ---")
        print(f"Improved (TF-IDF wrong, NLI right): {mcnemar.get('improved', 0)}")
        print(f"Degraded (TF-IDF right, NLI wrong): {mcnemar.get('degraded', 0)}")
        print(f"Statistic:  {mcnemar.get('statistic', 'N/A'):.4f}")
        print(f"p-value:    {mcnemar.get('p_value', 'N/A'):.6f}")
        print(f"Significant: {mcnemar.get('significant', 'N/A')}")

    print(f"\n{'='*60}")
    print(f"Results saved to: ipcha/evaluation/results/metric_eval.json")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
