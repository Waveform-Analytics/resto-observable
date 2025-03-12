# Load and prepare the restaurant week data

from resto import get_data
import json
import sys
import pandas as pd
from itertools import product
import pytz
from datetime import datetime

edt_timezone = pytz.timezone("US/Eastern")


ignore_emails = [
    "michellejw@gmail.com",
    "michelle@waveformanalytics.com",
    "michelle@bwri.org",
    "jaxblue28@hotmail.com",
    "jessbh3@gmail.com",
    "a.c.keeler1013@gmail.com",
]

all_data = get_data(["users", "visits", "restaurants"])

# Filter out users with NaN created_at (incomplete registration)
all_data["users"] = all_data["users"].dropna(subset=["created_at"])

# Get user_ids associated with the ignored emails
ignored_user_ids = all_data["users"][all_data["users"]["email"].isin(ignore_emails)][
    "user_id"
].tolist()

# Filter out ignored emails from users DataFrame
all_data["users"] = all_data["users"][~all_data["users"]["email"].isin(ignore_emails)]

# Filter out visits associated with ignored users
all_data["visits"] = all_data["visits"][
    ~all_data["visits"]["user_id"].isin(ignored_user_ids)
]

# Filter visits to only include those between March 8-15, 2025 inclusive
# Convert created_at to datetime if it's not already
if not pd.api.types.is_datetime64_any_dtype(all_data["visits"]["created_at"]):
    all_data["visits"]["created_at"] = pd.to_datetime(all_data["visits"]["created_at"])

# Check if timestamps have timezone info
sample_timestamp = (
    all_data["visits"]["created_at"].iloc[0] if len(all_data["visits"]) > 0 else None
)
has_timezone = sample_timestamp is not None and sample_timestamp.tzinfo is not None

# Create timezone-aware or naive timestamps based on the data
if has_timezone:
    start_date = pd.Timestamp("2025-03-08", tz="UTC")
    end_date = pd.Timestamp("2025-03-15 23:59:59", tz="UTC")
else:
    start_date = pd.Timestamp("2025-03-08")
    end_date = pd.Timestamp("2025-03-15 23:59:59")

# Apply date filter
all_data["visits"] = all_data["visits"][
    (all_data["visits"]["created_at"] >= start_date)
    & (all_data["visits"]["created_at"] <= end_date)
]

# Calculate some stats
visited_restaurants_count = all_data["visits"]["restaurant_id"].nunique()

# Convert datetime columns to strings for JSON serialization
for df_name in all_data:
    for col in all_data[df_name].columns:
        if pd.api.types.is_datetime64_any_dtype(all_data[df_name][col]):
            all_data[df_name][col] = all_data[df_name][col].astype(str)

# Create a table of visits that includes the restaurant name and the day of the week
# and the hour of day, where the id's are not named the same in each table: restaurants
# table uses "id", and visits table uses "restaurant_id"
all_data["visits"] = all_data["visits"].merge(
    all_data["restaurants"][["id", "name"]],
    left_on="restaurant_id",
    right_on="id",
    suffixes=("_visits", "_restaurants"),
)

# Adjust time zone in visits and users tables
all_data["visits"]["created_at"] = pd.to_datetime(all_data["visits"]["created_at"])
all_data["visits"]["created_at"] = all_data["visits"]["created_at"].dt.tz_convert(
    edt_timezone
)
all_data["users"]["created_at"] = pd.to_datetime(all_data["users"]["created_at"])
all_data["users"]["created_at"] = all_data["users"]["created_at"].dt.tz_convert(
    edt_timezone
)

# Add day of week and hour of day
all_data["visits"]["day_of_week"] = all_data["visits"]["created_at"].dt.dayofweek
all_data["visits"]["hour_of_day"] = all_data["visits"]["created_at"].dt.hour
all_data["visits"]["day_of_month"] = all_data["visits"]["created_at"].dt.day

# Count occurrences of each day/hour combination
actual_counts = (
    all_data["visits"]
    .groupby(["day_of_month", "hour_of_day"])
    .size()
    .reset_index(name="visit_count")
)

# Create complete grid with all possible combinations
days = range(8, 16)  # 8 to 15 inclusive
hours = range(24)  # 0 to 23
grid = pd.DataFrame(product(days, hours), columns=["day_of_month", "hour_of_day"])

# Merge actual counts with the complete grid
complete_counts = grid.merge(
    actual_counts, on=["day_of_month", "hour_of_day"], how="left"
)

# Fill NaN values with zeros and convert to integer
complete_counts["visit_count"] = complete_counts["visit_count"].fillna(0).astype(int)

# Add counts dataframes to all_data
all_data["complete_counts"] = complete_counts # with zeros
all_data["actual_counts"] = actual_counts # only include non-zero rows


def convert_timestamps(obj):
    if isinstance(obj, (pd.Timestamp, datetime)):
        return obj.isoformat()
    return obj


# Convert each DataFrame to records format (list of dictionaries)
# Handle NaN values by replacing them with None before conversion
json_ready_data = {
    key: df.where(df.notna(), None).to_dict(orient="records")
    for key, df in all_data.items()
}

# Add statistics to the JSON data
json_ready_data["stats"] = {
    "visitedRestaurants": int(visited_restaurants_count),
    "totalCheckIns": int(len(all_data["visits"])),
}

# Convert dictionary to JSON string with indentation for readability
json_data = json.dumps(json_ready_data, indent=4, default=convert_timestamps)

# Print JSON to stdout (required for Observable Framework loaders)
sys.stdout.write(json_data)
