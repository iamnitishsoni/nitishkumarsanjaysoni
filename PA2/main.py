#!/usr/bin/env python3
"""
CLI entry point for NYC 311 Data-Quality Layer (Fire AI PA2).
"""
import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.sample_data import generate_clean_nyc311_data
from src.injector import CorruptionInjector
from src.hybrid_pipeline import HybridDataQualityPipeline
from benchmark import run_benchmark


def main():
    parser = argparse.ArgumentParser(description="NYC 311 Data-Quality Layer (Fire AI PA2)")
    parser.add_argument("--benchmark", "-b", action="store_true", help="Run benchmark across all 12 corruptions & generate RESULTS_B.md")
    parser.add_argument("--demo", "-d", action="store_true", help="Run a quick live detection demo on an injected batch")
    parser.add_argument("--rows", type=int, default=1000, help="Number of rows for demo")

    args = parser.parse_args()

    if args.benchmark or len(sys.argv) == 1:
        run_benchmark()
        return

    if args.demo:
        print(f"\n🚀 Generating {args.rows} clean NYC 311 records...")
        clean_df = generate_clean_nyc311_data(n_rows=args.rows)
        injector = CorruptionInjector()
        
        print("💉 Injecting 3 corruption types: lat/lon swapped, closed < created, and status contradiction...")
        corrupt_df, _ = injector.inject(clean_df, "d_lat_lon_swapped", rate=0.03)
        corrupt_df, _ = injector.inject(corrupt_df, "h_closed_earlier_than_created", rate=0.03)
        corrupt_df, _ = injector.inject(corrupt_df, "k_resolution_contradicting_status", rate=0.03)

        pipeline = HybridDataQualityPipeline()
        print("🛡️ Running Hybrid Quality Gatekeeper...")
        results = pipeline.run_pipeline(corrupt_df)

        print("\n" + "=" * 65)
        print("📊 PIPELINE AUDIT REPORT")
        print("=" * 65)
        print(f"Total Records Inspected  : {results['total_rows']}")
        print(f"Total Quarantined Defects: {results['total_quarantined_rows']}")
        print(f"Clean Records Passed     : {results['clean_rows']}")
        print(f"Detection Latency        : {results['latency_ms']['total']} ms")
        print(f"Estimated Cost           : ${results['cost_usd']:.6f}")
        print("\nDefects Identified:")
        for defect, meta in results["anomalies_breakdown"].items():
            print(f"  • [{meta['tier']}] {defect} ({meta['count']} rows)")
        print("=" * 65)


if __name__ == "__main__":
    main()
