"""
Unit and Integration Test Suite for Project B (Data-Quality Checks).
"""
import pytest
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.sample_data import generate_clean_nyc311_data
from src.injector import CorruptionInjector
from src.detectors import DeclarativeDetector, StatisticalDetector, LLMDetector
from src.hybrid_pipeline import HybridDataQualityPipeline


@pytest.fixture(scope="module")
def clean_batch():
    return generate_clean_nyc311_data(n_rows=500, seed=123)


@pytest.fixture(scope="module")
def injector():
    return CorruptionInjector(seed=123)


def test_declarative_detects_swapped_lat_lon(clean_batch, injector):
    detector = DeclarativeDetector()
    corrupted_df, injected = injector.inject(clean_batch, "d_lat_lon_swapped", rate=0.1)
    flagged = detector.detect(corrupted_df, "d_lat_lon_swapped")
    assert len(flagged) > 0
    assert flagged == injected


def test_declarative_detects_closed_before_created(clean_batch, injector):
    detector = DeclarativeDetector()
    corrupted_df, injected = injector.inject(clean_batch, "h_closed_earlier_than_created", rate=0.1)
    flagged = detector.detect(corrupted_df, "h_closed_earlier_than_created")
    assert len(flagged) > 0
    assert flagged == injected


def test_statistical_detects_null_spike(clean_batch, injector):
    detector = StatisticalDetector()
    corrupted_df, injected = injector.inject(clean_batch, "g_null_spike_agency", rate=0.1)
    flagged = detector.detect(corrupted_df, "g_null_spike_agency")
    assert len(flagged) > 0
    assert len(flagged.intersection(injected)) > 0


def test_llm_detects_status_contradiction(clean_batch, injector):
    detector = LLMDetector()
    corrupted_df, injected = injector.inject(clean_batch, "k_resolution_contradicting_status", rate=0.1)
    flagged = detector.detect(corrupted_df, "k_resolution_contradicting_status")
    assert len(flagged) > 0
    assert flagged == injected


def test_hybrid_pipeline_run(clean_batch, injector):
    pipeline = HybridDataQualityPipeline()
    corrupted_df, _ = injector.inject(clean_batch, "b_column_type_change", rate=0.05)
    summary = pipeline.run_pipeline(corrupted_df)
    assert summary["total_rows"] == len(clean_batch)
    assert summary["total_quarantined_rows"] > 0
    assert "b_column_type_change" in summary["defect_types_found"]
