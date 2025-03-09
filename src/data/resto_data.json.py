# Load and prepare the restaurant week data

from resto import get_data
import json
import sys

all_data = get_data(['users', 'visits', 'restaurants'])

# Convert each DataFrame to records format (list of dictionaries)
# Handle NaN values by replacing them with None before conversion
json_ready_data = {
    key: df.where(df.notna(), None).to_dict(orient='records')
    for key, df in all_data.items()
}

# Convert dictionary to JSON string with indentation for readability
json_data = json.dumps(json_ready_data, indent=4)

# Print JSON to stdout (required for Observable Framework loaders)
sys.stdout.write(json_data)