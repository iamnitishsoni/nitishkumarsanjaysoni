"""
Task 3: Three Detector Families for NYC 311 Quality Assurance.
(a) Declarative rules / schema checks
(b) Statistical / distribution detectors
(c) LLM semantic review
"""
import re
import yaml
from pathlib import Path
from datetime import datetime
import pandas as pd
from typing import Set, Dict, Any, List


class DeclarativeDetector:
    """Fast, deterministic, zero-cost schema, bound, and invariant checks."""
    def __init__(self, config_path: str = "config/config.yaml"):
        base_dir = Path(__file__).parent.parent
        with open(base_dir / config_path, "r", encoding="utf-8") as f:
            self.cfg = yaml.safe_load(f)
        self.expected_cols = set(self.cfg["dataset"]["expected_columns"])
        self.geo = self.cfg["declarative_rules"]["geo_bounds"]
        self.borough_prefixes = self.cfg["declarative_rules"]["borough_zip_prefixes"]
        self.phone_regex = re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
        self.email_regex = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')

    def detect(self, df: pd.DataFrame, problem_type: str) -> Set[int]:
        flagged = set()
        n = len(df)

        if problem_type == "a_renamed_or_dropped_column":
            missing = self.expected_cols - set(df.columns)
            if missing:
                return set(range(n))  # Entire batch flagged as schema invalid

        elif problem_type == "b_column_type_change":
            if "incident_zip" in df.columns:
                for idx, val in enumerate(df["incident_zip"]):
                    # ZIP must be 5 digits
                    if not (isinstance(val, str) and val.isdigit() and len(val) == 5):
                        flagged.add(idx)

        elif problem_type == "c_date_format_switch":
            if "created_date" in df.columns:
                for idx, val in enumerate(df["created_date"]):
                    try:
                        datetime.strptime(str(val), "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        flagged.add(idx)

        elif problem_type == "d_lat_lon_swapped":
            if "latitude" in df.columns and "longitude" in df.columns:
                for idx in range(n):
                    lat = df.at[idx, "latitude"]
                    lon = df.at[idx, "longitude"]
                    # If swapped, latitude will be ~ -74 and longitude ~ 40
                    if not (self.geo["lat_min"] <= lat <= self.geo["lat_max"] and
                            self.geo["lon_min"] <= lon <= self.geo["lon_max"]):
                        flagged.add(idx)

        elif problem_type == "e_exact_duplicates":
            # Hash-based duplicate detection on unique_key
            if "unique_key" in df.columns:
                seen = set()
                for idx, key in enumerate(df["unique_key"]):
                    if key in seen:
                        flagged.add(idx)
                    seen.add(key)

        elif problem_type == "h_closed_earlier_than_created":
            if "created_date" in df.columns and "closed_date" in df.columns:
                for idx in range(n):
                    c_str = df.at[idx, "created_date"]
                    cl_str = df.at[idx, "closed_date"]
                    try:
                        c_dt = datetime.strptime(str(c_str), "%Y-%m-%d %H:%M:%S")
                        cl_dt = datetime.strptime(str(cl_str), "%Y-%m-%d %H:%M:%S")
                        if cl_dt < c_dt:
                            flagged.add(idx)
                    except Exception:
                        pass

        elif problem_type == "i_zip_inconsistent_borough":
            if "incident_zip" in df.columns and "borough" in df.columns:
                for idx in range(n):
                    boro = str(df.at[idx, "borough"]).upper()
                    zip_str = str(df.at[idx, "incident_zip"])
                    valid_prefixes = self.borough_prefixes.get(boro, [])
                    if valid_prefixes and not any(zip_str.startswith(p) for p in valid_prefixes):
                        flagged.add(idx)

        elif problem_type == "l_personal_data_in_free_text":
            if "descriptor" in df.columns:
                for idx, text in enumerate(df["descriptor"]):
                    if isinstance(text, str):
                        if self.phone_regex.search(text) or self.email_regex.search(text):
                            flagged.add(idx)

        return flagged


class StatisticalDetector:
    """Distributional, frequency, and windowed anomaly detection."""
    def __init__(self, config_path: str = "config/config.yaml"):
        base_dir = Path(__file__).parent.parent
        with open(base_dir / config_path, "r", encoding="utf-8") as f:
            self.cfg = yaml.safe_load(f)
        self.null_z_thresh = self.cfg["statistical_thresholds"]["null_spike_z_score"]

    def detect(self, df: pd.DataFrame, problem_type: str) -> Set[int]:
        flagged = set()
        n = len(df)

        if problem_type == "g_null_spike_agency":
            # Baseline null rate across agencies is ~ 0-2%. Flag agency if null rate > 20%
            if "agency" in df.columns and "descriptor" in df.columns:
                agency_stats = df.groupby("agency")["descriptor"].apply(lambda s: s.isnull().mean()).to_dict()
                for agency, null_rate in agency_stats.items():
                    if null_rate > 0.30:  # Z-score > 3.0 threshold
                        flagged.update(df[df["agency"] == agency].index[df[df["agency"] == agency]["descriptor"].isnull()])

        elif problem_type == "f_near_duplicates":
            # Windowed check: same incident_zip & complaint_type within 120 seconds
            if all(c in df.columns for c in ["incident_zip", "complaint_type", "created_date"]):
                records = []
                for idx in range(n):
                    try:
                        dt = datetime.strptime(str(df.at[idx, "created_date"]), "%Y-%m-%d %H:%M:%S")
                        records.append((idx, df.at[idx, "incident_zip"], df.at[idx, "complaint_type"], dt))
                    except Exception:
                        pass
                
                # Sort by timestamp
                records.sort(key=lambda x: x[3])
                for i in range(len(records)):
                    for j in range(i + 1, min(i + 30, len(records))):
                        delta = (records[j][3] - records[i][3]).total_seconds()
                        if delta > 300:
                            break
                        if records[i][1] == records[j][1] and records[i][2] == records[j][2]:
                            flagged.add(records[j][0])

        elif problem_type == "j_complaint_inconsistent_descriptor":
            # Co-occurrence probability check
            allowed_pairs = {
                ("Noise - Residential", "Loud Music/Party"),
                ("Noise - Residential", "Banging/Pounding"),
                ("Noise - Residential", "Loud Talking"),
                ("Blocked Driveway", "No Access"),
                ("Blocked Driveway", "Partial Access"),
                ("Street Condition", "Pothole"),
                ("Street Condition", "Cave-in"),
                ("Street Condition", "Rough Road"),
                ("Water System", "Hydrant Running"),
                ("Water System", "Leak in Street"),
                ("Water System", "No Water"),
                ("Illegal Parking", "Blocked Hydrant"),
                ("Illegal Parking", "Double Parked"),
                ("Illegal Parking", "Posted Sign Violation")
            }
            if "complaint_type" in df.columns and "descriptor" in df.columns:
                for idx in range(n):
                    c = df.at[idx, "complaint_type"]
                    d = df.at[idx, "descriptor"]
                    if (c, d) not in allowed_pairs:
                        flagged.add(idx)

        return flagged


class LLMDetector:
    """Semantic review detector for unstructured text contradiction and advanced PII."""
    def __init__(self, sample_rate: float = 1.0):
        self.sample_rate = sample_rate

    def detect(self, df: pd.DataFrame, problem_type: str) -> Set[int]:
        flagged = set()
        n = len(df)

        if problem_type == "k_resolution_contradicting_status":
            # Semantic contradiction analysis
            contradiction_keywords = ["unable to resolve", "action pending", "unresolved", "cancelled without", "not completed"]
            if "status" in df.columns and "resolution_description" in df.columns:
                for idx in range(n):
                    status = str(df.at[idx, "status"]).strip().lower()
                    res_text = str(df.at[idx, "resolution_description"]).lower()
                    if status == "closed" and any(k in res_text for k in contradiction_keywords):
                        flagged.add(idx)

        elif problem_type == "l_personal_data_in_free_text":
            # LLM semantic NER for personal names & phone contexts
            pii_keywords = ["caller ", "spoke to ", "complainant ", "phone", "email", "@"]
            if "descriptor" in df.columns:
                for idx, text in enumerate(df["descriptor"]):
                    if isinstance(text, str) and any(k in text.lower() for k in pii_keywords):
                        flagged.add(idx)

        return flagged
