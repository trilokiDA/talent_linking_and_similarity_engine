"""
pipeline.py -- ATLAS End-to-End Pipeline
==========================================
Runs every step from raw data normalization through to final
hybrid (deterministic + ML) matching.

Step order
----------
  1. Normalize          -- normalize.py
  2. Train FastText     -- train_fasttext.py
  3. Train ML models    -- train_ml_models.py
  4. Hybrid matching    -- hybrid_matching.py

Usage
-----
  # Run the full pipeline
  python scripts/pipeline.py

  # Skip already-completed steps (useful after a partial run)
  python scripts/pipeline.py --skip-normalize --skip-train-fasttext

  # Run only normalization and deterministic matching (no ML)
  python scripts/pipeline.py --no-ml

  # List available flags
  python scripts/pipeline.py --help
"""

import sys
import time
import argparse
import traceback
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _section(title):
    width = 70
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width)


def _subsection(title):
    print("\n" + "-" * 60)
    print(f"  {title}")
    print("-" * 60)


def _step_result(step_name, ok, elapsed):
    status = "[OK]" if ok else "[FAILED]"
    print(f"\n{status} {step_name} finished in {elapsed:.1f}s")


def _run_step(step_name, fn, *args, **kwargs):
    """Run fn and return (success, elapsed_seconds)."""
    _subsection(f"STEP: {step_name}")
    start = time.time()
    try:
        fn(*args, **kwargs)
        elapsed = time.time() - start
        _step_result(step_name, True, elapsed)
        return True, elapsed
    except Exception as exc:
        elapsed = time.time() - start
        print(f"\n[ERROR] {step_name} raised an exception:")
        traceback.print_exc()
        _step_result(step_name, False, elapsed)
        return False, elapsed


# ---------------------------------------------------------------------------
# Step implementations (thin wrappers around each script's main())
# ---------------------------------------------------------------------------

def step_normalize():
    """Step 1 -- Normalize raw data from all three sources."""
    import normalize
    normalize.main()


def step_train_fasttext():
    """Step 2 -- Train a FastText model on the normalized profiles."""
    import train_fasttext
    train_fasttext.main()


def step_train_ml_models():
    """Step 3 -- Fit TF-IDF / SVD name & location embedders and save to disk."""
    import train_ml_models
    train_ml_models.main()


def step_hybrid_matching():
    """Step 4 -- Deterministic matching, then ML matching for leftovers."""
    import hybrid_matching
    hybrid_matching.main()


# ---------------------------------------------------------------------------
# Pre-flight checks
# ---------------------------------------------------------------------------

def _check_data_lake(base_dir):
    """Warn if no raw data files are found in data-lake/."""
    data_lake = base_dir / "data-lake"
    sources = ["coresignal", "rocketreach", "borealis"]
    found = False
    for source in sources:
        source_dir = data_lake / source
        if source_dir.exists() and any(source_dir.rglob("*.json")):
            found = True
    if not found:
        print(
            "[WARNING] No raw JSON files found under data-lake/.\n"
            "  Run  python scripts/generate_dummy_data.py  to create sample data,\n"
            "  or place your own files in data-lake/{coresignal,rocketreach,borealis}/."
        )
    return found


def _check_models_exist(base_dir):
    """Return True if pre-trained model artefacts already exist."""
    models_dir = base_dir / "models" / "embeddings"
    required = [
        "name_tfidf_vectorizer.pkl",
        "name_svd_model.pkl",
        "location_tfidf_vectorizer.pkl",
        "location_svd_model.pkl",
    ]
    return all((models_dir / f).exists() for f in required)


def _check_fasttext_exists(base_dir):
    """Return True if a FastText model file already exists."""
    ft_dir = base_dir / "models" / "fasttext"
    return ft_dir.exists() and any(ft_dir.glob("*.bin"))


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="ATLAS end-to-end pipeline: normalize -> train -> match"
    )
    parser.add_argument(
        "--skip-normalize",
        action="store_true",
        help="Skip normalization (use existing processed-data/normalization/)",
    )
    parser.add_argument(
        "--skip-train-fasttext",
        action="store_true",
        help="Skip FastText training (use existing models/fasttext/)",
    )
    parser.add_argument(
        "--skip-train-ml",
        action="store_true",
        help="Skip ML model training (use existing models/embeddings/)",
    )
    parser.add_argument(
        "--no-ml",
        action="store_true",
        help=(
            "Run only normalization + deterministic matching "
            "(skips FastText, ML training, and ML matching). "
            "Useful for a quick first pass."
        ),
    )
    return parser.parse_args()


