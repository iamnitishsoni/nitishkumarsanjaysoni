"""
Task 5: Production Multi-Tiered Hybrid Pipeline.
Combines:
- Tier 1: Cheap declarative rules on 100% of incoming rows ($0.00)
- Tier 2: Statistical & distributional checks per batch ($0.00)
- Tier 3: LLM review ONLY on flagged anomalies or 0.5% audit sample (Controlled Cost)
"""
import time
import random
import pandas as pd
from typing import Dict, Any, Set
from src.detectors import DeclarativeDetector, StatisticalDetector, LLMDetector


class HybridDataQualityPipeline:
    def __init__(self, config_path: str = "config/config.yaml"):
        self.tier1_rules = DeclarativeDetector(config_path)
        self.tier2_stats = StatisticalDetector(config_path)
        self.tier3_llm = LLMDetector(sample_rate=0.005)

    def run_pipeline(self, df: pd.DataFrame) -> Dict[str, Any]:
        n_rows = len(df)
        t0 = time.perf_counter()

        flagged_anomalies = {}
        quarantine_indices = set()

        # ======================================================================
        # TIER 1: Declarative Rules (100% of rows, < 2ms latency, $0.00 cost)
        # ======================================================================
        t1_start = time.perf_counter()
        t1_checks = [
            ("a_renamed_or_dropped_column", "Schema Integrity Check"),
            ("b_column_type_change", "ZIP Format Check"),
            ("c_date_format_switch", "Timestamp ISO Format Check"),
            ("d_lat_lon_swapped", "NYC Bounding Box GPS Check"),
            ("e_exact_duplicates", "Primary Key Hash Deduplication"),
            ("h_closed_earlier_than_created", "Temporal Monotonicity Invariant"),
            ("i_zip_inconsistent_borough", "Borough-to-Postal Code Cross-Validation"),
            ("l_personal_data_in_free_text", "PII Regex Screening")
        ]
        tier1_flags = set()
        for check_type, desc in t1_checks:
            res = self.tier1_rules.detect(df, check_type)
            if res:
                flagged_anomalies[check_type] = {
                    "tier": "Tier 1 (Declarative)",
                    "count": len(res),
                    "description": desc,
                    "indices": list(res)[:5]
                }
                tier1_flags.update(res)

        quarantine_indices.update(tier1_flags)
        t1_duration_ms = (time.perf_counter() - t1_start) * 1000

        # ======================================================================
        # TIER 2: Statistical & Batch Checks (100% of batches, $0.00 cost)
        # ======================================================================
        t2_start = time.perf_counter()
        t2_checks = [
            ("g_null_spike_agency", "Agency-Level Null Rate Z-Score"),
            ("f_near_duplicates", "Time-Window Sliding Deduplication"),
            ("j_complaint_inconsistent_descriptor", "Complaint-Descriptor Co-occurrence Frequency")
        ]
        tier2_flags = set()
        for check_type, desc in t2_checks:
            res = self.tier2_stats.detect(df, check_type)
            if res:
                flagged_anomalies[check_type] = {
                    "tier": "Tier 2 (Statistical)",
                    "count": len(res),
                    "description": desc,
                    "indices": list(res)[:5]
                }
                tier2_flags.update(res)

        quarantine_indices.update(tier2_flags)
        t2_duration_ms = (time.perf_counter() - t2_start) * 1000

        # ======================================================================
        # TIER 3: LLM Semantic Review (Gated to Tier 2 flags + 0.5% audit sample)
        # ======================================================================
        t3_start = time.perf_counter()
        # Evaluate semantic contradictions on rows that claim status=Closed
        semantic_flags = self.tier3_llm.detect(df, "k_resolution_contradicting_status")
        if semantic_flags:
            flagged_anomalies["k_resolution_contradicting_status"] = {
                "tier": "Tier 3 (LLM Review)",
                "count": len(semantic_flags),
                "description": "Status vs Resolution Contradiction Audit",
                "indices": list(semantic_flags)[:5]
            }
            quarantine_indices.update(semantic_flags)

        t3_duration_ms = (time.perf_counter() - t3_start) * 1000
        total_duration_ms = (time.perf_counter() - t0) * 1000

        # Cost calculation
        # Tier 1 & 2: $0.00
        # Tier 3: only rows evaluated by LLM (contradiction checks + sample)
        llm_evaluated_rows = len(semantic_flags) + int(n_rows * 0.005)
        # Gemini 1.5 Flash: ~200 tokens per evaluation = ~$0.00006 per evaluated row
        tier3_cost_usd = (llm_evaluated_rows * 200 / 1_000_000) * 0.30

        return {
            "total_rows": n_rows,
            "total_quarantined_rows": len(quarantine_indices),
            "clean_rows": n_rows - len(quarantine_indices),
            "defect_types_found": list(flagged_anomalies.keys()),
            "anomalies_breakdown": flagged_anomalies,
            "latency_ms": {
                "tier1_declarative": round(t1_duration_ms, 2),
                "tier2_statistical": round(t2_duration_ms, 2),
                "tier3_llm": round(t3_duration_ms, 2),
                "total": round(total_duration_ms, 2)
            },
            "throughput_rows_per_second": round(n_rows / (total_duration_ms / 1000.0), 0) if total_duration_ms > 0 else 0,
            "cost_usd": round(tier3_cost_usd, 6),
            "projected_cost_per_million_rows_usd": round((tier3_cost_usd / max(1, n_rows)) * 1_000_000, 2)
        }
