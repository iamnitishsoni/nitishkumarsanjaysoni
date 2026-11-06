"""
Generates a realistic clean NYC 311 Service Requests baseline dataset for benchmarking.
"""
import random
from datetime import datetime, timedelta
import pandas as pd

AGENCIES = ["NYPD", "DSNY", "DOT", "DEP", "DOB"]
BOROUGHS = {
    "MANHATTAN": ["10001", "10002", "10016", "10025"],
    "BROOKLYN": ["11201", "11211", "11215", "11226"],
    "QUEENS": ["11101", "11375", "11432", "11691"],
    "BRONX": ["10451", "10458", "10467", "10475"],
    "STATEN ISLAND": ["10301", "10306", "10312", "10314"]
}

COMPLAINT_MAP = {
    "Noise - Residential": ["Loud Music/Party", "Banging/Pounding", "Loud Talking"],
    "Blocked Driveway": ["No Access", "Partial Access"],
    "Street Condition": ["Pothole", "Cave-in", "Rough Road"],
    "Water System": ["Hydrant Running", "Leak in Street", "No Water"],
    "Illegal Parking": ["Blocked Hydrant", "Double Parked", "Posted Sign Violation"]
}

BASE_RESOLUTIONS = {
    "Closed": "The Department responded to the complaint and determined that police action was not necessary.",
    "Assigned": "The service request has been assigned to the appropriate field office for investigation.",
    "Pending": "The condition has been scheduled for inspection within statutory timeframe."
}


def generate_clean_nyc311_data(n_rows: int = 5000, seed: int = 42) -> pd.DataFrame:
    random.seed(seed)
    base_time = datetime(2023, 6, 1, 8, 0, 0)
    rows = []

    for i in range(1, n_rows + 1):
        boro = random.choice(list(BOROUGHS.keys()))
        zip_code = random.choice(BOROUGHS[boro])
        c_type = random.choice(list(COMPLAINT_MAP.keys()))
        desc = random.choice(COMPLAINT_MAP[c_type])
        agency = random.choice(AGENCIES)

        created_dt = base_time + timedelta(minutes=i * 2 + random.randint(0, 5))
        duration_hrs = random.randint(1, 48)
        closed_dt = created_dt + timedelta(hours=duration_hrs)
        status = "Closed"
        res_desc = BASE_RESOLUTIONS["Closed"]

        # Valid NYC Coordinates
        lat = round(random.uniform(40.55, 40.85), 6)
        lon = round(random.uniform(-74.15, -73.75), 6)

        rows.append({
            "unique_key": 50000000 + i,
            "created_date": created_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "closed_date": closed_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "agency": agency,
            "complaint_type": c_type,
            "descriptor": desc,
            "status": status,
            "incident_zip": zip_code,
            "borough": boro,
            "latitude": lat,
            "longitude": lon,
            "resolution_description": res_desc
        })

    return pd.DataFrame(rows)