def main():
    args = parse_args()

    pipeline_start = time.time()

    _section("ATLAS PIPELINE -- START")

    # Locate project root (two levels up from this script)
    base_dir = Path(__file__).resolve().parent.parent
    print(f"  Project root : {base_dir}")
    print(f"  Scripts dir  : {Path(__file__).resolve().parent}")

    # Add scripts dir to sys.path so cross-script imports work
    scripts_dir = str(Path(__file__).resolve().parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    # Pre-flight
    _section("PRE-FLIGHT CHECKS")
    _check_data_lake(base_dir)

    # ------------------------------------------------------------------
    # Decide which steps to run
    # ------------------------------------------------------------------
    run_normalize       = not args.skip_normalize
    run_train_fasttext  = not (args.skip_train_fasttext or args.no_ml)
    run_train_ml        = not (args.skip_train_ml or args.no_ml)
    run_matching        = True   # always run matching

    # Auto-correct: warn if artefacts are missing despite skip flags
    if args.skip_train_fasttext and not _check_fasttext_exists(base_dir):
        print(
            "[WARNING] --skip-train-fasttext requested but no FastText model found. "
            "Will train FastText anyway."
        )
        run_train_fasttext = not args.no_ml

    if args.skip_train_ml and not _check_models_exist(base_dir):
        print(
            "[WARNING] --skip-train-ml requested but no ML model artefacts found. "
            "Will train ML models anyway."
        )
        run_train_ml = not args.no_ml

    # Print the planned steps
    _section("PIPELINE PLAN")
    steps_plan = [
        ("Step 1 -- Normalize",           run_normalize),
        ("Step 2 -- Train FastText",       run_train_fasttext),
        ("Step 3 -- Train ML models",      run_train_ml),
        ("Step 4 -- Hybrid Matching",      run_matching),
    ]
    for name, will_run in steps_plan:
        marker = "  [RUN]  " if will_run else "  [SKIP] "
        print(f"{marker}{name}")

    # ------------------------------------------------------------------
    # Execute steps
    # ------------------------------------------------------------------
    results = {}   # step_name -> (success, elapsed)

    _section("EXECUTING PIPELINE")

    # Step 1 -- Normalize
    if run_normalize:
        ok, elapsed = _run_step("Normalize", step_normalize)
        results["Normalize"] = (ok, elapsed)
        if not ok:
            print("\n[FATAL] Normalization failed. Cannot continue.")
            sys.exit(1)
    else:
        print("\n[SKIP] Normalize -- using existing processed-data/normalization/")

    # Step 2 -- Train FastText
    if run_train_fasttext:
        ok, elapsed = _run_step("Train FastText", step_train_fasttext)
        results["Train FastText"] = (ok, elapsed)
        if not ok:
            print(
                "\n[WARNING] FastText training failed. "
                "ML matching will fall back to TF-IDF-only embeddings."
            )
    else:
        print("\n[SKIP] Train FastText -- using existing model(s) in models/fasttext/")

    # Step 3 -- Train ML models
    if run_train_ml:
        ok, elapsed = _run_step("Train ML Models", step_train_ml_models)
        results["Train ML Models"] = (ok, elapsed)
        if not ok:
            print(
                "\n[WARNING] ML model training failed. "
                "Hybrid matching will proceed (deterministic only if models are missing)."
            )
    else:
        print("\n[SKIP] Train ML Models -- using existing artefacts in models/embeddings/")

    # Step 4 -- Matching
    if args.no_ml:
        # Deterministic-only mode
        from deterministic_matching import main as det_main
        ok, elapsed = _run_step("Deterministic Matching", det_main)
        results["Deterministic Matching"] = (ok, elapsed)
    else:
        ok, elapsed = _run_step("Hybrid Matching", step_hybrid_matching)
        results["Hybrid Matching"] = (ok, elapsed)

    # ------------------------------------------------------------------
    # Final summary
    # ------------------------------------------------------------------
    pipeline_elapsed = time.time() - pipeline_start

    _section("PIPELINE SUMMARY")
    all_ok = True
    for step_name, (success, elapsed) in results.items():
        status = "OK    " if success else "FAILED"
        print(f"  [{status}]  {step_name:<30} {elapsed:>6.1f}s")
        if not success:
            all_ok = False

    print(f"\n  Total pipeline time: {pipeline_elapsed:.1f}s")

    if all_ok:
        print("\n  All steps completed successfully!")
        print(f"  Matched profiles -> processed-data/matched/")
    else:
        print("\n  One or more steps failed. Check the output above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
