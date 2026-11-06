"""
Task 2: Corruption Injector for NYC 311 Service Requests.
Injects each of the 12 problem types into clean batches at a controlled rate.
"""
import random
from datetime import datetime, timedelta
import pandas as pd
from typing import Tuple, Set


class CorruptionInjector:
    def __init__(self, seed: int = 42):
        self.seed = seed
        random.seed(seed)

    def inject(self, df: pd.DataFrame, problem_type: str, rate: float = 0.05) -> Tuple[pd.DataFrame, Set[int]]:
        """
        Injects a specific corruption into a copy of df at the given rate.
        Returns: (corrupted_df, set_of_corrupted_indices)
        """
        df = df.copy()
        n_rows = len(df)
        k = max(1, int(n_rows * rate))
        sample_indices = set(random.sample(range(n_rows), k))

        if problem_type == "a_renamed_or_dropped_column":
            # Rename 'incident_zip' -> 'postal_code'
            df.rename(columns={"incident_zip": "postal_code"}, inplace=True)
            return df, set(range(n_rows))

        elif problem_type == "b_column_type_change":
            # Change incident_zip from string '10001' to float string '10001.0' or dirty values
            for idx in sample_indices:
                orig = df.at[idx, "incident_zip"]
                df.at[idx, "incident_zip"] = f"{orig}.0_dirty"
            return df, sample_indices

        elif problem_type == "c_date_format_switch":
            # Partway through batch, swap date format from YYYY-MM-DD to MM/DD/YYYY
            for idx in sample_indices:
                dt_str = df.at[idx, "created_date"]
                try:
                    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                    df.at[idx, "created_date"] = dt.strftime("%m/%d/%Y %I:%M:%S %p")
                except Exception:
                    pass
            return df, sample_indices

        elif problem_type == "d_lat_lon_swapped":
            for idx in sample_indices:
                lat = df.at[idx, "latitude"]
                lon = df.at[idx, "longitude"]
                df.at[idx, "latitude"] = lon
                df.at[idx, "longitude"] = lat
            return df, sample_indices

        elif problem_type == "e_exact_duplicates":
            dup_rows = df.iloc[list(sample_indices)].copy()
            new_df = pd.concat([df, dup_rows], ignore_index=True)
            new_indices = set(range(len(df), len(new_df)))
            return new_df, new_indices

        elif problem_type == "f_near_duplicates":
            dup_rows = df.iloc[list(sample_indices)].copy()
            # Alter timestamp by 60 seconds
            for r_idx in range(len(dup_rows)):
                dt = datetime.strptime(dup_rows.iloc[r_idx]["created_date"], "%Y-%m-%d %H:%M:%S")
                dup_rows.iloc[r_idx, dup_rows.columns.get_loc("created_date")] = (dt + timedelta(seconds=60)).strftime("%Y-%m-%d %H:%M:%S")
                dup_rows.iloc[r_idx, dup_rows.columns.get_loc("unique_key")] = 90000000 + r_idx
            new_df = pd.concat([df, dup_rows], ignore_index=True)
            new_indices = set(range(len(df), len(new_df)))
            return new_df, new_indices

        elif problem_type == "g_null_spike_agency":
            # Injects 85% nulls into descriptor for NYPD agency
            nypd_indices = [i for i in range(n_rows) if df.at[i, "agency"] == "NYPD"]
            spike_indices = set(random.sample(nypd_indices, int(len(nypd_indices) * 0.85)))
            for idx in spike_indices:
                df.at[idx, "descriptor"] = None
            return df, spike_indices

        elif problem_type == "h_closed_earlier_than_created":
            for idx in sample_indices:
                c_dt = datetime.strptime(df.at[idx, "created_date"], "%Y-%m-%d %H:%M:%S")
                # Set closed 5 hours BEFORE created
                df.at[idx, "closed_date"] = (c_dt - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")
            return df, sample_indices

        elif problem_type == "i_zip_inconsistent_borough":
            for idx in sample_indices:
                # Force Brooklyn zip into Manhattan borough
                df.at[idx, "borough"] = "MANHATTAN"
                df.at[idx, "incident_zip"] = "11201"  # Brooklyn zip
            return df, sample_indices

        elif problem_type == "j_complaint_inconsistent_descriptor":
            for idx in sample_indices:
                # Noise Residential complaint paired with Pothole descriptor
                df.at[idx, "complaint_type"] = "Noise - Residential"
                df.at[idx, "descriptor"] = "Pothole on Roadway"
            return df, sample_indices

        elif problem_type == "k_resolution_contradicting_status":
            contradictory_texts = [
                "Unable to resolve. Action pending parts arrival from vendor.",
                "Case unresolved. Officers were unable to gain entry to premises.",
                "Service request cancelled without inspection due to severe weather."
            ]
            for idx in sample_indices:
                df.at[idx, "status"] = "Closed"
                df.at[idx, "resolution_description"] = random.choice(contradictory_texts)
            return df, sample_indices

        elif problem_type == "l_personal_data_in_free_text":
            pii_samples = [
                "Caller John Doe requested callback at 212-555-0199 regarding noise.",
                "Complainant Jane Smith (email: janesmith88@gmail.com) reported illegal parking.",
                "Spoke to property owner Mark at (917) 555-8321 on site."
            ]
            for idx in sample_indices:
                df.at[idx, "descriptor"] = random.choice(pii_samples)
            return df, sample_indices

        else:
            raise ValueError(f"Unknown problem type: {problem_type}")
